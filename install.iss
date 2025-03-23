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
Source: ".\gambIArra-main\005\*.py"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\gambIArra-main\005\*.wav"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\gambIArra-main\005\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\gambIArra-main\005\models\*"; DestDir: "{app}\models"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: ".\gambIArra-main\005\commands.json"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\gambIArra-main\005\gambIArra.ico"; DestDir: "{app}"; Flags: ignoreversion

[Run]
; Instala Python
Filename: "cmd.exe"; Parameters: "/C if not exist ""C:\Users\{username}\AppData\Local\Programs\Python\Python39\python.exe"" (curl -L https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe -o ""{tmp}\python-installer.exe"" && ""{tmp}\python-installer.exe"" /quiet InstallAllUsers=0 PrependPath=1)"; StatusMsg: "Instalando Python..."; Flags: runhidden waituntilterminated
; Configura pip
Filename: "cmd.exe"; Parameters: "/C ""C:\Users\{username}\AppData\Local\Programs\Python\Python39\python.exe"" -m ensurepip && ""C:\Users\{username}\AppData\Local\Programs\Python\Python39\python.exe"" -m pip install --upgrade pip > ""{app}\pip_setup_log.txt"" 2>&1"; StatusMsg: "Configurando pip..."; Flags: runhidden waituntilterminated
; Cria requirements.txt se não existir
Filename: "cmd.exe"; Parameters: "/C if not exist ""{app}\requirements.txt"" (echo vosk>""{app}\requirements.txt"" && echo spacy>>""{app}\requirements.txt"" && echo aiohttp>>""{app}\requirements.txt"" && echo PyAudio==0.2.14>>""{app}\requirements.txt"")"; StatusMsg: "Criando requirements.txt..."; Flags: runhidden waituntilterminated
; Instala dependências do requirements.txt com log
Filename: "cmd.exe"; Parameters: "/C ""C:\Users\{username}\AppData\Local\Programs\Python\Python39\python.exe"" -m pip install -r ""{app}\requirements.txt"" > ""{app}\pip_install_log.txt"" 2>&1"; StatusMsg: "Instalando dependências Python..."; Flags: runhidden waituntilterminated
; Baixa e instala o modelo spaCy com log
Filename: "cmd.exe"; Parameters: "/C ""C:\Users\{username}\AppData\Local\Programs\Python\Python39\python.exe"" -m spacy download pt_core_news_sm --no-deps > ""{app}\spacy_model_log.txt"" 2>&1"; StatusMsg: "Baixando e instalando o modelo spaCy (pt_core_news_sm)..."; Flags: runhidden waituntilterminated
; Baixa e descompacta o modelo Vosk
Filename: "cmd.exe"; Parameters: "/C curl -L https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip -o ""{app}\models\vosk-model-small-pt-0.3.zip"""; StatusMsg: "Baixando o modelo Vosk..."; Flags: runhidden waituntilterminated
Filename: "cmd.exe"; Parameters: "/C powershell -Command Expand-Archive -Path ""{app}\models\vosk-model-small-pt-0.3.zip"" -DestinationPath ""{app}\models"""; StatusMsg: "Descompactando o modelo Vosk..."; Flags: runhidden waituntilterminated
Filename: "cmd.exe"; Parameters: "/C del ""{app}\models\vosk-model-small-pt-0.3.zip"""; StatusMsg: "Removendo arquivo zip..."; Flags: runhidden waituntilterminated

[Icons]
; Cria um atalho para main.py no menu Iniciar com o ícone gambIArra.ico
Name: "{userstartmenu}\gambIArra"; Filename: "C:\Users\{username}\AppData\Local\Programs\Python\Python39\python.exe"; Parameters: """{app}\main.py"""; IconFilename: "{app}\gambIArra.ico"; WorkingDir: "{app}"