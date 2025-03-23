### **README Ajustado - gambIArra**

# gambIArra - LEIAME

Bem-vindo ao **gambIArra**, um assistente pessoal de voz offline que utiliza reconhecimento de fala e memória para interagir com você!

---

## Descrição do Código

### Como Está Estruturado
O gambIArra é um projeto modular em Python, dividido em três componentes principais que trabalham juntos:
- **`listen.py`**: Captura áudio do microfone e usa o Vosk para converter voz em texto.
- **`think.py`**: Processa o texto recebido, gerencia a memória (`memory.json`), executa comandos locais ou consulta APIs.
- **`speak.py`**: Converte respostas em áudio usando síntese de voz.
- **`main.py`**: Integra os módulos, gerenciando o fluxo entre escuta, pensamento e fala.

O programa opera em um loop assíncrono, escutando continuamente, processando comandos e respondendo.

### Bibliotecas Utilizadas
- **`vosk`**: Reconhecimento de fala offline em português.
- **`spacy`**: Processamento de linguagem natural (modelo `pt_core_news_sm` para correção de texto e extração de entidades).
- **`aiohttp`**: Comunicação assíncrona com APIs externas (quando configurado).
- **`PyAudio`**: Captura e reprodução de áudio.
- **`json`**, **`pathlib`**, **`asyncio`**, **`subprocess`**, **`dotenv`**: Bibliotecas padrão do Python para manipulação de arquivos, assincronia e execução de comandos.

### Estrutura de Arquivos e Diretórios
```
gambIArra
│   .env                # Configurações de chaves API
│   close.wav           # Som de encerramento
│   commands.json       # Lista de comandos locais
│   gambIArra.ico       # Ícone do programa
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

### Hierarquia das APIs
O `think.py` suporta múltiplas APIs, consultadas na ordem definida em `commands.json` (padrão: `["openai", "grok", "deepseek", "llama"]`):
1. **OpenAI**: Primeira opção, se configurada.
2. **Grok**: Segunda opção (desenvolvido pela xAI).
3. **DeepSeek**: Terceira opção.
4. **LLaMA**: Última opção.
- Se uma API falhar (timeout ou erro), a próxima na lista é tentada. Caso todas falhem, retorna "Erro: todas as APIs falharam".

### Palavras-Chaves
- **"se chama"**: Define nomes (ex.: "Meu gato se chama Caxumba").
- **"qual é"**: Consulta memória (ex.: "Qual é o nome do meu gato?").
- **"não"**: Corrige informações (ex.: "Não, meu gato se chama Fumaça").
- **"gato"**, **"lugar"**, **"pessoas"**: Categorias de entidades salvas na memória.

---

## Utilização

Siga estas etapas para baixar, configurar e executar o `gambIArra`.

### 1. Baixe o Projeto
1. Acesse o link [https://github.com/mantenedor/gambIArra](https://github.com/mantenedor/gambIArra).
2. Clique no botão verde **"Code"** e depois em **"Download ZIP"**.
3. Salve o arquivo `gambIArra-main.zip` em uma pasta fácil de encontrar (ex.: `Documentos`).
4. Descompacte o arquivo:
   - No Windows: Clique com o botão direito no arquivo ZIP e escolha **"Extrair Tudo"**.
   - No Mac/Linux: Clique duas vezes no arquivo ZIP para descompactar.
5. Entre na pasta descompactada chamada `gambIArra-main`.

### 2. Instale o Python
O programa precisa do Python para funcionar.

1. Acesse [python.org](https://www.python.org/downloads/) e baixe a versão mais recente do Python (ex.: 3.9 ou superior).
2. Instale o Python:
   - **Windows**: Durante a instalação, marque a opção **"Add Python to PATH"** e clique em **"Install Now"**.
   - **Mac/Linux**: Siga as instruções do instalador ou use o gerenciador de pacotes (como `brew` no Mac ou `apt` no Linux).
3. Verifique se o Python foi instalado:
   - Abra o terminal (Prompt de Comando no Windows ou Terminal no Mac/Linux) e digite:
     ```bash
     python --version
     ```
   - Você deve ver algo como `Python 3.9.13`. Se não funcionar, tente `python3 --version`.

### 3. Instale as Dependências
O projeto precisa de algumas bibliotecas para funcionar.

1. Abra o terminal (Prompt de Comando ou Terminal).
2. Navegue até a pasta do projeto:
   - Exemplo no Windows:
     ```bash
     cd C:\Users\SeuUsuario\Documentos\gambIArra-main
     ```
   - Exemplo no Mac/Linux:
     ```bash
     cd ~/Documentos/gambIArra-main
     ```
3. Instale as bibliotecas necessárias:
   ```bash
   pip install -r requirements.txt
   ```
   - No Mac/Linux, pode ser necessário usar:
     ```bash
     pip3 install -r requirements.txt
     ```
4. Baixe o modelo do `spacy`:
   ```bash
   python -m spacy download pt_core_news_sm
   ```
   - Ou use `python3` no Mac/Linux.
5. Baixe o modelo Vosk (necessário para reconhecimento de voz):
   - No Windows:
     ```bash
     curl -L https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip -o models\vosk-model-small-pt-0.3.zip
     powershell -Command "Expand-Archive -Path models\vosk-model-small-pt-0.3.zip -DestinationPath models"
     del models\vosk-model-small-pt-0.3.zip
     ```
   - No Mac/Linux:
     ```bash
     curl -L https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip -o models/vosk-model-small-pt-0.3.zip
     unzip models/vosk-model-small-pt-0.3.zip -d models
     rm models/vosk-model-small-pt-0.3.zip
     ```

### 4. Configure o Python para Abrir o `main.py` com Dois Cliques
Para executar o programa clicando duas vezes no `main.py`, configure o Python como programa padrão para arquivos `.py`.

- **Windows**:
  1. Clique com o botão direito no arquivo `main.py` (dentro da pasta `gambIArra-main`).
  2. Escolha **"Abrir com"** > **"Escolher outro aplicativo"**.
  3. Selecione **"Python"** (pode aparecer como `python.exe` em `C:\Users\SeuUsuario\AppData\Local\Programs\Python\Python39`).
  4. Marque a opção **"Sempre usar este aplicativo para abrir arquivos .py"** e clique em **"OK"**.

- **Mac**:
  1. Clique com o botão direito no `main.py`.
  2. Escolha **"Abrir Com"** > **"Outros"**.
  3. Selecione **"Python Launcher"** (geralmente em `/usr/bin` ou instalado pelo `brew`).
  4. Marque **"Sempre Abrir Com"** e clique em **"Abrir"**.

- **Linux**:
  - Clicar duas vezes pode não funcionar diretamente no Linux, mas você pode criar um atalho:
    ```bash
    chmod +x main.py
    ```
    Ou execute pelo terminal (veja o próximo passo).

### 5. Execute o Programa
1. Na pasta `gambIArra-main`, localize o arquivo `main.py`.
2. Clique duas vezes no `main.py` para iniciar o programa.
   - Se a configuração do passo 4 não funcionar, abra o terminal na pasta do projeto e digite:
     ```bash
     python main.py
     ```
     Ou `python3 main.py` no Mac/Linux.

3. **Ícone na Bandeja do Sistema**:
   - Quando o programa iniciar, você verá um ícone na bandeja do sistema (área de notificação no Windows, ou barra de menu no Mac/Linux, se suportado).

4. **Palavra de Desbloqueio**:
   - Após 20 segundos do início do programa, você deve dizer a **palavra de desbloqueio** (definida no `commands.json`, como "gambIArra") para ativar o assistente. Fale a palavra claramente no microfone.

### 6. Teste o Programa
- Diga: "Meu gato se chama Caxumba."
- Diga: "Qual é o nome do meu gato?"
- O programa deve responder: "O nome do seu gato é Caxumba."

### 7. Configure as Chaves API (Opcional)
Se quiser usar APIs externas para respostas mais inteligentes:
- Edite o arquivo `.env` na pasta do projeto:
  ```
  OPENAI_API_KEY=sua-chave-aqui
  GROK_API_KEY=sua-chave-aqui
  DEEPSEEK_API_KEY=sua-chave-aqui
  LLAMA_API_KEY=sua-chave-aqui
  ```
- Obtenha as chaves nos respectivos serviços (ex.: OpenAI, xAI). Se não usar APIs, deixe em branco.

### 8. Configure Comandos Locais (Opcional)
- Edite o `commands.json` para adicionar comandos locais:
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

---

## Notas
- **Pré-requisitos**:
  - Certifique-se de ter um microfone funcional.
  - Tenha conexão à internet para baixar o projeto, as bibliotecas e os modelos.
- **Problemas**:
  - Se o programa não abrir ao clicar duas vezes, use o terminal para executar `python main.py` e veja as mensagens de erro.
  - Verifique os logs (como `conversas_YYYY-MM-DD.json`) para depurar.

Pronto! Agora você pode usar o `gambIArra` clicando duas vezes no `main.py`.
