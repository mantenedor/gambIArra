# gambIArra - Assistente de Voz Multifuncional

## Finalidade

Este projeto é um assistente de voz em Python que integra captura de áudio, processamento de texto, e síntese de voz. Ele permite interação por comandos de voz, incluindo palavras-chave para controle (como "oxe" para desbloqueio e "para para para" para interrupção) e comandos específicos definidos em JSON (ex.: "horas", "data", "tempo"). O sistema suporta processamento local de comandos do sistema operacional e integração com APIs de inteligência artificial (OpenAI, Grok, Deepseek, Ollama) para respostas dinâmicas.

O assistente é projetado para:
- Capturar comandos de voz em tempo real.
- Executar ações locais (ex.: verificar horário) ou consultas via APIs.
- Entrar em modo de inatividade após 10 segundos sem interação, exigindo desbloqueio com "oxe".
- Interromper a fala com "para para para".

## Estrutura do Código

O projeto é dividido em quatro arquivos principais, todos em Python, que trabalham juntos de forma assíncrona usando o módulo `asyncio`:

- **`main.py`**: Ponto de entrada do programa. Configura o estado compartilhado (`state`) via `multiprocessing.Manager` e inicializa as tarefas assíncronas `listen`, `speak`, e `think`.
- **`listen.py`**: Responsável pela captura de áudio usando `speech_recognition`. Detecta palavras-chave ("oxe", "para para para") e envia mensagens capturadas ao `think`.
- **`speak.py`**: Gera e reproduz áudio usando `pyttsx3` (sintetizador offline). Responde às mensagens processadas pelo `think`.
- **`think.py`**: Processa mensagens recebidas do `listen`. Verifica comandos JSON locais (ex.: "horas") e executa ações via `subprocess`, ou encaminha para APIs externas na ordem de prioridade definida.

### Fluxo Básico
1. `listen` captura áudio e atualiza `state["message"]`.
2. `think` processa `state["message"]`, verifica comandos locais ou consulta APIs, e define `state["response"]`.
3. `speak` reproduz `state["response"]` como áudio.
4. O estado compartilhado (`state`) coordena as interações entre os módulos.

## Instalação

### 1. Instalação do Python via Winget (Windows)
Para instalar o Python usando o `winget` (gerenciador de pacotes do Windows):
1. Abra o **Prompt de Comando** ou **Terminal**.
2. Execute o comando:
   ```
   winget install -e --id Python.Python.3
   ```
3. Confirme a instalação verificando a versão:
   ```
   python --version
   ```
   Você deve ver algo como `Python 3.11.x` ou superior.

### 2. Dependências do Código
O projeto requer as seguintes bibliotecas Python:
- `speechrecognition`: Para captura de áudio.
- `pygame`: Para controle de áudio (usado em `listen` para interrupção).
- `pyttsx3`: Para síntese de voz offline.
- `aiohttp`: Para chamadas assíncronas às APIs.
- `python-dotenv`: Para carregar chaves de API do arquivo `.env`.

#### Usando `requirements.txt`
1. Crie um arquivo chamado `requirements.txt` no diretório do projeto com o seguinte conteúdo:
   ```
   speechrecognition
   pygame
   pyttsx3
   aiohttp
   python-dotenv
   ```
2. Instale todas as dependências com:
   ```
   pip install -r requirements.txt
   ```

Alternativamente, se preferir instalar manualmente, use:
```
pip install speechrecognition pygame pyttsx3 aiohttp python-dotenv
```

## Chaves de API

O código suporta APIs externas (`openai`, `llama`, `grok`, `deepseek`). As chaves de API são necessárias para acessar essas APIs e devem ser configuradas em um arquivo `.env`.

### O que são Chaves de API?
Chaves de API são códigos únicos fornecidos por serviços de inteligência artificial para autenticar e autorizar acesso às suas funcionalidades. Elas são como "senhas" que identificam seu aplicativo ao usar os serviços.

### Como Obter as Chaves de API
1. **OpenAI**:
   - Crie uma conta em `https://platform.openai.com`.
   - Vá para "API Keys" no painel, crie uma nova chave, e copie-a.
   - Adicione ao `.env`:
     ```
     OPENAI_API_KEY=sua-chave-aqui
     ```

2. **Grok (xAI)**:
   - Acesse `https://x.ai` ou o console da xAI (ex.: `console.x.ai`).
   - Faça login, vá para "API Keys", gere uma chave, e copie-a.
   - Adicione ao `.env`:
     ```
     GROK_API_KEY=sua-chave-aqui
     ```

3. **Deepseek**:
   - Visite `https://deepseek.com`, crie uma conta, e gere uma chave no painel de desenvolvedor.
   - Adicione ao `.env`:
     ```
     DEEPSEEK_API_KEY=sua-chave-aqui
     ```

4. **Ollama (Local)**:
   - Não requer chave de API, mas precisa estar rodando localmente (`http://localhost:11434` por padrão).
   - Instale o Ollama: `curl https://ollama.ai/install.sh | sh` (Linux/Mac) ou baixe em `https://ollama.ai` (Windows).
   - Configure o host/modelo no `.env` (opcional):
     ```
     OLLAMA_HOST=http://localhost:11434
     OLLAMA_MODEL=llama2
     ```

Crie o arquivo `.env` no diretório do projeto com as chaves necessárias.

## Como Executar e Interagir

### Clonar o Projeto via Git
1. Instale o Git (se não estiver instalado):
   ```
   winget install -e --id Git.Git
   ```
2. Abra o terminal e clone o repositório:
   ```
   git clone <URL_DO_REPOSITORIO>
   ```
   Substitua `<URL_DO_REPOSITORIO>` pela URL do seu repositório Git.
3. Navegue até o diretório do projeto:
   ```
   cd <NOME_DA_PASTA>
   ```

### Configurar e Executar
1. Crie o arquivo `.env` com as chaves de API (veja acima).
2. Crie o arquivo `requirements.txt` com as dependências listadas acima.
3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
4. Execute o programa:
   ```
   python main.py
   ```

### Interagir com o Código
- **Comandos de Voz**:
  - Fale "horas" para ouvir o horário atual.
  - Fale "data" para ouvir a data atual.
  - Fale "tempo" para uma resposta padrão (pode ser ajustado).
  - Fale qualquer outra frase (ex.: "Oi, tudo bem?") para processamento via APIs.

- **Controle**:
  - Após 10 segundos sem falar, o sistema entra em modo de inatividade e aguarda "oxe" para desbloquear.
  - Durante a fala do assistente, diga "para para para" para interromper.

## Personalização

### Alterar Palavras-Chave
Edite as variáveis no início de `listen.py`:
- **`UNLOCK_KEYWORD`**: Mude de "oxe" para outra palavra (ex.: "olá"):
  ```python
  UNLOCK_KEYWORD = "olá"
  ```
- **`STOP_KEYWORD`**: Mude de "para para para" para outra frase (ex.: "pare"):
  ```python
  STOP_KEYWORD = "pare"
  ```

### Alterar Variáveis de Teste
- **`TEST_MESSAGE` em `think.py`**:
  - Teste uma mensagem fixa editando:
    ```python
    TEST_MESSAGE = "Que horas são?"
    ```
  - Execute `python think.py` para testar isoladamente.
- **`TEST_SPEECH` em `speak.py`**:
  - Teste uma fala fixa editando:
    ```python
    TEST_SPEECH = "Teste de voz"
    ```
  - Execute `python speak.py` para testar isoladamente.

### Alterar Comandos JSON em `think.py`
Edite a lista `COMMANDS` para adicionar ou modificar comandos:
- Exemplo de adição de um novo comando "quem sou eu":
  ```python
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
          "os_command": "echo 'cmd ok'",
          "default_output": "Informação climática não disponível no momento."
      },
      "quem sou eu": {
          "description": "Retorna uma identificação fixa",
          "os_command": "echo 'Você é um usuário!'",
          "default_output": "Não sei quem você é."
      }
  }
  ```
- A chave (`command_key`) é o que o sistema reconhece na fala, `os_command` é o comando executado no sistema, e `default_output` é a resposta padrão em caso de erro.

## Estrutura do Diretório
```
project_folder/
│
├── main.py           # Ponto de entrada e coordenação
├── listen.py         # Captura áudio e controle
├── speak.py          # Reprodução de áudio
├── think.py          # Processamento de comandos e APIs
├── .env              # Arquivo de chaves de API (crie manualmente)
├── requirements.txt  # Lista de dependências (crie manualmente)
└── README.md         # Este arquivo
```

## Notas
- O sistema depende de um microfone funcional e conexão à internet para APIs (exceto Ollama, que é local).
- Os comandos locais são limitados ao sistema operacional (Windows/Linux). Ajuste `os_command` conforme necessário.

---

### **Mudanças Realizadas**
1. **Instrução de Instalação**:
   - Substituí `pip install speechrecognition pygame pyttsx3 aiohttp python-dotenv` por:
     ```
     pip install -r requirements.txt
     ```
   - Adicionei instruções para criar o arquivo `requirements.txt` com as dependências listadas.

2. **Estrutura do Diretório**:
   - Atualizei para incluir `requirements.txt` como parte do projeto.

### **Próximos Passos**
- Salve este conteúdo como `README.md` no diretório do projeto.
- Crie o arquivo `requirements.txt` com:
  ```
  speechrecognition
  pygame
  pyttsx3
  aiohttp
  python-dotenv
  ```
- Teste as instruções clonando o projeto e seguindo os passos.
