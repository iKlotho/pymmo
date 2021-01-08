from tornado.tcpserver import TCPServer
import traceback
from tornado.iostream import StreamClosedError
from tornado import gen
import tornado.ioloop
from packet import PacketManager, PacketBuilder
from constants import OpCode
from helper import Vector3
import attr
import random
from datastorage import Users, User
from exceptions import UserNotFound


@attr.s
class Client:
    stream = attr.ib(repr=False)
    address = attr.ib(repr=False)
    authenticated = attr.ib(default=False)
    user: User = attr.ib(default=None)
    # _id = attr.ib(default=0)
    # username = attr.ib(default="")
    disconnected = attr.ib(default=False)

    async def start_coro(self, clients):
        """
        Start listening packets
        """
        while True:
            try:
                data = await self.stream.read_until(b"\xAA\x99")
                try:
                    package_manager = PacketManager(data)
                    if package_manager.opcode == OpCode.Authentication:
                        try:
                            self.user = users.get_user(package_manager.username)
                            self.authenticated = True
                            spawn_packet = PacketBuilder.build(OpCode.SpawnPlayer, self.user.user_asdict())
                            print("Spawn packet", spawn_packet)
                            # TODO: return online users
                            await clients.load_users_to_client(self)
                            await clients.broadcast_packet(self, spawn_packet)
                        except UserNotFound:
                            traceback.print_exc()
                            self.authenticated = False
                            error_packet = PacketBuilder.build(
                                OpCode.UserNotFound, {"errormsg": "No such user!"}
                            )
                            print(f"User {package_manager} not found {self.address}")
                            await self.stream.write(error_packet)
                    else:
                        if package_manager.opcode == OpCode.PlayerMovement:
                            if not self.authenticated or not self.user:
                                print(
                                    f"Client is not authenticated cant process movement {self.address}"
                                )
                                continue
                            new_position  = package_manager.player_position
                            # if self.user.player_position == new_position:
                            #     continue
                            # else:
                            self.user.player_position = new_position
                            packet = PacketBuilder.build(
                                OpCode.PlayerMovement,
                                {
                                    "id": self.user._id,
                                    "X": self.user.player_position.X,
                                    "Y": self.user.player_position.Y,
                                    "Z": self.user.player_position.Z,
                                },
                            )

                            await clients.broadcast_packet(self, packet)
                        elif package_manager.opcode == OpCode.PlayerShoot:
                            _position = package_manager.player_position
                            print("got the shoot packet", _position)
                            packet = PacketBuilder.build(
                                OpCode.PlayerShoot,
                                {
                                    "id": self.user._id,
                                    "X": _position.X,
                                    "Y": _position.Y,
                                    "Z": _position.Z,
                                },
                            )
                            await clients.broadcast_packet(self, packet)
                        else:
                            print("Unknown opcode? ", package_manager)

                    # print("client", self)
                except Exception as e:
                    traceback.print_exc()
                    print(f"error while parsing data {str(e)} - data {data}")
                # else:
                #     print("data", data)
            except StreamClosedError:
                self.disconnected = True
                clients.delete_player(self)
                break


@attr.s
class Clients:
    _players: list = attr.ib(default=[])

    def get_player_count(self):
        return len(self._players)

    def add_new_player(self, client: Client):
        self._players.append(client)

    def delete_player(self, client: Client):
        self._players.remove(client)

    def check_username_exists(self, username: str) -> bool:
        for player in self._players:
            if player.user.username == username:
                return True
        return False

    async def load_users_to_client(self, client):
        for player in self._players:
            if player.user and player != client:
                spawn_packet = PacketBuilder.build(OpCode.SpawnPlayer, player.user.user_asdict())
                await client.stream.write(spawn_packet)

    async def broadcast_packet(self, client, packet):
        """
            Send packet to users except self
        """
        for player in self._players:
            if player != client:
                print(f"packet sent to user {player.user}")
                await player.stream.write(packet)
        return

    async def broadcast_msg(self, msg):
        print(f"Sending {msg} to all clients {len(self.conns)}")
        for conn in self.conns:
            await conn.write(msg.encode("utf-8"))


clients_ref = Clients()


class MMOServer(TCPServer):
    conns = []

    async def handle_stream(self, stream, address):
        print(f"Client connected {address}")
        client = Client(stream, address)
        clients_ref.add_new_player(client)
        await client.start_coro(clients_ref)


def populate_users(users_ref: Users):
    """
    Populate users
    """
    users_ref.add_new_user(User(11, "Username:"))
    users_ref.add_new_user(User(22, "unity"))
    users_ref.add_new_user(User(33, "bot"))
    users_ref.add_new_user(User(43, "bot2"))
    users_ref.add_new_user(User(55, "bot3"))
    print("Users", users_ref._user_list)
    print("get", users_ref.get_user("Username:"))


users = Users()

if __name__ == "__main__":
    populate_users(users)
    server = MMOServer()
    server.listen(8888)
    tornado.ioloop.IOLoop.current().start()

"""
data_str = data.decode("utf-8")
if data_str.startswith("broadcast"):
    msg = data_str.split("broadcast ")[1]
    opcode = msg.split('-')[0]
    custom_msg = "USER_SPAWN"
    if opcode == "USER_SPAWN":
        custom_msg = "USER_SPAWN"
        # rest = msg.split('-')[1]
        # Z, Y, X = rest.split("|")
        # X = r
        X = 1.720723
        Y = 0.9399997
        Z = 5
        D = -1
    print("woop ", opcode)
    await self.broadcast_msg(custom_msg)
else:
    await stream.write(data)
"""
