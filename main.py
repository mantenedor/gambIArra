import asyncio
import time
import sys
import os
from listen import listen
from speak import speak
from think import think
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import psutil

# Flag global para sinalizar encerramento
should_stop = False

def kill_other_instances():
    # Obter o nome do processo atual
    current_process_name = "gambIArra.exe" if getattr(sys, 'frozen', False) else os.path.basename(sys.argv[0])
    current_pid = os.getpid()  # PID do processo atual
    
    # Encerrar todos os outros processos com o mesmo nome
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] == current_process_name and proc.info['pid'] != current_pid:
                proc.kill()  # Força o encerramento do processo
                print(f"Encerrado processo {current_process_name} (PID: {proc.info['pid']})")
                time.sleep(0.5)  # Pequena pausa para liberar recursos como o microfone
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

# Executa a eliminação de instâncias duplicadas no início
kill_other_instances()

# Função para criar a imagem do ícone na bandeja
def create_image():
    # Cria uma imagem simples para o ícone
    image = Image.new('RGB', (64, 64), color=(255, 255, 255))  # Fundo branco
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 64, 64), fill=(0, 0, 255))  # Cor do ícone (azul)
    return image

# Função para parar o programa quando solicitado pelo ícone
def on_quit(icon, tasks):
    global should_stop
    should_stop = True
    for task in tasks:
        task.cancel()  # Cancela todas as tarefas assíncronas
    icon.stop()  # Para o ícone da bandeja

# Função para rodar as tarefas principais do programa
async def main():
    global should_stop
    state = {
        "listening": False,
        "speaking": False,
        "thinking": False,
        "message": None,
        "response": None,
        "adjusted": False,
        "interrupt": False,
        "last_speech_time": time.time()
    }
    print("Main: iniciando tarefas...")

    # Cria as tarefas assíncronas
    tasks = [
        asyncio.create_task(listen(state)),
        asyncio.create_task(speak(state)),
        asyncio.create_task(think(state))
    ]

    # Configura o ícone da bandeja
    menu = Menu(MenuItem("Sair", lambda icon, item: on_quit(icon, tasks)))
    icon = Icon("Assistente", create_image(), menu=menu)

    # Função para rodar o ícone em uma thread separada
    def run_icon():
        icon.run()

    # Inicia o ícone em uma thread separada
    import threading
    icon_thread = threading.Thread(target=run_icon, daemon=True)
    icon_thread.start()

    try:
        # Executa as tarefas assíncronas
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        print("Main: tarefas canceladas.")
    except Exception as e:
        print(f"Main: erro durante execução: {e}")
    finally:
        # Garante que o ícone pare ao encerrar
        icon.stop()
        print("Main: todas as tarefas e ícone encerrados.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Programa encerrado pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        sys.exit(1)