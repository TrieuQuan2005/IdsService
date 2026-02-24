from dataclasses import dataclass
from NetworkReader.Data.ValueObjects.FlowBased.FlowKey import FlowKey

@dataclass(frozen=True, slots=True)
class FlowSlidingWindowSnapshot:
    # identity
    flow_key: FlowKey

    # window
    window_start: float
    window_end: float
    window_duration: float

    # volume
    packet_count: int
    byte_count: int
    packets_per_sec: float
    bytes_per_sec: float

    # temporal
    flow_duration: float
    inter_arrival_mean: float
    inter_arrival_variance: float

    # TCP behavior
    syn_count: int
    ack_count: int
    rst_count: int
    fin_count: int

    syn_ratio: float
    rst_ratio: float
