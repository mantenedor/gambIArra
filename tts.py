import asyncio
import websockets
import json
from gtts import gTTS
import os

async def receive_text(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        response_text = data.get("response", "")
        print(f"🗣️ Falando: {response_text}")
        
        # Converte para áudio e salva no diretório /mnt/RAM
        tts = gTTS(response_text, lang='pt')
        tts.save("/mnt/RAM/response.mp3")
        os.system("mpg321 /mnt/RAM/response.mp3")  # Executa o áudio

async def main():
    async with websockets.serve(receive_text, "localhost", 8766):
        print("🔊 Servidor TTS iniciado na porta 8766")
        await asyncio.Future()

asyncio.run(main())

