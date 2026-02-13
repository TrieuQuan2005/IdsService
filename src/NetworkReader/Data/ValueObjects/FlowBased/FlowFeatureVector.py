from dataclasses import dataclass
from NetworkReader.Data.ValueObjects.FlowBased.FlowKey import FlowKey

@dataclass(frozen=True, slots=True)
class FlowFeatureVector:
    # identity
    timestamp: float
    window_size: float
    flow_key: FlowKey

    # volume
    packet_count: int
    byte_count: int
    packets_per_second: float
    bytes_per_second: float

    # temporal
    flow_duration: float
    inter_arrival_mean: float
    inter_arrival_variance: float

    # direction
    forward_ratio: float

    # TCP behavior
    syn_ratio: float
    rst_ratio: float
