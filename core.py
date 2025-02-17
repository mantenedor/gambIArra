import asyncio
import websockets
import json
import time
import os
import subprocess
import requests
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Carrega o dicionário COMMANDS do arquivo JSON
with open('commands.json', 'r') as commands_file:
    COMMANDS = json.load(commands_file)

async def send_to_tts(response):
    """Função para enviar resposta ao servidor TTS via WebSocket"""
    try:
        async with websockets.connect("ws://localhost:8766") as tts_ws:
            await tts_ws.send(json.dumps({"response": response}))
    except websockets.exceptions.ConnectionClosedError:
        await asyncio.sleep(2)
    except Exception as e:
        print(f"Erro ao enviar ao TTS: {e}")

def score_command(input_command, commands):
    """Calcula um score de similaridade para o comando de entrada contra os comandos conhecidos."""
    import difflib
    scores = {}
    for command in commands:
        score = difflib.SequenceMatcher(None, input_command, command).ratio() * 100
        scores[command] = score
    matched_command = max(scores, key=scores.get)
    return scores[matched_command], matched_command

async def receive_confirmation(websocket):
    """Recebe a confirmação do usuário via WebSocket."""
    while True:
        try:
            confirmation = await websocket.recv()
            confirmation = confirmation.lower()
            if confirmation in ["sim", "não", "nao"]:
                return confirmation
            else:
                await send_to_tts("Por favor, responda com 'sim' ou 'não'.")
        except websockets.exceptions.ConnectionClosedError:
            await asyncio.sleep(2)

def chat_with_openai(prompt, model="gpt-3.5-turbo"):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Chave de API não encontrada.")
        return None

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Levanta um erro em caso de status != 200
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"Erro ao chamar a API do ChatGPT: {e}")
        return None

async def process_command(websocket, path):
    """Processa os comandos recebidos via WebSocket"""
    try:
        async for message in websocket:
            data = json.loads(message)
            command = data.get("command", "").lower()
            score, matched_command = score_command(command, list(COMMANDS.keys()))
            
            if score > 90:
                # Comando reconhecido com alta certeza, executa diretamente
                task = COMMANDS[matched_command]
                os_command = task["os_command"]
                try:
                    result = subprocess.run(os_command, shell=True, capture_output=True, text=True)
                    response = result.stdout.strip() if result.returncode == 0 else f"Erro ao executar o comando: {result.stderr.strip()}"
                except Exception as e:
                    response = "O comando foi cancelado devido a um erro."
            
            elif 60 < score <= 90:
                # Comando com média certeza, solicita confirmação
                task = COMMANDS[matched_command]
                confirmation_message = f"Você quis dizer '{matched_command}'?"
                await send_to_tts(confirmation_message)
                
                confirmation = await receive_confirmation(websocket)
                
                if confirmation == "sim":
                    os_command = task["os_command"]
                    try:
                        result = subprocess.run(os_command, shell=True, capture_output=True, text=True)
                        response = result.stdout.strip() if result.returncode == 0 else f"Erro ao executar o comando: {result.stderr.strip()}"
                    except Exception as e:
                        response = "O comando foi cancelado devido a um erro."
                else:
                    response = "Comando cancelado."
            else:
                # Não é um comando reconhecido, encaminha para IA
                response = chat_with_openai(command) or "Não consegui entender ou obter uma resposta para isso."

            print(f"✅ Input recebido: {command} -> {response}")
            await send_to_tts(response)
    except Exception as e:
        print(f"⚠️ Erro ao processar o comando: {e}. Continuando...")
        # Aqui você poderia optar por enviar uma mensagem via TTS sobre o erro, se achar necessário.

async def main():
    """Inicia o servidor WebSocket"""
    while True:
        try:
            async with websockets.serve(process_command, "localhost", 8765):
                print("🧠 Servidor WebSocket iniciado na porta 8765")
                await asyncio.Future()  # Mantém o servidor rodando
        except Exception as e:
            print(f"⚠️ Erro ao iniciar o servidor WebSocket: {e}. Tentando reiniciar em 5 segundos.")
            await asyncio.sleep(5)

# Inicia o servidor WebSocket
asyncio.run(main())
