from dataclasses import dataclass
from typing import Optional
from NetworkReader.Data.Enums.L4Protocol import L4Protocol
from NetworkReader.Data.Enums.Direction import Direction


@dataclass(frozen=True, slots=True)
class PacketMeta:
    timestamp: float
    direction: Direction

    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    protocol: L4Protocol

    packet_size: int

    # TCP flags (None for UDP)
    syn: Optional[bool] = None
    ack: Optional[bool] = None
    rst: Optional[bool] = None
    fin: Optional[bool] = None
