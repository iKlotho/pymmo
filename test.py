from packet import packet, vector_packet, authentication_packet, PacketBuilder
from constants import OpCode
from helper import Vector3

def parse_some_data(bdata, expected: Vector3):
    resp = vector_packet.parse(bdata)
    print("DEBUG: parsed", resp)
    assert Vector3(resp.X, resp.Y, resp.Z) == expected

def get_opcode(bdata, expected):
    resp = packet.parse(bdata)
    print("resp", resp)
    assert resp.opcode == expected
    return resp

def parse_credentials(bdata, expected):
    resp = authentication_packet.parse(bdata)
    print("DEBUG: parsed", resp)

if __name__ == '__main__':
    byte = b'\x10\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\xea\xa71\xbf\x00\x00\xa0@\x99'
    pack = PacketBuilder.build(OpCode.PlayerMovement, {
        "X": 0.0,
        "Y": -0.7,
        "Z": 5.0,
    })
    assert pack == byte

    authdata = b'\x11\x00\x00\x00\x99\xaa\x01\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00qwe\xaa\x99'
    response = get_opcode(authdata, 1)
    if response.opcode == 1:
        parse_credentials(response.rest_data, None)
        assert False

    # parse_some_data(byte, Vector3(0.0, -0.7, 5.0))
    response = get_opcode(byte, 2)
    if response.opcode == 2: # vector
        parse_some_data(response.rest_data, Vector3(0.0, -0.7, 5.0))

