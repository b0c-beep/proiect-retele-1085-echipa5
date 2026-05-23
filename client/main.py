import asyncio
import threading
from commands import process_user_commands

def ui_thread_func(loop, queue):
    # Aceasta functie ruleaza pe un thread separat de event loop-ul asyncio.
    # Motivul: input() este blocant - daca l-am rula direct in asyncio,
    # ar ingheata toata comunicarea cu serverul cat timp asteptam sa tastam.
    # Solutia: citim inputul pe un thread dedicat si trimitem comanda in coada asyncio.
    while True:
        try:
            cmd = input("client> ")
            if cmd.strip():
                # run_coroutine_threadsafe este modul sigur de a comunica
                # intre un thread obisnuit si un event loop asyncio
                asyncio.run_coroutine_threadsafe(queue.put(cmd), loop)
        except EOFError:
            # EOFError apare cand terminalul este inchis (ex: Ctrl+D)
            break

async def main():
    print("=== Client/Worker - Motor Executie Distribuit ===")
    print("Pasi recomandati pentru start:")
    print("1. connect server 8506")
    print("2. add_script ./scripts/reverse.py")
    print("3. publish my_pipe reverse.py")
    print("4. execute my_pipe test.txt\n")

    loop = asyncio.get_running_loop()

    # Coada asyncio folosita ca pod intre thread-ul UI si event loop-ul de retea
    cmd_queue = asyncio.Queue()

    # Pornim thread-ul de UI ca daemon, astfel incat sa se opreasca automat
    # cand procesul principal se termina
    ui_thread = threading.Thread(target=ui_thread_func, args=(loop, cmd_queue), daemon=True)
    ui_thread.start()

    # Procesam comenzile venite din coada pana la exit
    await process_user_commands(cmd_queue)

if __name__ == '__main__':
    asyncio.run(main())
