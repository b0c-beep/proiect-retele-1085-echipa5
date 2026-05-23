import os
import state
from protocol import receive_message, send_message
from executor import execute_local_script

async def handle_server_messages():
    # Aceasta corutina ruleaza in continuu in fundal dupa conectare.
    # Asculta orice mesaj trimis de server si reactioneaza corespunzator.
    while True:
        try:
            header, payload = await receive_message(state.reader)
        except ConnectionError:
            # Daca serverul cade sau conexiunea se intrerupe, oprim clientul
            print("\n[!] Conexiunea cu serverul s-a intrerupt.")
            os._exit(1)

        msg_type = header.get("type")

        if msg_type == "ACK":
            # Confirmare de la server pentru o operatie facuta (register, publish, delete)
            print(f"\n[SERVER] ACK: {header.get('message')}")
            print("client> ", end="", flush=True)

        elif msg_type == "PIPELINE_RESULT":
            # Serverul ne trimite rezultatul final al unui pipeline pe care l-am cerut
            status = header.get("status")
            if status == "ok":
                print(f"\n[SERVER] PIPELINE SUCCES! Am primit un fisier de {len(payload)} bytes.")
                # Salvam rezultatul binar pe disk
                with open("result.out", "wb") as f:
                    f.write(payload)
                print("[SERVER] Rezultatul a fost salvat in 'result.out'.")
            else:
                # Ceva a esuat in timpul executiei pipeline-ului
                print(f"\n[SERVER] PIPELINE EROARE: {header.get('message')}")
            print("client> ", end="", flush=True)

        elif msg_type == "EXECUTE_SCRIPT":
            # Serverul ne cere sa rulam un script local ca parte dintr-un pipeline.
            # Payload-ul contine datele de intrare pentru script.
            script_name = header.get("script_name")
            future_id = header.get("future_id")

            # Verificam ca scriptul cerut este inregistrat local
            if script_name not in state.my_scripts:
                await send_message(state.writer, "SCRIPT_RESULT", status="error", message="Script negasit local", future_id=future_id)
                continue

            script_path = state.my_scripts[script_name]

            # Rulam scriptul ca subproces si asteptam rezultatul
            success, out_data, err_msg = await execute_local_script(script_path, payload)

            # Trimitem rezultatul inapoi la server, cu acelasi future_id
            # ca serverul sa stie la care pas din pipeline corespunde
            if success:
                await send_message(state.writer, "SCRIPT_RESULT", status="ok", payload=out_data, future_id=future_id)
            else:
                await send_message(state.writer, "SCRIPT_RESULT", status="error", message=err_msg, future_id=future_id)
