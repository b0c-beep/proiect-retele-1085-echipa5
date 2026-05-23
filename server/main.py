import asyncio
import logging
from handlers import handle_client
from cli import server_cli

# Configuram sistemul de logging ca sa vedem in terminal ce se intampla pe server
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Server")

async def main():
    # Pornim serverul TCP pe toate interfetele de retea, portul 8506.
    # Pentru fiecare client care se conecteaza, asyncio va apela automat handle_client().
    server = await asyncio.start_server(handle_client, '0.0.0.0', 8506)
    addr = server.sockets[0].getsockname()
    logger.info(f"Serverul a pornit pe {addr}")

    # Lansam consola de administrare in paralel cu serverul.
    # create_task() o ruleaza in fundal fara sa blocheze serverul TCP.
    asyncio.create_task(server_cli())

    # Tinem serverul activ la infinit pana cand procesul este oprit manual.
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
