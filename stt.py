import asyncio
import websockets
import json
import speech_recognition as sr
import os
import glob

# Diretório temporário na RAM
TEMP_DIR = "/mnt/RAM"
os.makedirs(TEMP_DIR, exist_ok=True)

# Número máximo de arquivos temporários antes da rotação
MAX_TEMP_FILES = 5

def cleanup_temp_files():
    """Mantém apenas os últimos MAX_TEMP_FILES arquivos na RAM, removendo os mais antigos."""
    temp_files = sorted(glob.glob(os.path.join(TEMP_DIR, "*.wav")), key=os.path.getctime)
    
    # Se o número de arquivos exceder o limite, remove os mais antigos
    while len(temp_files) > MAX_TEMP_FILES:
        os.remove(temp_files.pop(0))

async def send_audio(sentence):
    try:
        async with websockets.connect("ws://localhost:8765") as websocket:
            print(f"🎤 Enviando comando: {sentence}")
            await websocket.send(json.dumps({"command": sentence}))

    except websockets.exceptions.ConnectionClosedError:
        print("⚠️ Conexão com o servidor WebSocket fechada. Tentando reconectar...")
        await asyncio.sleep(2)
        await send_audio(sentence)
    except Exception as e:
        print(f"⚠️ Erro ao enviar dados: {e}")
        await asyncio.sleep(2)
        await send_audio(sentence)

def recognize_speech():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("🎤 Diga algo...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("🔊 Reconhecendo...")

        # Criar um arquivo temporário numerado para rotação
        temp_audio_path = os.path.join(TEMP_DIR, f"audio_{len(glob.glob(TEMP_DIR + '/*.wav')) % MAX_TEMP_FILES}.wav")

        # Salvar áudio no arquivo temporário
        with open(temp_audio_path, "wb") as f:
            f.write(audio.get_wav_data())

        sentence = recognizer.recognize_google(audio, language="pt-BR")
        print(f"📝 Reconhecido: {sentence}")

        # Realiza a limpeza dos arquivos antigos
        cleanup_temp_files()

        # Envia o áudio reconhecido para o servidor WebSocket
        asyncio.run(send_audio(sentence))

    except sr.UnknownValueError:
        print("😞 Não consegui entender o que você disse.")
    except sr.RequestError as e:
        print(f"⚠️ Erro no serviço de reconhecimento de fala: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    while True:
        recognize_speech()

