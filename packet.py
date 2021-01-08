"""
    Handle packet data
"""
import attr
import construct as cs
from helper import Vector3
from constants import OpCode

packet = cs.Struct(
    "head" / cs.Const(b"\x99\xAA"),
    "len" / cs.Int32sl,
    "opcode" / cs.Int32sl,
    # subsctract the 4 byte (opcode) + len 4 byte + len 4 id
    "rest_data" / cs.Bytes(cs.this.len - 8),
    "end" / cs.Const(b"\xAA\x99"),
)

vector_packet = cs.Struct(
    "X" / cs.Float32l, "Y" / cs.Float32l, "Z" / cs.Float32l
)

authentication_packet = cs.Struct(
    # "id" / cs.Int32sl,
    "username"
    / cs.PascalString(cs.Int32sl, "utf8"),
)

"""
    TODO: find a way to re user packet parts
"""
send_vector_packet = cs.Struct(
    "head" / cs.Const(b"\x99\xAA"),
    "len" / cs.Int32sl,
    "opcode" / cs.Int32sl,  # 4
    "id" / cs.Int32sl,  # 4
    "X" / cs.Float32l,  # 4
    "Y" / cs.Float32l,  # 4
    "Z" / cs.Float32l,  # 4
    "end" / cs.Const(b"\xAA\x99"),
)

send_authentication_packet = cs.Struct(
    "head" / cs.Const(b"\x99\xAA"),
    "len" / cs.Int32sl,
    "opcode" / cs.Int32sl,  # 4
    # "id" / cs.Int32sl, # 4
    "username" / cs.PascalString(cs.Int32sl, "utf8"),  # var
    "end" / cs.Const(b"\xAA\x99"),
)

send_auth_failed_packet = cs.Struct(
    "head" / cs.Const(b"\x99\xAA"),
    "len" / cs.Int32sl,
    "opcode" / cs.Int32sl,  # 4
    # "id" / cs.Int32sl, # 4
    "errormsg" / cs.PascalString(cs.Int32sl, "utf8"),  # var
    "end" / cs.Const(b"\xAA\x99"),
)

send_spawn_player_packet = cs.Struct(
    "head" / cs.Const(b"\x99\xAA"),
    "len" / cs.Int32sl,
    "opcode" / cs.Int32sl,  # 4
    "id" / cs.Int32sl, # 4
    "username" / cs.PascalString(cs.Int32sl, "utf8"),  # var
    "X" / cs.Float32l,  # 4
    "Y" / cs.Float32l,  # 4
    "Z" / cs.Float32l,  # 4
    "end" / cs.Const(b"\xAA\x99"),
)


@attr.s
class PacketBuilder(object):
    @staticmethod
    def build(opcode: OpCode, data: dict):

        if opcode == OpCode.PlayerMovement:
            # vector_packed = vector_packet.build(data)
            return send_vector_packet.build(
                {
                    "len": 24,
                    "opcode": opcode,
                    "id": data["id"],
                    "X": float(data["X"]),
                    "Y": float(data["Y"]),
                    "Z": float(data["Z"]),
                }
            )

        if opcode == OpCode.Authentication:
            username_length = len(data["username"])
            return send_authentication_packet.build(
                {
                    # opcode(4) + stringlenint(4) + username_length(4vyte)
                    "len": 8 +  4 + username_length,  # 16 byte
                    "opcode": opcode,
                    # "id": data["id"],
                    "username": data["username"],
                }
            )

        if opcode == OpCode.UserNotFound:
            errormsg_length = len(data["errormsg"])
            return send_auth_failed_packet.build(
                {
                    # opcode(4) + id(4) + stringlenint(4) + username_length
                    "len": 8 + 4 + errormsg_length,  # 16 byte
                    "opcode": opcode,
                    # "id": data["id"],
                    "errormsg": data["errormsg"],
                }
            )

        if opcode == OpCode.SpawnPlayer:
            """
                Pascal string will build 4 + len(str) bytes
                PascalString.build("qwe") -> \x03\x00\x00\x00qwe
            """
            username_length = len(data["username"])
            pascal_len = 4 + username_length
            # len + opcode + id + pascal + x + y + z
            total_len = 4 + 4 + 4 + pascal_len + 4 + 4 + 4
            player_position = data["player_position"]
            print("data", data, "len", total_len)

            return send_spawn_player_packet.build(
                {
                    "len": total_len,
                    "opcode": opcode,
                    "id": data["_id"],
                    "username": data["username"],
                    "X": float(player_position["X"]),
                    "Y": float(player_position["Y"]),
                    "Z": float(player_position["Z"]),
                }
            )

        if opcode == OpCode.PlayerShoot:
            # vector_packed = vector_packet.build(data)
            return send_vector_packet.build(
                {
                    "len": 24,
                    "opcode": opcode,
                    "id": data["id"],
                    "X": float(data["X"]),
                    "Y": float(data["Y"]),
                    "Z": float(data["Z"]),
                }
            )


@attr.s
class PacketManager(object):
    data = attr.ib(repr=False)
    parsed_data = attr.ib(default=None, repr=False)
    opcode = attr.ib(default=0)
    user_id = attr.ib(default="")
    username = attr.ib(default="")
    player_position = attr.ib(default=Vector3(0.0, 0.0, 0.0))

    def __attrs_post_init__(self):
        self.parsed_data = packet.parse(self.data)
        self.opcode = OpCode(self.parsed_data.opcode)
        if self.opcode == OpCode.PlayerMovement:
            self.player_position = self.get_vector3(self.parsed_data.rest_data)
        if self.opcode == OpCode.PlayerShoot:
            self.player_position = self.get_vector3(self.parsed_data.rest_data)
        elif self.opcode == OpCode.Authentication:
            self.populate_user(self.parsed_data.rest_data)

    def populate_user(self, bdata) -> Vector3:
        """
        Set user data from packet
        """
        parsed = authentication_packet.parse(bdata)
        self.username = parsed.username

    def get_vector3(self, bdata) -> Vector3:
        """
        TODO: add annotation
        """
        parsed = vector_packet.parse(bdata)
        return Vector3(parsed.X, parsed.Y, parsed.Z)
