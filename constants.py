from enum import IntEnum

class OpCode(IntEnum):
    """
        Operation codes
    """
    Authentication = 1
    PlayerMovement = 2
    UserNotFound = 3
    SpawnPlayer = 4
    PlayerShoot = 5

class ClientPackets(IntEnum):
    Authentication = 1
    PlayerMovement = 2
    playerShoot = 3

