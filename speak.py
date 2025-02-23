import asyncio
import pygame
import os
import pyttsx3  # Substitui gTTS para síntese offline rápida
import time

# Inicializa o sintetizador de voz offline
pygame.mixer.init()
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 200)  # Aumenta a velocidade da fala

# Variável de teste de fala
TEST_SPEECH = ""  # Deixe vazio ("") para fluxo normal

async def speak(state):
    """Gera e reproduz a resposta em áudio."""
    ultima_mensagem = None

    # Teste inicial de fala, se TEST_SPEECH estiver preenchido
    if TEST_SPEECH:
        print(f"Speak: executando teste de fala: {TEST_SPEECH}")
        state["speaking"] = True
        try:
            start_time = time.time()
            tts_engine.say(TEST_SPEECH)
            tts_engine.runAndWait()
            end_time = time.time()
            print(f"Speak: teste de fala concluído em {end_time - start_time:.2f} segundos")
        except Exception as e:
            print(f"Erro no teste de fala: {e}")
        finally:
            state["speaking"] = False

    # Fluxo normal de processamento
    while True:
        if state["response"] and state["response"] != "Null" and state["response"] != ultima_mensagem and not state["speaking"] and not state["thinking"]:
            print(f"Speak: falando: {state['response']}")
            state["speaking"] = True
            try:
                start_time = time.time()
                tts_engine.say(state["response"])
                tts_engine.runAndWait()
                end_time = time.time()
                if not state["interrupt"]:
                    ultima_mensagem = state["response"]
                    state["last_speech_time"] = time.time()  # Atualiza após reprodução
                print(f"Speak: reprodução concluída em {end_time - start_time:.2f} segundos")
            except Exception as e:
                print(f"Erro ao reproduzir áudio: {e}")
            finally:
                state["speaking"] = False
                state["response"] = None
                print("Speak: speaking desativado")
        await asyncio.sleep(0.01)  # Reduzido de 0.05 para 0.01

# Função para teste isolado
async def test_speak():
    state = {
        "speaking": False,
        "thinking": False,
        "interrupt": False,
        "response": None,
        "last_speech_time": time.time()
    }
    await speak(state)

if __name__ == "__main__":
    asyncio.run(test_speak())