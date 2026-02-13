from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class HostSlidingWindowSnapshot:
    # identity
    src_ip: str

    # window
    window_start: float
    window_end: float
    window_duration: float

    # traffic
    packet_count: int
    byte_count: int
    packets_per_sec: float

    # fan-out
    unique_dst_ips: int
    unique_dst_ports: int
    port_entropy: float

    # connection behavior
    connection_attempts: int
    connection_rate: float
    failed_connection_ratio: float

    # TCP behavior
    syn_count: int
    ack_count: int
    rst_count: int
    syn_only_ratio: float

    # flow behavior
    mean_flow_duration: float
