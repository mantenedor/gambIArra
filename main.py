import asyncio
import time
import sys
from listen import listen
from speak import speak
from think import think

# Flag global para sinalizar encerramento
should_stop = False

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
    tasks = [
        asyncio.create_task(listen(state)),
        asyncio.create_task(speak(state)),
        asyncio.create_task(think(state))
    ]
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("Main: recebendo interrupção...")
        should_stop = True
        for task in tasks:
            task.cancel()
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            print(f"Main: erro ao cancelar tarefas: {e}")
        print("Main: todas as tarefas encerradas")
        sys.exit(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Programa encerrado pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro geral: {e}")