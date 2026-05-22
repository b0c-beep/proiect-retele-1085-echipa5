import asyncio
import logging
import os
import sys
import state

logger = logging.getLogger("Server")

async def server_cli():
    # Consola de administrare ruleaza in paralel cu serverul TCP.
    # Daca procesul nu este atasat la un terminal real (ex: rulat ca daemon),
    # nu are rost sa pornim consola interactiva.
    if not sys.stdin.isatty():
        return

    loop = asyncio.get_event_loop()
    print("=== Server CLI (Interactiv) ===")
    print("Tasteaza 'status' pentru starea retelei, sau 'help' pentru comenzi.")

    while True:
        try:
            # run_in_executor ruleaza input() pe un thread separat ca sa nu blocheze asyncio
            cmd = await loop.run_in_executor(None, input, "server> ")
            cmd = cmd.strip().lower()
            if not cmd:
                continue

            if cmd == "status":
                # Afisam un snapshot al starii interne a serverului in acel moment
                print("\n--- SERVER STATUS ---")
                print(f"Clienti conectati: {len(state.clients)}")
                for cid in state.clients:
                    print(f"  - {cid}")
                print(f"Scripturi inregistrate: {len(state.script_registry)}")
                for s, c_set in state.script_registry.items():
                    print(f"  - {s} (pe {len(c_set)} noduri: {', '.join(c_set)})")
                print(f"Fluxuri: {len(state.pipelines)}")
                for p, s_list in state.pipelines.items():
                    print(f"  - {p}: {' -> '.join(s_list)}")
                print("---------------------\n")

            elif cmd == "clear":
                os.system("clear" if os.name != "nt" else "cls")

            elif cmd == "help":
                print("\nComenzi disponibile:")
                print("  status - Afiseaza toti clientii, scripturile si fluxurile active")
                print("  clear  - Curata ecranul")
                print("  help   - Afiseaza acest mesaj")
                print("\nNota: Fisierele generate de executii sunt salvate in folderul 'output/'\n")
            else:
                print(f"Comanda necunoscuta: {cmd}. Tasteaza 'help'.")

        except EOFError:
            # Ctrl+D - iesim din consola
            break
        except Exception as e:
            logger.error(f"Eroare in CLI: {e}")
