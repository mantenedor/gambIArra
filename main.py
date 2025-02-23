import asyncio
import time
import multiprocessing
from listen import listen
from speak import speak
from think import think

async def main(state):
    """Função principal que inicia as tarefas assíncronas."""
    state["last_speech_time"] = time.time()  # Inicializa no estado compartilhado
    listen_task = asyncio.create_task(listen(state))
    speak_task = asyncio.create_task(speak(state))
    think_task = asyncio.create_task(think(state))
    await asyncio.gather(listen_task, speak_task, think_task)

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    manager = multiprocessing.Manager()
    state = manager.dict()
    state["listening"] = False
    state["speaking"] = False
    state["thinking"] = False
    state["message"] = None
    state["response"] = None
    state["adjusted"] = False
    state["interrupt"] = False
    asyncio.run(main(state))