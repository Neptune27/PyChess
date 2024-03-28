import asyncio
import json
import uuid
from asyncio import StreamReader, StreamWriter
from random import randint

rooms = []


async def handle_client(reader: StreamReader, writer: StreamWriter):
    uid = uuid.uuid4()
    client_info = {
        "uid": uid,
        "writer": writer,
        "role": "p"
    }

    room_id = -1
    while True:
        try:
            request = (await reader.read(1024)).decode('utf8')
            if request == 'quit':
                break
            tokens = request.split("|")
            if tokens[0] == "join":
                rid = tokens[1]

                if room_id in rooms:
                    rooms[room_id].remove(client_info)

                room_id = int(rid)
                if len(rooms) != room_id:
                    rooms.append([])
                    room_id = len(rooms)

                rooms[room_id-1].append(client_info)
                print(f"Rooms: {rooms}")
                await send_to_other(uid, room_id, f"join|{client_info['role']}")
            elif tokens[0] == "rooms":
                room_infos = [(i, len(room)) for i, room in enumerate(rooms)]
                writer.write(f"room_info|{json.dumps(room_infos)}".encode('utf8'))
            else:
                await send_to_other(uid, room_id, request)
        except ConnectionResetError:
            break

    await send_to_other(uid, room_id, f"quit|{client_info['role']}")
    rooms[room_id-1].remove(client_info)
    if len(rooms[room_id-1]) == 0:
        rooms.pop(room_id-1)
    print(rooms)

    writer.close()


async def send_to_other(uid, room_id, message):
    for client_info in rooms[room_id-1]:
        if client_info['uid'] == uid:
            continue
        sender = client_info["writer"]
        sender.write(message.encode('utf8'))
        await sender.drain()


async def send_to_all(room_id, message):
    for client_info in rooms[room_id]:
        sender = client_info["writer"]
        sender.write(message.encode('utf8'))
        await sender.drain()


async def run_server():
    server = await asyncio.start_server(handle_client, '0.0.0.0', 9999)
    print("Server started")
    async with server:
        await server.serve_forever()


asyncio.run(run_server())
