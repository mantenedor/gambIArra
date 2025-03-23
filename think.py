import asyncio
import aiohttp
import json
from pathlib import Path
import time
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import sys
import spacy

load_dotenv()

COMMANDS_FILE = "commands.json"
MEMORY_FILE = "memory.json"
LOG_DIR = Path(__file__).parent if not getattr(sys, 'frozen', False) else Path(sys.executable).parent

should_stop = False
nlp = spacy.load("pt_core_news_sm")  # Modelo em português

BASE_DIR = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent

# Carrega memória
def load_memory():
    memory_path = BASE_DIR / MEMORY_FILE
    if memory_path.exists():
        with memory_path.open('r', encoding='utf-8') as f:
            return json.load(f)
    default_memory = {"user_id": "default_user", "entities": {"nomes": {}, "lugares": {}, "pessoas": {}}}
    save_memory(default_memory)
    return default_memory

def save_memory(memory):
    memory_path = BASE_DIR / MEMORY_FILE
    with memory_path.open('w', encoding='utf-8') as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

# Corrige texto com spaCy (simplificado)
def correct_text(text):
    doc = nlp(text)
    corrected = " ".join(token.text for token in doc)
    return corrected

# Extrai entidades (corrigida)
def extract_entities(text):
    doc = nlp(text)
    entities = {"nomes": {}, "lugares": {}, "pessoas": {}}
    text_lower = text.lower()

    # Detecta entidades com spaCy
    for ent in doc.ents:
        if ent.label_ == "PER":
            entities["pessoas"][ent.text] = ent.text
        elif ent.label_ == "LOC":
            entities["lugares"][ent.text] = ent.text

    # Regras manuais ajustadas com verificações
    if "se chama" in text_lower:
        parts = text_lower.split("se chama")
        if len(parts) > 1 and parts[1].strip():
            name = parts[1].strip().split()[0]  # Pega a primeira palavra após "se chama"
            if "gato" in text_lower:
                entities["nomes"]["gato"] = name
            elif "lugar" in text_lower:
                entities["lugares"]["meu_lugar"] = name
    elif "nome do meu gato" in text_lower and "é" in text_lower:
        parts = text_lower.split("é")
        if len(parts) > 1 and parts[1].strip():
            name = parts[1].strip().split()[0]  # Pega a primeira palavra após "é"
            entities["nomes"]["gato"] = name
    elif "nome do meu lugar" in text_lower and "é" in text_lower:
        parts = text_lower.split("é")
        if len(parts) > 1 and parts[1].strip():
            name = parts[1].strip().split()[0]  # Pega a primeira palavra após "é"
            entities["lugares"]["meu_lugar"] = name
    elif "na verdade eu me refiro ao nome do meu gato" in text_lower:
        history = load_conversation_history()
        if history and len(history) > 1:
            last_message = history[-2]["mensagem"].lower()
            if "nome" in last_message and len(last_message.split()) > 1:
                last_name = last_message.split()[-1]  # Última palavra da mensagem anterior
                entities["nomes"]["gato"] = last_name
                if "meu_lugar" in entities["lugares"] and entities["lugares"]["meu_lugar"] == last_name:
                    del entities["lugares"]["meu_lugar"]

    return entities

# Carrega configuração
def load_config():
    commands_path = BASE_DIR / COMMANDS_FILE
    if commands_path.exists():
        with commands_path.open('r', encoding='utf-8') as f:
            return json.load(f)
    raise FileNotFoundError(f"⚠️ Arquivo {commands_path} não encontrado.")

# Carrega histórico
def load_conversation_history():
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"conversas_{date_str}.json"
    if log_file.exists():
        with log_file.open('r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# Registra conversa
def log_conversation(message, response):
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"conversas_{date_str}.json"
    conversation = {"timestamp": datetime.now().isoformat(), "mensagem": message, "resposta": response}
    conversations = load_conversation_history()
    conversations.append(conversation)
    with log_file.open('w', encoding='utf-8') as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)

CONFIG = load_config()
COMMANDS = CONFIG["commands"]
ROLES = CONFIG["roles"]
APIS = CONFIG["apis"]
API_ORDER = CONFIG.get("api_order", ["openai", "grok", "deepseek", "llama"])

async def process_command(message, memory):
    message_lower = message.lower().strip()
    
    # Consultas à memória
    if "qual é o nome do meu gato" in message_lower or "me diga qual é o nome do meu gato" in message_lower or "e o nome do meu gato qual é" in message_lower:
        name = memory["entities"]["nomes"].get("gato")
        if name:
            return f"O nome do seu gato é {name}."
        return "Ainda não sei o nome do seu gato."
    elif "qual é o nome do meu lugar" in message_lower:
        place = memory["entities"]["lugares"].get("meu_lugar")
        if place:
            return f"O nome do seu lugar é {place}."
        return "Ainda não sei o nome do seu lugar."
    
    # Correção manual
    if "não" in message_lower and "se chama" in message_lower:
        parts = message_lower.split("se chama")
        if len(parts) > 1 and parts[1].strip():
            new_name = parts[1].strip().split()[0]
            if "gato" in message_lower:
                memory["entities"]["nomes"]["gato"] = new_name
                save_memory(memory)
                return f"Entendido, o nome do seu gato agora é {new_name}."
            elif "lugar" in message_lower:
                memory["entities"]["lugares"]["meu_lugar"] = new_name
                save_memory(memory)
                return f"Entendido, o nome do seu lugar agora é {new_name}."
    
    # Comandos padrão
    for cmd, info in COMMANDS.items():
        if cmd == message_lower:
            if info.get("os_command"):
                try:
                    result = subprocess.check_output(info["os_command"], shell=True, text=True, stderr=subprocess.STDOUT)
                    return result.strip()
                except Exception as e:
                    print(f"Erro ao executar comando '{cmd}': {e}")
                    return info.get("default_output", "Comando sem saída padrão.")
            return info.get("default_output", "Comando sem saída padrão.")
    return None

async def process_with_api(api, message):
    api_config = APIS.get(api, {})
    url = api_config.get("url")
    api_key = api_config.get("api_key")
    model = api_config.get("model")
    if not url:
        print(f"Think: URL não configurada para API {api}")
        return None
    async with aiohttp.ClientSession() as session:
        try:
            conversation_history = load_conversation_history()
            messages = [{"role": "system", "content": "Você tem memória de nomes, lugares e pessoas. Use-a quando necessário."}]
            for conv in conversation_history:
                messages.append({"role": "user", "content": conv["mensagem"]})
                messages.append({"role": "assistant", "content": conv["resposta"]})
            for role_entry in ROLES:
                messages.append({"role": role_entry["role"], "content": role_entry["content"].replace("{message}", message)})
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            payload = {"model": model, "messages": messages, "stream": False}
            print(f"Think: Enviando para API {api}: {json.dumps(payload, indent=2)}")
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    print(f"Erro na API {api}: {resp.status} - {error_text}")
                    return None
                result = await resp.json()
                response = result.get("choices", [{}])[0].get("message", {}).get("content")
                print(f"Think: Resposta da API {api}: {response}")
                return response
        except Exception as e:
            print(f"Erro na API {api}: {e}")
            return None

async def think(state):
    global should_stop
    ultima_mensagem = None
    memory = load_memory()
    while not should_stop:
        try:
            if state["message"] and state["message"] != ultima_mensagem and not state["thinking"]:
                print(f"Think: Nova mensagem recebida: {state['message']}")
                state["thinking"] = True
                if state.get("interrupt"):
                    print("Think: Interrompido.")
                    state["thinking"] = False
                    await asyncio.sleep(0.05)
                    continue
                
                # Corrige o texto
                raw_message = state["message"]
                corrected_message = correct_text(raw_message)
                print(f"Think: Texto bruto: {raw_message} → Corrigido: {corrected_message}")
                
                # Extrai e atualiza entidades
                entities = extract_entities(corrected_message)
                for category, values in entities.items():
                    memory["entities"][category].update(values)
                save_memory(memory)
                print(f"Think: Memória atualizada: {json.dumps(memory, indent=2)}")
                
                # Processa comando ou API
                response = await process_command(corrected_message, memory)
                if response is None:
                    print(f"Think: Não é comando local, tentando APIs...")
                    api_order = state.get("config", {}).get("api_order", API_ORDER)
                    for api in api_order:
                        response = await process_with_api(api, corrected_message)
                        if response:
                            break
                    if not response:
                        response = "Erro: todas as APIs falharam"
                
                log_conversation(corrected_message, response)
                state["response"] = response
                ultima_mensagem = state["message"]
                state["message"] = None
                state["last_speech_time"] = time.time()
                print(f"Think: Resposta definida: {response}")
                state["thinking"] = False
            else:
                print(f"Think: Aguardando - state: {dict(state)}")
            await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            print("Think: Tarefa cancelada")
            break
        except Exception as e:
            print(f"Think: Erro geral: {e}")
            state["thinking"] = False

if __name__ == "__main__":
    state = {
        "message": None,
        "response": None,
        "thinking": False,
        "interrupt": False,
        "last_speech_time": time.time(),
        "config": CONFIG
    }
    asyncio.run(think(state))