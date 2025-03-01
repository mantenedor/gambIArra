import asyncio
import websockets
import json
import os
import pyaudio
import vosk
import time
import unicodedata

MODEL_PATH = "./models/vosk-model-small-pt-0.3"
WEBSOCKET_URI = "ws://localhost:8765"
INACTIVITY_TIMEOUT = 10.0
UNLOCK_KEYWORDS = ["oxe", "desbloquear", "acorda", "reativar", "e aí 4", "e aí quatro"]
STOP_KEYWORD = "para para para"
USE_WEBSOCKET = False

# Flag global para sinalizar encerramento
should_stop = False

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Modelo não encontrado em {MODEL_PATH}")

def normalize_text(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if unicodedata.category(c) != 'Mn')

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
        normalized_stop_keyword = normalize_text(STOP_KEYWORD)
        
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
                        
                        if (time.time() - state["last_speech_time"] > INACTIVITY_TIMEOUT) and not state["speaking"] and not state["thinking"] and not state["response"]:
                            print(f"🕒 Inativo por mais de {INACTIVITY_TIMEOUT}s. Aguardando {UNLOCK_KEYWORDS}...")
                            if any(kw in normalized_sentence for kw in normalized_unlock_keywords):
                                detected = next(kw for kw in UNLOCK_KEYWORDS if normalize_text(kw) in normalized_sentence)
                                print(f"✅ '{detected}' detectado. Retomando.")
                                state["last_speech_time"] = time.time()
                                state["message"] = None
                                state["response"] = None
                                state["interrupt"] = False
                                state["speaking"] = False
                                state["thinking"] = False
                            continue
                        
                        if not state["thinking"] and (time.time() - state["last_speech_time"] <= INACTIVITY_TIMEOUT):
                            state["last_speech_time"] = time.time()
                            state["message"] = sentence
                            print(f"Listen: capturado e definido em state['message']: {sentence}")
                            await send_audio(sentence)
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