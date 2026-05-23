import asyncio
import logging
import os
import state
from protocol import send_message

logger = logging.getLogger("Server")

async def run_pipeline(requester_id: str, pipeline_name: str, initial_payload: bytes):
    # Verificam ca clientul care a cerut executia mai este conectat
    requester_reader, requester_writer = state.clients.get(requester_id, (None, None))
    if not requester_writer:
        return

    scripts = state.pipelines[pipeline_name]
    # current_payload incepe cu fisierul trimis de client si se actualizeaza dupa fiecare pas
    current_payload = initial_payload

    os.makedirs("output", exist_ok=True)
    logger.info(f"Incepere executie pipeline '{pipeline_name}' ({len(scripts)} pasi) solicitat de {requester_id}")

    # Parcurgem scripturile din pipeline in ordine
    for i, script_name in enumerate(scripts):

        # Verificam ca exista cel putin un client activ care detine acest script
        if script_name not in state.script_registry or not state.script_registry[script_name]:
            msg = f"Eroare: Scriptul '{script_name}' (pasul {i+1}) nu este disponibil. Niciun client conectat nu il detine."
            logger.warning(msg)
            await send_message(requester_writer, "PIPELINE_RESULT", status="error", message=msg)
            return

        # Alegem primul client disponibil din multimea care detine scriptul
        target_client_id = next(iter(state.script_registry[script_name]))
        target_reader, target_writer = state.clients.get(target_client_id, (None, None))

        if not target_writer:
            # Clientul s-a deconectat exact intre verificare si trimitere
            msg = f"Eroare: Clientul tinta {target_client_id} pentru scriptul '{script_name}' s-a deconectat."
            logger.warning(msg)
            await send_message(requester_writer, "PIPELINE_RESULT", status="error", message=msg)
            return

        # Cream un Future si il salvam in pending_results.
        # Cand workerul raspunde cu SCRIPT_RESULT, handlers.py va rezolva acest Future
        # si executia va continua de la linia "await asyncio.wait_for" de mai jos.
        future_id = f"{requester_id}_{pipeline_name}_{i}"
        fut = asyncio.get_running_loop().create_future()
        state.pending_results[future_id] = fut

        # Trimitem comanda de executie catre workerul ales, cu datele curente ca payload
        logger.info(f"Trimitem scriptul '{script_name}' catre {target_client_id}")
        await send_message(target_writer, "EXECUTE_SCRIPT", payload=current_payload, script_name=script_name, future_id=future_id)

        try:
            # Asteptam rezultatul maxim 30 de secunde
            result_header, result_payload = await asyncio.wait_for(fut, timeout=30.0)
        except asyncio.TimeoutError:
            msg = f"Eroare: Timeout la executia '{script_name}' pe {target_client_id}."
            logger.warning(msg)
            await send_message(requester_writer, "PIPELINE_RESULT", status="error", message=msg)
            return
        finally:
            # Curatam Future-ul din dictionar indiferent de rezultat
            if future_id in state.pending_results:
                del state.pending_results[future_id]

        # Verificam daca workerul a raportat o eroare in timpul rularii scriptului
        if result_header.get("status") == "error":
            msg = f"Eroare in timpul rularii '{script_name}': {result_header.get('message', '')}"
            logger.warning(msg)
            await send_message(requester_writer, "PIPELINE_RESULT", status="error", message=msg)
            return

        # Iesirea acestui pas devine intrarea urmatorului pas - asta e esenta unui pipeline
        current_payload = result_payload

        # Salvam rezultatul intermediar pe disk pentru debugging si audit
        step_file = f"output/{pipeline_name}_{requester_id}_pas{i+1}_{script_name}.out"
        with open(step_file, "wb") as f:
            f.write(current_payload)
        logger.info(f"Salvat rezultat intermediar: {step_file}")

    # Toate scripturile au rulat cu succes - salvam fisierul final
    final_file = f"output/{pipeline_name}_{requester_id}_final.out"
    with open(final_file, "wb") as f:
        f.write(current_payload)

    # Trimitem rezultatul final inapoi la clientul care a initiat executia
    logger.info(f"Pipeline '{pipeline_name}' finalizat. Salvare finala in '{final_file}'. Trimitem la client.")
    await send_message(requester_writer, "PIPELINE_RESULT", status="ok", payload=current_payload)
