import asyncio
import websockets
import json
import os
import pyaudio
import vosk
import time
import unicodedata
import pygame
import sys

# Inicializa o pygame mixer para tocar sons
pygame.mixer.init()

WEBSOCKET_URI = "ws://localhost:8765"
USE_WEBSOCKET = False
COMMANDS_FILE = "commands.json"

# Flag global para sinalizar encerramento
should_stop = False

# Define o diretório base dependendo do ambiente
if getattr(sys, 'frozen', False):
    # Se for um executável compilado (PyInstaller)
    BASE_DIR = sys._MEIPASS
else:
    # Se for um script Python sendo executado diretamente
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Normaliza o BASE_DIR para garantir barras corretas
BASE_DIR = os.path.normpath(BASE_DIR)
print(f"Listen: BASE_DIR calculado como: {BASE_DIR}")
print(f"Listen: Diretório de trabalho atual: {os.getcwd()}")

# Carrega a configuração a partir do arquivo JSON
def load_config():
    commands_path = os.path.normpath(os.path.join(BASE_DIR, COMMANDS_FILE))
    print(f"Listen: Tentando carregar config de: {commands_path}")
    try:
        if os.path.exists(commands_path):
            with open(commands_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"Listen: Configuração carregada do arquivo {commands_path}: {json.dumps(config, indent=2)}")
            return config["listen_config"]
        else:
            raise FileNotFoundError(f"⚠️ Arquivo {commands_path} não encontrado.")
    except Exception as e:
        print(f"❌ Erro ao carregar configuração de {commands_path}: {e}.")
        raise

# Carrega as configurações ao iniciar
CONFIG = load_config()
INACTIVITY_TIMEOUT = CONFIG["inactivity_timeout"]
UNLOCK_KEYWORDS = CONFIG["unlock_keywords"]
LOCK_KEYWORDS = CONFIG["lock_keywords"]
STOP_KEYWORD = CONFIG["stop_keyword"]
LOCK_SOUND = os.path.normpath(os.path.join(BASE_DIR, CONFIG["lock_sound"]))
UNLOCK_SOUND = os.path.normpath(os.path.join(BASE_DIR, CONFIG["unlock_sound"]))
MODEL_PATH = os.path.normpath(os.path.join(BASE_DIR, CONFIG["model_path"]))  # Obtido do commands.json

print(f"Listen: MODEL_PATH calculado como: {MODEL_PATH}")
print(f"Listen: LOCK_SOUND calculado como: {LOCK_SOUND}")
print(f"Listen: UNLOCK_SOUND calculado como: {UNLOCK_SOUND}")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Modelo não encontrado em {MODEL_PATH}")

# Verifica se os arquivos de som existem
if not os.path.exists(LOCK_SOUND):
    print(f"⚠️ Arquivo de som de bloqueio '{LOCK_SOUND}' não encontrado.")
if not os.path.exists(UNLOCK_SOUND):
    print(f"⚠️ Arquivo de som de desbloqueio '{UNLOCK_SOUND}' não encontrado.")

def normalize_text(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if unicodedata.category(c) != 'Mn')

async def play_sound(sound_file):
    """Toca um arquivo de som usando pygame."""
    try:
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
        print(f"🎵 Som '{sound_file}' reproduzido com sucesso")
    except Exception as e:
        print(f"❌ Erro ao reproduzir som '{sound_file}': {e}")

async def send_audio(sentence):
    if not USE_WEBSOCKET:
        print("🎤 WebSocket desativado. Comando não enviado.")
        return True
    
    max_retries = 3
    retry_delay = 2
    for attempt in range(max_retries):
        try:
            async with websockets.connect(WEBSOCKET_URI) as websocket:
                print(f"🎤 Enviando comando: {sentence}")
                await websocket.send(json.dumps({"command": sentence}))
                return True
        except (websockets.exceptions.ConnectionClosedError, Exception) as e:
            print(f"⚠️ Erro ao enviar dados (tentativa {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                print("❌ Falha após todas as tentativas. Prosseguindo sem WebSocket.")
                return False

async def recognize_speech(state):
    global should_stop
    print("🔄 Carregando modelo Vosk...")
    model = vosk.Model(MODEL_PATH)
    recognizer = vosk.KaldiRecognizer(model, 16000)
    
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
    stream.start_stream()
    
    print("🎤 Escutando em tempo real...")
    
    try:
        normalized_unlock_keywords = [normalize_text(kw) for kw in UNLOCK_KEYWORDS]
        normalized_lock_keywords = [normalize_text(kw) for kw in LOCK_KEYWORDS]
        normalized_stop_keyword = normalize_text(STOP_KEYWORD)
        was_inactive = False
        
        while not should_stop:
            try:
                data = stream.read(4096, exception_on_overflow=False)
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    sentence = result.get("text", "")
                    if sentence:
                        print(f"📝 Reconhecido: {sentence}")
                        normalized_sentence = normalize_text(sentence)
                        
                        if normalized_stop_keyword in normalized_sentence:
                            print(f"Listen: '{STOP_KEYWORD}' detectado, interrompendo...")
                            state["interrupt"] = True
                            state["message"] = None
                            state["response"] = None
                            await asyncio.sleep(0.1)
                            state["interrupt"] = False
                            state["listening"] = False
                            continue
                        
                        if any(kw in normalized_sentence for kw in normalized_lock_keywords):
                            detected = next(kw for kw in LOCK_KEYWORDS if normalize_text(kw) in normalized_sentence)
                            print(f"🔒 '{detected}' detectado. Bloqueando sistema.")
                            if os.path.exists(LOCK_SOUND):
                                await play_sound(LOCK_SOUND)
                            state["last_speech_time"] = time.time() - INACTIVITY_TIMEOUT - 1
                            was_inactive = True
                            continue
                        
                        if (time.time() - state["last_speech_time"] > INACTIVITY_TIMEOUT) and not state["speaking"] and not state["thinking"] and not state["response"]:
                            if not was_inactive:
                                print(f"🕒 Inativo por mais de {INACTIVITY_TIMEOUT}s. Aguardando {UNLOCK_KEYWORDS}...")
                                if os.path.exists(LOCK_SOUND):
                                    await play_sound(LOCK_SOUND)
                                was_inactive = True
                            
                            if any(kw in normalized_sentence for kw in normalized_unlock_keywords):
                                detected = next(kw for kw in UNLOCK_KEYWORDS if normalize_text(kw) in normalized_sentence)
                                print(f"✅ '{detected}' detectado. Retomando.")
                                if os.path.exists(UNLOCK_SOUND):
                                    await play_sound(UNLOCK_SOUND)
                                state["last_speech_time"] = time.time()
                                state["message"] = None
                                state["response"] = None
                                state["interrupt"] = False
                                state["speaking"] = False
                                state["thinking"] = False
                                was_inactive = False
                            continue
                        
                        if not state["thinking"] and (time.time() - state["last_speech_time"] <= INACTIVITY_TIMEOUT):
                            state["last_speech_time"] = time.time()
                            state["message"] = sentence
                            print(f"Listen: capturado e definido em state['message']: {sentence}")
                            await send_audio(sentence)
                            was_inactive = False
                else:
                    if (time.time() - state["last_speech_time"] > INACTIVITY_TIMEOUT) and not state["speaking"] and not state["thinking"] and not state["response"]:
                        if not was_inactive:
                            print(f"🕒 Inativo por mais de {INACTIVITY_TIMEOUT}s. Aguardando {UNLOCK_KEYWORDS}...")
                            if os.path.exists(LOCK_SOUND):
                                await play_sound(LOCK_SOUND)
                            was_inactive = True
                    else:
                        print("Listen: aguardando áudio...")
                await asyncio.sleep(0.01)
            except asyncio.CancelledError:
                print("Listen: tarefa cancelada")
                break
    except Exception as e:
        print(f"❌ Erro no reconhecimento: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Listen: stream de áudio finalizado")

async def listen(state):
    state["listening"] = True
    await recognize_speech(state)