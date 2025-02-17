import asyncio
import subprocess

async def run_script(script, log_file):
    # Criar um subprocesso para executar o script Python e redirecionar para um arquivo de log
    with open(log_file, 'w') as log:
        process = await asyncio.create_subprocess_exec(
            'python3', script,
            stdout=log,
            stderr=log
        )
        # Esperar que o script termine
        await process.communicate()

async def main():
    log_file_core = '/tmp/core.log'
    log_file_tts = '/tmp/tts.log'
    log_file_stt = '/tmp/stt.log'

    # Executar todos os scripts simultaneamente, com redirecionamento para o log
    await asyncio.gather(
        run_script("/opt/lacaia/core.py", log_file_core),
        run_script("/opt/lacaia/tts.py", log_file_tts),
        run_script("/opt/lacaia/stt.py", log_file_stt)
    )

# Executar a função principal de forma assíncrona
asyncio.run(main())

