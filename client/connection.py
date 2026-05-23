import asyncio
import state
from protocol import send_message

async def connect_to_server(ip, port):
    try:
        # Deschidem conexiunea TCP cu serverul
        state.reader, state.writer = await asyncio.open_connection(ip, port)
        print(f"Conectat la {ip}:{port}")

        # Imediat dupa conectare, anuntam serverul ce scripturi putem rula.
        # Daca lista e goala, serverul inregistreaza clientul fara niciun script.
        scripts_list = list(state.my_scripts.keys())
        await send_message(state.writer, "REGISTER_SCRIPTS", scripts=scripts_list)

        # Pornim ascultarea mesajelor venite de la server in fundal.
        # Importul se face aici (nu la nivel de modul) ca sa evitam importurile circulare
        # intre connection.py si handlers.py.
        from handlers import handle_server_messages
        asyncio.create_task(handle_server_messages())
    except Exception as e:
        print(f"Eroare conectare: {e}")
