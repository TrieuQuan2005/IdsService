from enum import IntEnum

class BinaryLabel(IntEnum):
    Benign = 0
    Attack = 1

class HostAttackLabel(IntEnum):
    SynScan = 0
    UdpScan = 1
    FullScan =2
    BruteForce = 3

class FlowAttackLabel(IntEnum):
    TcpFlood = 0
    UdpFlood = 1

class FinalPredictionLabel(IntEnum):
    Benign = 0

    TcpFlood = 1
    UdpFlood = 2

    SynScan = 3
    UdpScan = 4
    FullScan = 5
    BruteForce = 6

