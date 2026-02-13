from typing import Dict

from NetworkReader.Data.ValueObjects.PacketMeta import PacketMeta
from NetworkReader.Data.ValueObjects.FlowBased.FlowKey import FlowKey
from NetworkReader.Data.ValueObjects.FlowBased.FlowStats import FlowStats
from NetworkReader.Data.Enums.Direction import Direction
from NetworkReader.Data.Enums.L4Protocol import L4Protocol


class FlowTableService:
    def __init__(self, flow_timeout: float):
        self.flow_timeout = flow_timeout
        self._flows: Dict[FlowKey, FlowStats] = {}

    def on_packet(self, pkt: PacketMeta) -> None:
        flow_key = FlowKey(
            src_ip=pkt.src_ip,
            dst_ip=pkt.dst_ip,
            dst_port=pkt.dst_port,
            protocol=pkt.protocol,
            direction=pkt.direction,
        )

        ts = pkt.timestamp
        stats = self._flows.get(flow_key)

        if stats is None:
            stats = FlowStats(first_seen=ts, last_seen=ts)
            self._flows[flow_key] = stats

        self._update_stats(stats, pkt)

    def cleanup(self, now: float) -> None:
        expired = [
            fk for fk, stats in self._flows.items()
            if now - stats.last_seen > self.flow_timeout
        ]
        for fk in expired:
            del self._flows[fk]

    def get_active_flows(self) -> Dict[FlowKey, FlowStats]:
        # return shallow copy to protect internal state
        return dict(self._flows)

    @staticmethod
    def _update_stats(stats: FlowStats, pkt: PacketMeta) -> None:
        ts = pkt.timestamp

        stats.total_packets += 1
        stats.total_bytes += pkt.packet_size
        stats.last_seen = ts

        # direction
        if pkt.direction == Direction.FORWARD:
            stats.fwd_packets += 1
        else:
            stats.bwd_packets += 1

        # inter-arrival (Welford – chuẩn)
        if stats.last_pkt_ts is not None:
            delta = ts - stats.last_pkt_ts
            stats.inter_arrival_count += 1

            diff = delta - stats.inter_arrival_mean
            stats.inter_arrival_mean += diff / stats.inter_arrival_count
            stats.inter_arrival_m2 += diff * (delta - stats.inter_arrival_mean)

        stats.last_pkt_ts = ts

        # TCP behavior
        if pkt.protocol == L4Protocol.TCP:
            if pkt.syn:
                stats.syn_count += 1
            if pkt.ack:
                stats.ack_count += 1
            if pkt.rst:
                stats.rst_count += 1
            if pkt.fin:
                stats.fin_count += 1
