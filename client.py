"""
    simulate movements
"""

import random
import attr
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado import gen
from tornado.iostream import StreamClosedError
from tornado.tcpclient import TCPClient
from tornado.tcpserver import TCPServer
from packet import PacketBuilder
from helper import Vector3
from constants import OpCode


async def start_process(stream):
    """
        Auth and send packets
    """
    _id = random.randint(900, 1000)
    username = "bot2"
    print(f"Bot started id: {_id}, name: bot")
    packet = PacketBuilder.build(OpCode.Authentication,{
        "id": _id,
        "username": username,
    })
    # send auth packet
    await stream.write(packet)
    # TODO: implement ack maybe ? but is tcp so nvm
    # send location pack every sec

    initial_pos = Vector3(0.0, 0.0, 5.0)
    while True:
        # move character along the X axis
        initial_pos.X += random.uniform(-2.0, 3)
        if initial_pos.X > 13 or initial_pos.X < -13:
            initial_pos.X -= 1

        movement_dict = attr.asdict(initial_pos)
        movement_pack = PacketBuilder.build(OpCode.PlayerMovement, {
            "id": _id,
            "X": initial_pos.X,
            "Y": initial_pos.Y,
            "Z": initial_pos.Z
        })
        print("init", initial_pos)
        print("Bot location pack", movement_pack)
        await stream.write(movement_pack)
        await gen.sleep(1)




async def run_bot():
    """
        Setup a bot
    """

    stream = await TCPClient().connect("127.0.0.1", 8888)
    await start_process(stream)


if __name__ == '__main__':
    try:
        IOLoop.instance().run_sync(run_bot)
    except KeyboardInterrupt:
        pass

