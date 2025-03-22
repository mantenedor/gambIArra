# gambIArra - LEIAME

Bem-vindo ao **gambIArra**, um assistente pessoal de voz offline que utiliza reconhecimento de fala e memória para interagir com você!

---

# Descrição do Código

## Como Está Estruturado
O gambIArra é um projeto modular em Python, dividido em três componentes principais que trabalham juntos:
- **`listen.py`**: Captura áudio do microfone e usa o Vosk para converter voz em texto.
- **`think.py`**: Processa o texto recebido, gerencia a memória (`memory.json`), executa comandos locais ou consulta APIs.
- **`speak.py`**: Converte respostas em áudio usando síntese de voz.
- **`main.py`**: Integra os módulos, gerenciando o fluxo entre escuta, pensamento e fala.

O programa opera em um loop assíncrono, escutando continuamente, processando comandos e respondendo.

## Bibliotecas Utilizadas
- **`vosk`**: Reconhecimento de fala offline em português.
- **`spacy`**: Processamento de linguagem natural (modelo `pt_core_news_sm` para correção de texto e extração de entidades).
- **`aiohttp`**: Comunicação assíncrona com APIs externas (quando configurado).
- **`pyinstaller`**: Compilação do projeto em um executável standalone.
- **`json`**, **`pathlib`**, **`asyncio`**, **`subprocess`**, **`dotenv`**: Bibliotecas padrão do Python para manipulação de arquivos, assincronia e execução de comandos.

## Estrutura de Arquivos e Diretórios
```
gambIArra
│   .env                # Configurações de chaves API
│   close.wav           # Som de encerramento
│   commands.json       # Lista de comandos locais
│   gambIArra.ico       # Ícone do programa
│   install.iss         # Script Inno Setup para criar o instalador
│   listen.py           # Módulo de reconhecimento de fala
│   main.py             # Script principal que integra os módulos
│   memory.json         # Arquivo de memória persistente
│   open.wav            # Som de inicialização
│   requirements.txt    # Lista de dependências Python
│   speak.py            # Módulo de síntese de voz
│   think.py            # Módulo de processamento e lógica
└───models
   └───vosk-model-small-pt-0.3
       │   disambig_tid.int    # Arquivos do modelo Vosk
       │   final.mdl
       │   Gr.fst
       │   HCLr.fst
       │   mfcc.conf
       │   phones.txt
       │   README
       │   word_boundary.int
       └───ivector
               final.dubm       # Configurações de ivector do Vosk
               final.ie
               final.mat
               global_cmvn.stats
               online_cmvn.conf
               splice.conf
```

## Hierarquia das APIs
O `think.py` suporta múltiplas APIs, consultadas na ordem definida em `commands.json` (padrão: `["openai", "grok", "deepseek", "llama"]`):
1. **OpenAI**: Primeira opção, se configurada.
2. **Grok**: Segunda opção (desenvolvido pela xAI).
3. **DeepSeek**: Terceira opção.
4. **LLaMA**: Última opção.
- Se uma API falhar (timeout ou erro), a próxima na lista é tentada. Caso todas falhem, retorna "Erro: todas as APIs falharam".

## Palavras-Chaves
- **"se chama"**: Define nomes (ex.: "Meu gato se chama Bagunça").
- **"qual é"**: Consulta memória (ex.: "Qual é o nome do meu gato?").
- **"não"**: Corrige informações (ex.: "Não, meu gato se chama Fumaça").
- **"gato"**, **"lugar"**, **"pessoas"**: Categorias de entidades salvas na memória.

---

# Utilização

## Como Configurar
1. **Pré-requisitos**:
   - Certifique-se de ter um microfone funcional.
   - Tenha conexão à internet para a primeira instalação.

2. **Instalação Básica**:
   - Execute o instalador `gambIArra_Instalador.exe` (veja "Compilação" para gerá-lo).

## Configuração das Chaves API
- Edite o arquivo `.env` na pasta de instalação:
  ```
  OPENAI_API_KEY=sua-chave-aqui
  GROK_API_KEY=sua-chave-aqui
  DEEPSEEK_API_KEY=sua-chave-aqui
  LLAMA_API_KEY=sua-chave-aqui
  ```
- Obtenha as chaves nos respectivos serviços (ex.: OpenAI, xAI). Se não usar APIs, deixe em branco.

## Configuração do ".env"
- O arquivo `.env` é carregado pelo `dotenv` em `think.py`. Exemplo:
  ```
  OPENAI_API_KEY=sk-xxx
  GROK_API_KEY=xk-xxx
  ```
- Coloque-o na raiz do projeto ou na pasta de instalação.

## Configuração do "commands.json"
- Edite `commands.json` para adicionar comandos locais:
  ```json
  {
    "commands": {
      "abrir notepad": {
        "os_command": "notepad.exe",
        "default_output": "Abrindo o Notepad..."
      }
    },
    "roles": [],
    "apis": {
      "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "api_key": "{OPENAI_API_KEY}",
        "model": "gpt-3.5-turbo"
      }
    },
    "api_order": ["openai", "grok", "deepseek", "llama"]
  }
  ```
- **`commands`**: Define ações locais.
- **`apis`**: Configura endpoints e modelos.
- **`api_order`**: Ordem de tentativa das APIs.

## Como Testar
1. Execute `gambIArra.exe`.
2. Diga: "Meu gato se chama Bagunça."
3. Diga: "Qual é o nome do meu gato?"
   - Esperado: "O nome do seu gato é Bagunça."
4. Verifique `memory.json` e `conversas_YYYY-MM-DD.json` para depurar.

---

# Compilação

## Como Compilar
1. **Instale o Python**:
   - Baixe Python 3.6+ em [python.org](https://www.python.org). Marque "Add Python to PATH".

2. **Crie o `requirements.txt`**:
   - Manualmente:
     ```
     vosk
     spacy
     aiohttp
     pyinstaller
     ```
   - Ou gere com:
     ```bash
     pip freeze > requirements.txt
     ```

3. **Instale Dependências**:
   ```bash
   pip install -r requirements.txt
   python -m spacy download pt_core_news_sm
   ```

4. **Compile com PyInstaller**:
   ```bash
   python -m PyInstaller --onefile --collect-all vosk --add-data "models\vosk-model-small-pt-0.3;models\vosk-model-small-pt-0.3" --add-data "open.wav;." --add-data "close.wav;." --add-data "commands.json;." --windowed --clean --name gambIArra --icon=gambIArra.ico main.py
   ```
   - Resultado: `dist\gambIArra.exe`.

## Como Gerar um Instalador
1. **Instale o Inno Setup**:
   - Baixe em [innosetup.com](https://jrsoftware.org/isinfo.php).

2. **Edite o `install.iss`**:
   ```ini
   [Setup]
   AppName=gambIArra
   AppVersion=1.0
   DefaultDirName={userappdata}\gambIArra
   DefaultGroupName=gambIArra
   OutputDir=C:\Instaladores
   OutputBaseFilename=gambIArra_Instalador
   Compression=lzma
   SolidCompression=yes
   PrivilegesRequired=lowest

   [Files]
   Source: "*.py"; DestDir: "{app}"; Flags: ignoreversion
   Source: "*.wav"; DestDir: "{app}"; Flags: ignoreversion
   Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists('requirements.txt')
   Source: "models\*"; DestDir: "{app}\models"; Flags: ignoreversion recursesubdirs createallsubdirs
   Source: "dist\gambIArra.exe"; DestDir: "{app}"; Flags: ignoreversion
   Source: "commands.json"; DestDir: "{app}"; Flags: ignoreversion
   Source: "gambIArra.ico"; DestDir: "{app}"; Flags: ignoreversion

   [Run]
   Filename: "cmd.exe"; Parameters: "/C if not exist ""C:\Users\{username}\AppData\Local\Programs\Python\Python39\python.exe"" (curl -L https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe -o ""{tmp}\python-installer.exe"" && ""{tmp}\python-installer.exe"" /quiet InstallAllUsers=0 PrependPath=1)"; StatusMsg: "Instalando Python..."; Flags: runhidden waituntilterminated
   Filename: "cmd.exe"; Parameters: "/C python -m ensurepip && python -m pip install --upgrade pip"; StatusMsg: "Configurando pip..."; Flags: runhidden waituntilterminated
   Filename: "cmd.exe"; Parameters: "/C if not exist ""{app}\requirements.txt"" (echo vosk>""{app}\requirements.txt"" && echo spacy>>""{app}\requirements.txt"" && echo aiohttp>>""{app}\requirements.txt"" && echo pyinstaller>>""{app}\requirements.txt"")"; StatusMsg: "Criando requirements.txt..."; Flags: runhidden waituntilterminated
   Filename: "cmd.exe"; Parameters: "/C python -m pip install -r ""{app}\requirements.txt"""; StatusMsg: "Instalando dependências Python..."; Flags: runhidden waituntilterminated
   Filename: "cmd.exe"; Parameters: "/C python -m spacy download pt_core_news_sm"; StatusMsg: "Instalando modelo spaCy..."; Flags: runhidden waituntilterminated
   Filename: "cmd.exe"; Parameters: "/C curl -L https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip -o ""{app}\models\vosk-model-small-pt-0.3.zip"""; StatusMsg: "Baixando o modelo Vosk..."; Flags: runhidden waituntilterminated
   Filename: "cmd.exe"; Parameters: "/C powershell -Command Expand-Archive -Path ""{app}\models\vosk-model-small-pt-0.3.zip"" -DestinationPath ""{app}\models"""; StatusMsg: "Descompactando o modelo Vosk..."; Flags: runhidden waituntilterminated
   Filename: "cmd.exe"; Parameters: "/C del ""{app}\models\vosk-model-small-pt-0.3.zip"""; StatusMsg: "Removendo arquivo zip..."; Flags: runhidden waituntilterminated

   [Icons]
   Name: "{userstartmenu}\gambIArra"; Filename: "{app}\gambIArra.exe"; IconFilename: "{app}\gambIArra.ico"; WorkingDir: "{app}"
   ```

3. **Compile o Instalador**:
   - Abra o `install.iss` no Inno Setup Compiler e clique em "Build" > "Compile".
   - Resultado: `C:\Instaladores\gambIArra_Instalador.exe`.

---
