import asyncio
import speech_recognition as sr
import time
import pygame

# Variáveis de configuração para palavras-chave
UNLOCK_KEYWORD = "oxe"  # Palavra para desbloquear após inatividade
STOP_KEYWORD = "para para para"  # Palavra para interromper o sistema

async def recognize_speech(state, interrupt_mode=False):
    """Reconhece a fala do usuário usando pause_threshold para fim de frase."""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    try:
        with mic as source:
            if not state.get("adjusted", False):
                print("🎤 Ajustando para ruído ambiente...")
                recognizer.adjust_for_ambient_noise(source, duration=0.2)
                state["adjusted"] = True
            print("🎤 Escutando" + (" (interrupção)" if interrupt_mode else "") + "...")
            audio = recognizer.listen(source, timeout=5 if interrupt_mode else 5)
            recognizer.pause_threshold = 1.0  # 1 segundo de silêncio para fim de frase
        
        print("🔊 Reconhecendo áudio...")
        sentence = recognizer.recognize_google(audio, language="pt-BR")
        print(f"📝 Reconhecido: {sentence}")
        return sentence
    except sr.UnknownValueError:
        print("❌ Não foi possível entender o áudio.")
        return None
    except sr.RequestError as e:
        print(f"❌ Erro na requisição ao serviço de reconhecimento: {e}")
        return None
    except sr.WaitTimeoutError:
        print("❌ Timeout: nenhuma fala detectada.")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado no reconhecimento: {e}")
        return None

async def listen(state):
    """Ouve o usuário e processa a fala com reativação por 'feijoada'."""
    INACTIVITY_TIMEOUT = 10.0
    while True:
        # Modo de interrupção: sempre ativo para "para para para"
        state["listening"] = True
        sentence_interrupt = await recognize_speech(state, interrupt_mode=True)
        if sentence_interrupt and STOP_KEYWORD in sentence_interrupt.lower():
            print(f"Listen: palavra-chave '{STOP_KEYWORD}' detectada, interrompendo...")
            state["interrupt"] = True
            state["message"] = None
            state["response"] = None
            pygame.mixer.music.stop()
            await asyncio.sleep(0.1)
            state["interrupt"] = False
            state["listening"] = False
            print(f"Debug: estados após interrupção - speaking: {state['speaking']}, thinking: {state['thinking']}")
            continue
        
        # Verifica inatividade
        if (time.time() - state["last_speech_time"] > INACTIVITY_TIMEOUT) and not state["speaking"] and not state["thinking"] and not state["response"]:
            print(f"🕒 Sistema inativo há mais de 10 segundos. Aguardando '{UNLOCK_KEYWORD}' (diga '{STOP_KEYWORD}' para interromper)...")
            if sentence_interrupt and UNLOCK_KEYWORD in sentence_interrupt.lower():
                print(f"✅ Palavra '{UNLOCK_KEYWORD}' detectada. Retomando operação normal.")
                state["last_speech_time"] = time.time()
                state["message"] = None
                state["response"] = None
                state["interrupt"] = False
                state["speaking"] = False
                state["thinking"] = False
            continue
        
        # Modo normal: captura frases completas apenas se não estiver pensando e não inativo
        if not state["thinking"] and (time.time() - state["last_speech_time"] <= INACTIVITY_TIMEOUT):
            if sentence_interrupt and not state["speaking"]:
                state["last_speech_time"] = time.time()
                state["message"] = sentence_interrupt
                print(f"Listen: capturado no modo interrupção e enviado: {sentence_interrupt}")
                print(f"Debug: mensagem enviada ao think - message: {state['message']}, speaking: {state['speaking']}, thinking: {state['thinking']}")
            else:
                print("Listen: iniciando captura de áudio...")
                sentence_normal = await recognize_speech(state, interrupt_mode=False)
                if sentence_normal:
                    state["last_speech_time"] = time.time()
                    state["message"] = sentence_normal
                    print(f"Listen: capturado e enviado: {sentence_normal}")
                    print(f"Debug: mensagem enviada ao think - message: {state['message']}, speaking: {state['speaking']}, thinking: {state['thinking']}")
        
        state["listening"] = False
        await asyncio.sleep(0.05)