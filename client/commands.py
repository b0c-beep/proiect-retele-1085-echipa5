import os
import state
from protocol import send_message
from connection import connect_to_server

async def process_user_commands(queue):
    # Consumam comenzile tastate de utilizator din coada asyncio
    while True:
        cmd_line = await queue.get()
        parts = cmd_line.strip().split()
        if not parts:
            continue

        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == "add_script":
            # Adaugam un script local in lista noastra si anuntam serverul
            if len(args) != 1:
                print("Usage: add_script <path>")
                continue
            path = args[0]
            if not os.path.exists(path):
                print("Eroare: Fisierul nu exista!")
                continue
            name = os.path.basename(path)
            # Salvam calea absoluta ca sa nu depindem de directorul de lucru curent
            state.my_scripts[name] = os.path.abspath(path)
            print(f"Script adaugat local: {name} -> {state.my_scripts[name]}")

            # Daca suntem conectati, retrimitem lista completa de scripturi catre server
            if state.writer is not None:
                await send_message(state.writer, "REGISTER_SCRIPTS", scripts=list(state.my_scripts.keys()))
                print(f"Serverul a fost notificat de noul script: {name}")

        elif cmd == "connect":
            # Stabilim conexiunea TCP cu serverul
            if len(args) != 2:
                print("Usage: connect <ip> <port>")
                continue
            ip, port = args[0], int(args[1])
            await connect_to_server(ip, port)

        elif cmd == "publish":
            # Definim un pipeline pe server - o secventa de scripturi care ruleaza in lant
            if len(args) < 2:
                print("Usage: publish <nume_pipeline> <script1> <script2> ...")
                continue
            if state.writer is None:
                print("Nu esti conectat!")
                continue
            await send_message(state.writer, "PUBLISH_PIPELINE", name=args[0], scripts=args[1:])

        elif cmd == "delete":
            # Stergem un pipeline existent de pe server
            if len(args) != 1:
                print("Usage: delete <nume_pipeline>")
                continue
            if state.writer is None:
                print("Nu esti conectat!")
                continue
            await send_message(state.writer, "DELETE_PIPELINE", name=args[0])

        elif cmd == "execute":
            # Citim fisierul de intrare si il trimitem serverului pentru a rula pipeline-ul
            if len(args) != 2:
                print("Usage: execute <nume_pipeline> <fisier_intrare>")
                continue
            if state.writer is None:
                print("Nu esti conectat!")
                continue
            name = args[0]
            file_path = args[1]
            if not os.path.exists(file_path):
                print("Fisierul de intrare nu exista!")
                continue
            # Citim fisierul ca date binare - functioneaza si pentru imagini, arhive etc.
            with open(file_path, "rb") as f:
                data = f.read()
            await send_message(state.writer, "EXECUTE_PIPELINE", pipeline_name=name, payload=data)

        elif cmd == "create_file":
            # Comanda de ajutor: genereaza rapid un fisier text pentru testare
            if len(args) < 2:
                print("Usage: create_file <nume_fisier> <continut...>")
                continue
            file_name = args[0]
            content = " ".join(args[1:])
            with open(file_name, "w") as f:
                f.write(content)
            print(f"Fisier creat cu succes: '{file_name}' ({len(content)} bytes).")

        elif cmd == "clear":
            os.system("clear" if os.name != "nt" else "cls")

        elif cmd == "help":
            print("\n=== Comenzi Disponibile ===")
            print("  connect <ip> <port>                  - Conectare la server")
            print("  add_script <cale_fisier>             - Expune un script local in retea")
            print("  publish <nume_flux> <s1> <s2> ...    - Creeaza un pipeline de executie pe server")
            print("  delete <nume_flux>                   - Sterge un pipeline")
            print("  create_file <nume> <text...>         - Creeaza rapid un fisier test local pentru input")
            print("  execute <nume_flux> <fisier_intrare> - Executa fluxul cu datele tale")
            print("  clear                                - Curata ecranul terminalului")
            print("  help                                 - Afiseaza acest mesaj")
            print("  exit                                 - Inchide clientul/workerul\n")

        elif cmd == "exit":
            print("La revedere!")
            os._exit(0)

        else:
            print("Comanda necunoscuta. Tasteaza 'help' pentru lista de comenzi.")
