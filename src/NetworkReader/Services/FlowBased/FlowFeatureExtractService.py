from NetworkReader.Data.ValueObjects.FlowBased.FlowSlidingWindowSnapshot import (
    FlowSlidingWindowSnapshot
)
from NetworkReader.Data.ValueObjects.FlowBased.FlowFeatureVector import FlowFeatureVector


class FlowFeatureExtractService:
    def __init__(self, window_size: float):
        self.window_size = window_size

    def extract(self, snapshot: FlowSlidingWindowSnapshot) -> FlowFeatureVector:
        total = snapshot.packet_count
        fwd = snapshot.fwd_packets if hasattr(snapshot, "fwd_packets") else total

        forward_ratio = fwd / total if total > 0 else 0.0

        return FlowFeatureVector(
            timestamp=snapshot.window_end,
            window_size=self.window_size,
            flow_key=snapshot.flow_key,

            packet_count=int(snapshot.packet_count),
            byte_count=int(snapshot.byte_count),
            packets_per_second=float(snapshot.packets_per_sec),
            bytes_per_second=float(snapshot.bytes_per_sec),

            flow_duration=float(snapshot.flow_duration),
            inter_arrival_mean=float(snapshot.inter_arrival_mean),
            inter_arrival_variance=float(snapshot.inter_arrival_variance),

            forward_ratio=forward_ratio,

            syn_ratio=float(snapshot.syn_ratio),
            rst_ratio=float(snapshot.rst_ratio),
        )
