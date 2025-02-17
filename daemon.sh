#!/bin/bash

LOG_FILE="/tmp/lacaia.log"
MAX_LOG_SIZE=100000000  # 100MB

# Função para verificar e rotacionar o log
rotate_log() {
    if [ -f "$LOG_FILE" ] && [ $(stat --format=%s "$LOG_FILE") -gt $MAX_LOG_SIZE ]; then
        mv "$LOG_FILE" "$LOG_FILE.old"
        touch "$LOG_FILE"
    fi
}

# Executar os scripts Python em segundo plano e redirecionar para o arquivo de log
start_script() {
    rotate_log
    /usr/bin/python3 /opt/lacaia/core.py >> "$LOG_FILE" 2>&1 &
    /usr/bin/python3 /opt/lacaia/tts.py >> "$LOG_FILE" 2>&1 &
    /usr/bin/python3 /opt/lacaia/stt.py >> "$LOG_FILE" 2>&1 &
}

# Chamada para iniciar os scripts
start_script

# Manter o script em execução como daemon
while true; do
    sleep 60
    rotate_log  # Verifica a cada 60 segundos se o log precisa ser rotacionado
done
