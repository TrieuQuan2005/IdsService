from NetworkReader.Data.ValueObjects.HostBased.HostSlidingWindowSnapshot import HostSlidingWindowSnapshot
from NetworkReader.Data.ValueObjects.HostBased.HostFeatureVector import HostFeatureVector


class HostFeatureExtractService:
    def __init__(self, window_size: float):
        self.window_size = window_size

    def extract(self, snap: HostSlidingWindowSnapshot) -> HostFeatureVector:
        syn_ratio = snap.syn_count / max(1, snap.packet_count)
        rst_ratio = snap.rst_count / max(1, snap.packet_count)

        return HostFeatureVector(
            # identity
            timestamp=snap.window_end,
            window_size=self.window_size,
            src_ip=snap.src_ip,

            # traffic
            packet_count=snap.packet_count,
            packets_per_second=snap.packets_per_sec,

            # fan-out
            unique_dst_ips=snap.unique_dst_ips,
            unique_dst_ports=snap.unique_dst_ports,
            port_entropy=snap.port_entropy,

            # connection behavior
            connection_attempts=snap.connection_attempts,
            connections_per_second=snap.connection_rate,
            failed_connection_ratio=snap.failed_connection_ratio,

            # TCP behavior
            syn_ratio=syn_ratio,
            rst_ratio=rst_ratio,

            # temporal
            mean_flow_duration=snap.mean_flow_duration,
        )


