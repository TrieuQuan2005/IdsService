from enum import IntEnum

class BinaryLabel(IntEnum):
    BENIGN = 0
    ATTACK = 1

class HostAttackLabel(IntEnum):
    PORT_SCAN = 0
    BRUTE_FORCE = 1

class FlowAttackLabel(IntEnum):
    TcpFlood = 0
    UdpFlood = 1

class FinalPredictionLabel(IntEnum):
    BENIGN = 0
    PORT_SCAN = 1
    BRUTE_FORCE = 2
    TcpFlood = 3
    UdpFlood = 4
