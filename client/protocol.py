import asyncio
import json
import struct

# Protocolul de comunicare binar folosit intre client si server.
# Fiecare mesaj are doua parti:
#   1. Un header JSON cu metadatele (tipul comenzii, parametri, lungimea payload-ului)
#   2. Un payload binar optional (fisiere, date comprimate, text brut etc.)
#
# Structura unui mesaj pe socket:
#   [4 bytes]  - lungimea header-ului JSON, ca unsigned int in format big-endian
#   [N bytes]  - header-ul JSON codificat UTF-8
#   [M bytes]  - payload-ul binar (absent daca lungimea e 0)

async def send_message(writer: asyncio.StreamWriter, msg_type: str, payload: bytes = b'', **kwargs):
    # Construim header-ul cu tipul mesajului si lungimea payload-ului
    header_dict = {
        "type": msg_type,
        "payload_length": len(payload)
    }
    # Adaugam orice parametri extra transmisi ca keyword arguments (status, script_name, future_id etc.)
    header_dict.update(kwargs)

    # Serializam header-ul in JSON si il codificam ca bytes UTF-8
    header_json = json.dumps(header_dict).encode('utf-8')
    header_length = len(header_json)

    # Impachetam lungimea intr-un intreg de 4 bytes in format network (big-endian)
    # '!I' = Network Byte Order + Unsigned Int
    length_prefix = struct.pack('!I', header_length)

    # Scriem bucatile in buffer-ul socket-ului
    writer.write(length_prefix)
    writer.write(header_json)
    if payload:
        writer.write(payload)

    # Golim buffer-ul - ne asiguram ca datele au fost trimise efectiv pe retea
    await writer.drain()

async def receive_message(reader: asyncio.StreamReader):
    # Returneaza (header_dict, payload_bytes) sau arunca ConnectionError daca conexiunea cade
    try:
        # Pasul 1: citim primii 4 bytes ca sa aflam cat de mare e header-ul JSON
        length_prefix = await reader.readexactly(4)
        header_length = struct.unpack('!I', length_prefix)[0]

        # Pasul 2: citim exact atatia bytes cat are header-ul si il parsam ca JSON
        header_json = await reader.readexactly(header_length)
        header_dict = json.loads(header_json.decode('utf-8'))

        # Pasul 3: daca mesajul are un payload, il citim binar fara nicio modificare
        payload_length = header_dict.get("payload_length", 0)
        payload = b''
        if payload_length > 0:
            payload = await reader.readexactly(payload_length)

        return header_dict, payload

    except asyncio.IncompleteReadError:
        # readexactly() arunca aceasta exceptie cand conexiunea se inchide in mijlocul citirii
        raise ConnectionError("Connection closed by peer")
