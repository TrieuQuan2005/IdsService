from typing import Dict, List
from collections import deque

from NetworkReader.Data.ValueObjects.FlowBased.FlowKey import FlowKey
from NetworkReader.Data.ValueObjects.FlowBased.FlowStats import FlowStats
from NetworkReader.Data.ValueObjects.FlowBased.FlowSlidingWindowSnapshot import (
    FlowSlidingWindowSnapshot
)
from NetworkReader.Data.ValueObjects.PacketMeta import PacketMeta
from NetworkReader.Data.Enums.Direction import Direction


class FlowSlidingWindowService:
    """
    True sliding window implementation per FlowKey.

    Mỗi packet đến:
        1. Add vào deque
        2. Remove packet quá hạn
        3. Rebuild stats từ buffer hiện tại
        4. Emit snapshot realtime
    """

    def __init__(self, window_size: float):
        self.window_size = window_size
        self._buffers: Dict[FlowKey, deque[PacketMeta]] = {}
        self._last_emit_ts: Dict[FlowKey, float] = {}

    # ================================
    # MAIN ENTRY
    # ================================
    def process_packet(self, pkt: PacketMeta) -> List[FlowSlidingWindowSnapshot]:
        snapshots: List[FlowSlidingWindowSnapshot] = []

        flow_key = FlowKey(
            src_ip=pkt.src_ip,
            dst_ip=pkt.dst_ip,
            dst_port=pkt.dst_port,
            protocol=pkt.protocol,
            direction=pkt.direction,
        )

        ts = pkt.timestamp

        # init buffer nếu flow mới
        if flow_key not in self._buffers:
            self._buffers[flow_key] = deque()
            self._last_emit_ts[flow_key] = ts

        buffer = self._buffers[flow_key]
        buffer.append(pkt)

        # 🔥 remove packet hết hạn (core sliding window)
        window_start = ts - self.window_size
        while buffer and buffer[0].timestamp < window_start:
            buffer.popleft()

        # rebuild stats từ buffer hiện tại
        stats = FlowStats(first_seen=buffer[0].timestamp, last_seen=ts)
        stats.last_pkt_ts = None  # VERY IMPORTANT for Welford replay

        for p in buffer:
            self._update_stats(stats, p)

        snapshots.append(
            self._emit_snapshot_from_stats(
                flow_key=flow_key,
                stats=stats,
                window_start=window_start,
                window_end=ts,
            )
        )

        return snapshots

    # ================================
    # STATS UPDATE (reusable)
    # ================================
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

        # inter-arrival time (Welford)
        if stats.last_pkt_ts is not None:
            delta = ts - stats.last_pkt_ts
            stats.inter_arrival_count += 1

            if stats.inter_arrival_count == 1:
                stats.inter_arrival_mean = delta
                stats.inter_arrival_m2 = 0.0
            else:
                diff = delta - stats.inter_arrival_mean
                stats.inter_arrival_mean += diff / stats.inter_arrival_count
                stats.inter_arrival_m2 += diff * (delta - stats.inter_arrival_mean)

        stats.last_pkt_ts = ts

        # TCP flags
        if pkt.syn:
            stats.syn_count += 1
        if pkt.ack:
            stats.ack_count += 1
        if pkt.rst:
            stats.rst_count += 1
        if pkt.fin:
            stats.fin_count += 1

    # ================================
    # SNAPSHOT BUILDER
    # ================================
    def _emit_snapshot_from_stats(
        self,
        flow_key: FlowKey,
        stats: FlowStats,
        window_start: float,
        window_end: float,
    ) -> FlowSlidingWindowSnapshot:

        window_duration = window_end - window_start

        return FlowSlidingWindowSnapshot(
            flow_key=flow_key,
            window_start=window_start,
            window_end=window_end,
            window_duration=window_duration,

            packet_count=stats.total_packets,
            byte_count=stats.total_bytes,

            packets_per_sec=(
                stats.total_packets / window_duration
                if window_duration > 0 else 0.0
            ),
            bytes_per_sec=(
                stats.total_bytes / window_duration
                if window_duration > 0 else 0.0
            ),

            flow_duration=stats.last_seen - stats.first_seen,

            inter_arrival_mean=stats.inter_arrival_mean,
            inter_arrival_variance=(
                stats.inter_arrival_m2 / (stats.inter_arrival_count - 1)
                if stats.inter_arrival_count > 1 else 0.0
            ),

            syn_count=stats.syn_count,
            ack_count=stats.ack_count,
            rst_count=stats.rst_count,
            fin_count=stats.fin_count,

            syn_ratio=(
                stats.syn_count / stats.total_packets
                if stats.total_packets > 0 else 0.0
            ),
            rst_ratio=(
                stats.rst_count / stats.total_packets
                if stats.total_packets > 0 else 0.0
            ),
        )
