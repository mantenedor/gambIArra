# LEIAME - gambIArra

Bem-vindo ao **gambIArra**, um assistente pessoal de voz offline que utiliza reconhecimento de fala e memória para interagir com você! Este documento explica como instalar, configurar e usar o programa.

## Descrição
O gambIArra é um assistente de voz desenvolvido em Python que:
- Usa o **Vosk** para reconhecimento de fala offline em português.
- Armazena informações como nomes (ex.: do seu gato), lugares e pessoas em um arquivo de memória (`memory.json`).
- Responde a comandos de voz configuráveis e perguntas simples, como "Qual é o nome do meu gato?".

## Requisitos
- **Sistema Operacional**: Windows (o instalador foi projetado para Windows).
- **Espaço em Disco**: Aproximadamente 100 MB (incluindo o modelo Vosk).
- **Permissões**: Não requer privilégios de administrador (roda como usuário comum).
- **Internet**: Necessária apenas na primeira instalação para baixar o modelo Vosk.

---

## Instalação

### Para Usuários Finais
1. **Baixe o Instalador**:
   - Obtenha o arquivo `gambIArra_Instalador.exe` na pasta `C:\Instaladores` (ou onde foi gerado pelo desenvolvedor).

2. **Execute o Instalador**:
   - Dê um duplo clique em `gambIArra_Instalador.exe`.
   - Siga as instruções na tela:
     - O instalador será salvo em `{userappdata}\gambIArra` (ex.: `C:\Users\SeuNome\AppData\Roaming\gambIArra`).
     - O modelo Vosk será baixado e descompactado automaticamente.

3. **Inicie o Programa**:
   - Após a instalação, procure "gambIArra" no menu Iniciar do Windows e clique para abrir.
   - O programa começará a escutar comandos de voz imediatamente.

### Para Desenvolvedores (Compilação Manual)
Se você quer compilar o projeto a partir do código-fonte:
1. **Instale o Python**:
   - Use Python 3.6 ou superior. Baixe em [python.org](https://www.python.org).

2. **Clone o Repositório** (se aplicável):
   - Copie os arquivos `.py`, `.wav`, `commands.json`, e o ícone `gambIArra.ico` do diretório original.

3. **Instale Dependências**:
   - Abra o terminal na pasta do projeto e execute:
     ```bash
     pip install -r requirements.txt
     ```

4. **Baixe o Modelo Vosk**:
   - O modelo `vosk-model-small-pt-0.3` já está incluído no comando PyInstaller, mas você pode baixá-lo manualmente em:
     ```
     https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
     ```
   - Descompacte-o na pasta `models`.

5. **Compile com PyInstaller**:
   - Execute o seguinte comando no terminal (ajuste os caminhos se necessário):
     ```bash
     python -m PyInstaller --onefile --collect-all vosk --add-data "models\vosk-model-small-pt-0.3;models\vosk-model-small-pt-0.3" --add-data "open.wav;." --add-data "close.wav;." --add-data "commands.json;." --windowed --clean --name gambIArra --icon=gambIArra.ico main.py
     ```
   - O executável `gambIArra.exe` será gerado na pasta `dist`.

6. **Crie o Instalador com Inno Setup**:
   - Baixe e instale o Inno Setup ([innosetup.com](https://jrsoftware.org/isinfo.php)).
   - Abra o arquivo `.iss` fornecido no bloco de notas ou no Inno Setup Compiler.
   - Ajuste os caminhos em `[Files]` para corresponder ao seu diretório local (ex.: `C:\SeuCaminho\`).
   - Compile o script clicando em "Build" > "Compile".
   - O instalador `gambIArra_Instalador.exe` será gerado em `C:\Instaladores`.

---

## Uso
1. **Iniciando**:
   - Ao abrir o `gambIArra.exe`, você ouvirá um som (`open.wav`) indicando que o assistente está ativo e escutando.

2. **Comandos Básicos**:
   - **Definir um nome**: Diga "Meu gato se chama Bagunça" ou "O nome do meu gato é Bagunça".
   - **Consultar um nome**: Diga "Qual é o nome do meu gato?" ou "E o nome do meu gato qual é?".
   - **Corrigir um nome**: Diga "Não, meu gato se chama Fumaça" para atualizar a memória.
   - Outros comandos estão definidos no arquivo `commands.json`.

3. **Encerrando**:
   - Feche a janela (se visível) ou use um comando de voz configurado para sair (se implementado).

4. **Memória**:
   - O assistente salva informações em `memory.json` na pasta de instalação. Exemplo:
     ```json
     {
       "user_id": "default_user",
       "entities": {
         "nomes": {"gato": "caxumba"},
         "lugares": {},
         "pessoas": {}
       }
     }
     ```

---

## Configuração Avançada
- **Editar Comandos**:
  - Abra `commands.json` na pasta de instalação e adicione ou modifique comandos. Exemplo:
    ```json
    {
      "commands": {
        "abrir notepad": {
          "os_command": "notepad.exe",
          "default_output": "Abrindo o Notepad..."
        }
      }
    }
    ```
- **Alterar Sons**:
  - Substitua `open.wav` e `close.wav` por outros arquivos WAV na pasta de instalação.

---

## Solução de Problemas
- **O programa não escuta**:
  - Verifique se o microfone está conectado e funcionando.
  - Confirme que o modelo Vosk está na pasta `models\vosk-model-small-pt-0.3`.
- **Erro ao abrir**:
  - Certifique-se de que o instalador terminou de baixar e descompactar o modelo Vosk. Reinstale se necessário.
- **Respostas erradas**:
  - Veja o log em `conversas_YYYY-MM-DD.json` para depurar o que foi reconhecido e respondido.

---

## Contribuições
Se você é desenvolvedor e quer melhorar o gambIArra:
- Adicione suporte a mais idiomas no Vosk.
- Melhore a correção de texto com um modelo spaCy maior (ex.: `pt_core_news_md`).
- Envie sugestões ou correções ao criador original!
