import os
import json
import requests
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def chat_with_openai(prompt, model="gpt-3.5-turbo"):
    """Função para enviar uma mensagem à API do ChatGPT e obter a resposta."""
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

if __name__ == "__main__":
    prompt = input("Digite sua pergunta para o ChatGPT: ")
    response = chat_with_openai(prompt)
    if response:
        print(f"Resposta do ChatGPT: {response}")
    else:
        print("Não foi possível obter uma resposta.")

