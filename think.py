import asyncio
import aiohttp
import json
import os
import time
import subprocess
from dotenv import load_dotenv

load_dotenv()

API_ORDER = ["openai", "llama", "grok", "deepseek"]
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")

COMMANDS = {
    "horas": {"description": "Verificar o horário", "os_command": "time /t" if os.name == 'nt' else "date +%H:%M", "default_output": "Horário não disponível."},
    "data": {"description": "Verificar a data", "os_command": "date /t" if os.name == 'nt' else "date +%d/%m/%Y", "default_output": "Data não disponível."},
    "tempo": {"description": "Verificar o clima", "os_command": None, "default_output": "Clima não disponível."}
}

# Flag global para sinalizar encerramento
should_stop = False

async def process_command(message):
    message_lower = message.lower().strip()
    for cmd, info in COMMANDS.items():
        if cmd in message_lower.split():
            print(f"Think: comando '{cmd}' detectado.")
            if info["os_command"]:
                try:
                    result = subprocess.check_output(info["os_command"], shell=True, text=True)
                    return result.strip()
                except Exception as e:
                    print(f"Erro no comando '{cmd}': {e}")
                    return info["default_output"]
            return info["default_output"]
    return None

async def process_with_api(api, message):
    async with aiohttp.ClientSession() as session:
        try:
            if api == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    print("Think: chave OpenAI não encontrada")
                    return None
                headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
                payload = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": message}]}
                url = "https://api.openai.com/v1/chat/completions"
            elif api == "grok":
                api_key = os.getenv("GROK_API_KEY")
                if not api_key:
                    print("Think: chave Grok não encontrada")
                    return None
                headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
                payload = {"model": "grok", "messages": [{"role": "user", "content": message}]}
                url = "https://api.xai.com/v1/chat/completions"
            elif api == "deepseek":
                api_key = os.getenv("DEEPSEEK_API_KEY")
                if not api_key:
                    print("Think: chave Deepseek não encontrada")
                    return None
                headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
                payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": message}]}
                url = "https://api.deepseek.com/v1/chat/completions"
            elif api == "llama":
                headers = {"Content-Type": "application/json"}
                payload = {"model": OLLAMA_MODEL, "prompt": message, "stream": False}
                url = f"{OLLAMA_HOST}/api/generate"
            
            print(f"Think: tentando API {api} com mensagem: {message}")
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    print(f"Erro na API {api}: {resp.status} - {error_text}")
                    return None
                result = await resp.json()
                print(f"Think: resposta completa da API {api}: {json.dumps(result, indent=2)}")
                response = result.get("response") if api == "llama" else result.get("choices", [{}])[0].get("message", {}).get("content")
                print(f"Think: resposta extraída de {api}: {response}")
                return response
        except Exception as e:
            print(f"Erro na API {api}: {e}")
            return None

async def think(state):
    global should_stop
    ultima_mensagem = None
    try:
        while not should_stop:
            try:
                if state["message"] and state["message"] != ultima_mensagem and not state["thinking"]:
                    print(f"Think: processando nova mensagem: {state['message']}")
                    state["thinking"] = True
                    
                    if state.get("interrupt"):
                        print("Think: interrompido.")
                        state["thinking"] = False
                        await asyncio.sleep(0.05)
                        continue
                    
                    response = await process_command(state["message"])
                    if response is None:
                        print(f"Think: mensagem '{state['message']}' não é comando local, encaminhando para APIs")
                        for api in API_ORDER:
                            response = await process_with_api(api, state['message'])
                            if response:
                                break
                        if not response:
                            response = "Erro: todas as APIs falharam"
                    else:
                        print(f"Think: resposta de comando local: {response}")
                    
                    state["response"] = response
                    ultima_mensagem = state["message"]
                    state["message"] = None
                    state["last_speech_time"] = time.time()
                    print(f"Think: resposta definida em state['response']: {response}")
                    state["thinking"] = False
                else:
                    print(f"Think: aguardando - state: {dict(state)}")
                await asyncio.sleep(0.05)
            except asyncio.CancelledError:
                print("Think: tarefa cancelada")
                break
    except Exception as e:
        print(f"❌ Erro geral no think: {e}")