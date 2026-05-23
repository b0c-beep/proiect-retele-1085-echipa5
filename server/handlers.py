import asyncio
import logging
import state
from protocol import receive_message, send_message
from pipeline import run_pipeline

logger = logging.getLogger("Server")

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    # Fiecare client care se conecteaza primeste un ID unic bazat pe contor global
    state.client_counter += 1
    client_id = f"client_{state.client_counter}"
    addr = writer.get_extra_info('peername')

    # Inregistram clientul in dictionarul global de clienti activi
    state.clients[client_id] = (reader, writer)
    logger.info(f"Client conectat: {client_id} de la {addr}")

    try:
        # Ascultam mesaje de la acest client la infinit
        while True:
            try:
                header, payload = await receive_message(reader)
            except ConnectionError:
                # Clientul s-a deconectat brusc, iesim din bucla
                break

            msg_type = header.get("type")

            if msg_type == "REGISTER_SCRIPTS":
                # Clientul ne spune ce scripturi poate rula.
                # Le adaugam in registru - mai multi clienti pot detine acelasi script.
                scripts = header.get("scripts", [])
                for s in scripts:
                    if s not in state.script_registry:
                        state.script_registry[s] = set()
                    state.script_registry[s].add(client_id)
                logger.info(f"[{client_id}] A inregistrat scripturile: {scripts}")
                await send_message(writer, "ACK", status="ok", message=f"Scripturi inregistrate: {len(scripts)}")

            elif msg_type == "PUBLISH_PIPELINE":
                # Clientul defineste un pipeline nou (sau suprascrie unul existent cu acelasi nume)
                name = header.get("name")
                scripts = header.get("scripts", [])
                if name and scripts:
                    state.pipelines[name] = scripts
                    logger.info(f"[{client_id}] A publicat pipeline-ul '{name}': {scripts}")
                    await send_message(writer, "ACK", status="ok", message=f"Pipeline '{name}' publicat.")
                else:
                    await send_message(writer, "ACK", status="error", message="Nume sau scripturi lipsa.")

            elif msg_type == "DELETE_PIPELINE":
                # Clientul cere stergerea unui pipeline din lista serverului
                name = header.get("name")
                if name in state.pipelines:
                    del state.pipelines[name]
                    logger.info(f"[{client_id}] A sters pipeline-ul '{name}'")
                    await send_message(writer, "ACK", status="ok", message=f"Pipeline '{name}' sters.")
                else:
                    await send_message(writer, "ACK", status="error", message="Pipeline inexistent.")

            elif msg_type == "EXECUTE_PIPELINE":
                # Clientul vrea sa ruleze un pipeline si trimite fisierul de intrare ca payload.
                # Lansam executia ca task separat ca sa nu blocam citirea altor mesaje de la client.
                name = header.get("pipeline_name")
                if name not in state.pipelines:
                    await send_message(writer, "PIPELINE_RESULT", status="error", message="Pipeline inexistent.")
                    continue
                asyncio.create_task(run_pipeline(client_id, name, payload))

            elif msg_type == "SCRIPT_RESULT":
                # Un worker a terminat de rulat un script si ne trimite rezultatul.
                # Gasim Future-ul care astepta acest rezultat si il rezolvam.
                future_id = header.get("future_id")
                if future_id in state.pending_results:
                    fut = state.pending_results[future_id]
                    if not fut.done():
                        fut.set_result((header, payload))
            else:
                logger.warning(f"Tip mesaj necunoscut primit de la {client_id}: {msg_type}")

    except Exception as e:
        logger.error(f"Eroare neasteptata pentru {client_id}: {e}")
    finally:
        # Curatare la deconectare - eliminam clientul din toate structurile de date
        logger.info(f"Client deconectat: {client_id}")
        if client_id in state.clients:
            del state.clients[client_id]

        # Scoatem clientul din registrul de scripturi.
        # Daca nimeni altcineva nu mai are scriptul, il stergem complet din registru.
        for s in list(state.script_registry.keys()):
            if client_id in state.script_registry[s]:
                state.script_registry[s].remove(client_id)
                if not state.script_registry[s]:
                    del state.script_registry[s]

        writer.close()
        await writer.wait_closed()
