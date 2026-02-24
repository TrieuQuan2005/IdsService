from dataclasses import dataclass, field

@dataclass(slots=True)
class HostStats:
    first_seen: float
    last_seen: float

    total_packets: int = 0
    total_bytes: int = 0

    dst_port_counter: dict[int, int] = field(default_factory=dict)

    # fan-out
    distinct_dst_ips: set[str] = field(default_factory=set)
    distinct_dst_ports: set[int] = field(default_factory=set)

    # connection attempts
    conn_attempts: int = 0
    failed_conn: int = 0

    # TCP behavior
    syn_count: int = 0
    syn_only_count: int = 0
    ack_count: int = 0
    rst_count: int = 0
    fin_count: int = 0

    # flow duration (online)
    flow_duration_mean: float = 0.0
    flow_duration_m2: float = 0.0
    flow_count: int = 0
