from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class HostFeatureVector:
    # identity
    timestamp: float
    window_size: float
    src_ip: str

    # traffic
    packet_count: int
    packets_per_second: float

    # fan-out
    unique_dst_ips: int
    unique_dst_ports: int
    port_entropy: float

    # connection behavior
    connection_attempts: int
    connections_per_second: float
    failed_connection_ratio: float

    # TCP behavior
    syn_ratio: float
    rst_ratio: float

    # temporal
    mean_flow_duration: float
