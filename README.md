O código implementa um **assistente de voz inteligente** que recebe comandos de áudio do usuário, interpreta e executa ações no sistema ou consulta a API do ChatGPT para fornecer respostas.  

Ele é composto por três módulos principais que se comunicam via WebSocket:  

- **`core.py`**: O núcleo do sistema, responsável por processar comandos, executar ações no sistema e se comunicar com a API do ChatGPT.  
- **`tts.py`** (Speech-to-Text - STT): Captura a entrada de áudio do usuário, converte em texto e envia para o `core.py`.  
- **`stt.py`** (Text-to-Speech - TTS): Recebe as respostas processadas e as converte em áudio para o usuário.  

O sistema suporta comandos pré-definidos e respostas geradas dinamicamente via IA, permitindo interações naturais e automação de tarefas.

---

## **Passos para utilizar o código**

### **1. Preparação do Ambiente**
Antes de rodar o sistema, certifique-se de que o ambiente está configurado corretamente:

#### **1.1 Instalar dependências**
Se ainda não tiver as dependências instaladas, instale-as com:
```bash
pip install websockets requests python-dotenv
```

#### **1.2 Configurar a chave da API do OpenAI**
- **Usando um arquivo `.env`**: Crie um arquivo `.env` na raiz do projeto e adicione a chave:
  ```
  OPENAI_API_KEY=your_api_key_here
  ```
- **Ou defina manualmente no terminal (Linux/macOS)**:
  ```bash
  export OPENAI_API_KEY="your_api_key_here"
  ```
- **No Windows (PowerShell)**:
  ```powershell
  $env:OPENAI_API_KEY="your_api_key_here"
  ```

#### **1.3 Criar o arquivo `commands.json`**
O código depende de um arquivo `commands.json`, que deve conter comandos mapeados para execução. Exemplo:
```json
{
  "abrir navegador": {
    "os_command": "firefox",
    "default_output": "Navegador aberto com sucesso."
  },
  "diga olá": {
    "os_command": "echo 'Olá, como posso ajudar?'",
    "default_output": "Olá, como posso ajudar?"
  }
}
```

---

### **2. Executar os componentes**
Os três arquivos (`core.py`, `tts.py` e `stt.py`) devem ser iniciados separadamente, pois se comunicam via WebSocket.

#### **2.1 Iniciar `core.py`**
O `core.py` é o coração do sistema, responsável por processar os comandos e interagir com o ChatGPT.
```bash
python core.py
```
Se estiver funcionando corretamente, deverá exibir:
```
🧠 Servidor WebSocket iniciado na porta 8765
```

#### **2.2 Iniciar `tts.py` (Speech-to-Text - STT)**
Esse arquivo captura áudio do usuário e envia o comando para `core.py` via WebSocket.
```bash
python tts.py
```
Se estiver funcionando, ele começará a capturar áudio e enviar comandos ao `core.py`.

#### **2.3 Iniciar `stt.py` (Text-to-Speech - TTS)**
Esse arquivo recebe as respostas de `core.py` e converte o texto em áudio para o usuário.
```bash
python stt.py
```
Quando rodar corretamente, ele receberá as respostas e falará a saída gerada pelo `core.py`.

---

### **3. Fluxo de funcionamento**
Com os três serviços rodando, o fluxo típico será:

1. **Usuário fala um comando** (capturado por `tts.py`).
2. **O áudio é convertido em texto e enviado ao WebSocket do `core.py`**.
3. **`core.py` processa o comando**:
   - Se for um comando conhecido (`commands.json`), executa a ação no sistema.
   - Se for um comando desconhecido, encaminha para a API do ChatGPT para gerar uma resposta.
4. **O resultado é enviado para `stt.py`**, que converte o texto em fala e reproduz para o usuário.

---

## **4. Testando a integração com o ChatGPT**
Se quiser testar diretamente a API do ChatGPT sem utilizar WebSocket, execute:
```bash
python test_chatgpt_integration.py
```
Ele pedirá uma entrada no terminal e mostrará a resposta da IA.

---

## **5. Solução de Problemas**
### **Erro: "Chave de API não encontrada"**
- Verifique se o arquivo `.env` contém a chave correta.
- Execute `echo $OPENAI_API_KEY` (Linux/macOS) ou `$env:OPENAI_API_KEY` (Windows) para confirmar que a variável está definida.

### **Erro ao conectar ao WebSocket**
- Certifique-se de que `core.py` está rodando antes de `tts.py` e `stt.py`.
- Verifique se as portas 8765 (para `core.py`) e 8766 (para TTS) estão livres e acessíveis.

### **Erro na execução de comandos do sistema**
- Confirme que `commands.json` está corretamente formatado.
- Teste os comandos manualmente no terminal para verificar se funcionam.

---

### **Conclusão**
Seguindo esses passos, você conseguirá rodar o sistema corretamente, garantindo a comunicação entre os componentes (`core.py`, `tts.py` e `stt.py`) via WebSocket e a integração com a API do ChatGPT. 🚀
