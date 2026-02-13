from enum import IntEnum

class BinaryLabel(IntEnum):
    BENIGN = 0
    ATTACK = 1

class HostAttackLabel(IntEnum):
    PORT_SCAN = 0
    BRUTE_FORCE = 1

class FlowAttackLabel(IntEnum):
    DOS = 0
    DDOS = 1

class FinalPredictionLabel(IntEnum):
    BENIGN = 0
    PORT_SCAN = 1
    BRUTE_FORCE = 2
    DOS = 3
    DDOS = 4
