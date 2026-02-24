from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True)
class FlowStats:
    first_seen: float
    last_seen: float

    total_packets: int = 0
    total_bytes: int = 0

    # inter-arrival stats (online)
    last_pkt_ts: float | None = None
    inter_arrival_mean: float = 0.0
    inter_arrival_m2: float = 0.0
    inter_arrival_count: int = 0

    # TCP flags
    syn_count: int = 0
    ack_count: int = 0
    rst_count: int = 0
    fin_count: int = 0

    # direction
    fwd_packets: int = 0
    bwd_packets: int = 0
