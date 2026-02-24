from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class HostKey:
    src_ip: str
