import asyncio
import aiohttp
import json
import os
import time
import subprocess
from dotenv import load_dotenv

load_dotenv()

# Ordem de prioridade das APIs
API_ORDER = ["openai", "llama", "grok", "deepseek"]

TEST_MESSAGE = ""  # Deixe vazio para fluxo normal ou preencha para teste

# Configuração do Ollama (ajuste conforme seu servidor)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")

# Lista de comandos suportados
COMMANDS = {
    "horas": {
        "description": "Verificar o horário",
        "os_command": "echo 'Ok google. Quantas horas'",
        "default_output": "Horário não disponível no momento."
    },
    "data": {
        "description": "Verificar a data",
        "os_command": "date /t" if os.name == 'nt' else "date +%d/%m/%Y",
        "default_output": "Data não disponível no momento."
    },
    "tempo": {
        "description": "Verificar o clima",
        "os_command": "echo 'cmd ok'",  # Placeholder, substitua por comando real se disponível
        "default_output": "Informação climática não disponível no momento."
    }
}

async def think(state):
    """Processa a mensagem com comandos locais ou APIs, seguindo a ordem de prioridade."""
    ultima_mensagem = None

    async def process_with_openai(message):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Erro: chave da OpenAI não encontrada no .env")
            return "Erro: configure a chave da OpenAI"
        
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}".strip()}
        payload = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": message}]}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"Erro na API OpenAI: {response.status} - {error_text}")
                        return f"Erro API {response.status}: {error_text}"
                    result = await response.json()
                    return result.get("choices", [{}])[0].get("message", {}).get("content", "Erro: resposta inválida")
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                print(f"Erro de conexão com a API OpenAI: {e}")
                return None
            except json.JSONDecodeError:
                print("Erro ao decodificar resposta da API OpenAI")
                return None
            except Exception as e:
                print(f"Erro inesperado na API OpenAI: {e}")
                return None

    async def process_with_grok(message):
        api_key = os.getenv("GROK_API_KEY")
        if not api_key:
            print("Erro: chave da Grok não encontrada no .env")
            return "Erro: configure a chave da Grok"
        
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}".strip()}
        payload = {"model": "grok", "messages": [{"role": "user", "content": message}]}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    "https://api.xai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"Erro na API Grok: {response.status} - {error_text}")
                        return f"Erro API {response.status}: {error_text}"
                    result = await response.json()
                    return result.get("choices", [{}])[0].get("message", {}).get("content", "Erro: resposta inválida")
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                print(f"Erro de conexão com a API Grok: {e}")
                return None
            except json.JSONDecodeError:
                print("Erro ao decodificar resposta da API Grok")
                return None
            except Exception as e:
                print(f"Erro inesperado na API Grok: {e}")
                return None

    async def process_with_deepseek(message):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("Erro: chave da Deepseek não encontrada no .env")
            return "Erro: configure a chave da Deepseek"
        
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}".strip()}
        payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": message}]}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"Erro na API Deepseek: {response.status} - {error_text}")
                        return f"Erro API {response.status}: {error_text}"
                    result = await response.json()
                    return result.get("choices", [{}])[0].get("message", {}).get("content", "Erro: resposta inválida")
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                print(f"Erro de conexão com a API Deepseek: {e}")
                return None
            except json.JSONDecodeError:
                print("Erro ao decodificar resposta da API Deepseek")
                return None
            except Exception as e:
                print(f"Erro inesperado na API Deepseek: {e}")
                return None

    async def process_with_llama(message):
        headers = {"Content-Type": "application/json"}
        payload = {"model": OLLAMA_MODEL, "prompt": message, "stream": False}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{OLLAMA_HOST}/api/generate",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"Erro na API Ollama: {response.status} - {error_text}")
                        return f"Erro API {response.status}: {error_text}"
                    result = await response.json()
                    return result.get("response", "Erro: resposta inválida")
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                print(f"Erro de conexão com o Ollama: {e}")
                return None
            except json.JSONDecodeError:
                print("Erro ao decodificar resposta do Ollama")
                return None
            except Exception as e:
                print(f"Erro inesperado no Ollama: {e}")
                return None

    async def process_command(message):
        """Verifica e executa comandos locais antes de enviar às APIs."""
        message_lower = message.lower().strip()
        print(f"Debug: verificando comando em '{message_lower}'")
        for command_key, command_info in COMMANDS.items():
            if command_key in message_lower.split():  # Verifica palavras individuais
                print(f"Think: comando '{command_key}' detectado, executando: {command_info['os_command']}")
                try:
                    result = subprocess.check_output(command_info["os_command"], shell=True, text=True, stderr=subprocess.STDOUT)
                    print(f"Debug: saída do comando '{command_key}': {result.strip()}")
                    return result.strip()
                except subprocess.CalledProcessError as e:
                    print(f"Erro ao executar comando '{command_key}': {e.output}")
                    return command_info["default_output"]
                except Exception as e:
                    print(f"Erro inesperado ao executar comando '{command_key}': {e}")
                    return command_info["default_output"]
        print("Debug: nenhum comando correspondente encontrado")
        return None

    async def process_message(message):
        """Tenta processar a mensagem com comandos locais ou APIs."""
        command_result = await process_command(message)
        if command_result is not None:
            return command_result

        for api in API_ORDER:
            if api == "openai":
                response = await process_with_openai(message)
            elif api == "grok":
                response = await process_with_grok(message)
            elif api == "deepseek":
                response = await process_with_deepseek(message)
            elif api == "llama":
                response = await process_with_llama(message)
            else:
                continue

            if response is not None:
                return response

        return "Erro: todas as APIs falharam"

    # Teste de mensagem fixa
    if TEST_MESSAGE:
        print(f"Think: executando teste de processamento: {TEST_MESSAGE}")
        state["thinking"] = True
        state["response"] = await process_message(TEST_MESSAGE)
        state["thinking"] = False
        state["last_speech_time"] = time.time()
        print(f"Think: resposta do teste: {state['response']}")
        return

    # Loop principal para processar mensagens do estado
    while True:
        print(f"Debug: estado atual - message: {state['message']}, thinking: {state['thinking']}, ultima_mensagem: {ultima_mensagem}")
        if (state["message"] and 
            state["message"] != "Null" and 
            state["message"] != ultima_mensagem and 
            not state["thinking"]):
            
            print(f"Think: processando: {state['message']}")
            state["thinking"] = True

            if state.get("interrupt"):
                print("Think: interrompido por 'para para para'")
                state["thinking"] = False
                await asyncio.sleep(0.05)
                continue

            response_text = await process_message(state["message"])
            state["response"] = response_text
            ultima_mensagem = state["message"]
            state["message"] = None
            state["last_speech_time"] = time.time()
            print(f"Think: resposta: {response_text}")

            state["thinking"] = False
        else:
            print("Debug: think não ativado - verificando condições")

        await asyncio.sleep(0.05)

# Função para teste isolado
async def test_think():
    state = {
        "speaking": False,
        "thinking": False,
        "interrupt": False,
        "message": None,
        "response": None,
        "last_speech_time": time.time()
    }
    await think(state)

if __name__ == "__main__":
    asyncio.run(test_think())