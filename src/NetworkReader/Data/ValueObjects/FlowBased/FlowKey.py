from dataclasses import dataclass
from NetworkReader.Data.Enums.L4Protocol import L4Protocol
from NetworkReader.Data.Enums.Direction import Direction

@dataclass(frozen=True, slots=True)
class FlowKey:
    src_ip: str
    dst_ip: str
    dst_port: int
    protocol: L4Protocol
    direction: Direction

    def __str__(self) -> str:
        return f"{self.direction.name}: {self.src_ip} → {self.dst_ip}:{self.dst_port}/{self.protocol}"
