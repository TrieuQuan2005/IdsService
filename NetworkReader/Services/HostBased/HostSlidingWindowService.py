from typing import Dict, List
import math
from collections import deque, defaultdict

from NetworkReader.Data.ValueObjects.HostBased.HostStats import HostStats
from NetworkReader.Data.ValueObjects.HostBased.HostSlidingWindowSnapshot import HostSlidingWindowSnapshot
from NetworkReader.Data.ValueObjects.PacketMeta import PacketMeta


class HostSlidingWindowService:
    """
    Sliding window per host IP (true sliding, giống FlowSlidingWindowService).

    Mỗi packet đến:
        1. Append vào deque host
        2. Remove packet quá hạn (window_size)
        3. Rebuild stats từ buffer hiện tại
        4. Emit snapshot realtime
    """

    def __init__(self, window_size: float):
        self.window_size = window_size
        self._buffers: Dict[str, deque[PacketMeta]] = {}

    # ================================
    # MAIN ENTRY
    # ================================
    def process_packet(self, pkt: PacketMeta) -> List[HostSlidingWindowSnapshot]:
        snapshots: List[HostSlidingWindowSnapshot] = []
        host_ip = pkt.src_ip
        ts = pkt.timestamp

        if host_ip not in self._buffers:
            self._buffers[host_ip] = deque()

        buffer = self._buffers[host_ip]
        buffer.append(pkt)

        # 🔥 remove packet hết hạn (sliding window)
        window_start = ts - self.window_size
        while buffer and buffer[0].timestamp < window_start:
            buffer.popleft()

        # rebuild stats từ buffer hiện tại
        stats = self._rebuild_stats(buffer, window_start, ts)

        snapshots.append(
            self._emit_snapshot(host_ip, stats, window_start, ts)
        )
        return snapshots

    # ================================
    # REBUILD STATS FROM BUFFER
    # ================================
    def _rebuild_stats(self, buffer: deque, window_start: float, window_end: float) -> HostStats:
        if not buffer:
            stats = HostStats(first_seen=window_start, last_seen=window_end)
            stats.dst_port_counter = defaultdict(int)
            stats.distinct_dst_ips = set()
            stats.distinct_dst_ports = set()
            return stats

        stats = HostStats(first_seen=buffer[0].timestamp, last_seen=buffer[-1].timestamp)
        stats.dst_port_counter = defaultdict(int)
        stats.distinct_dst_ips = set()
        stats.distinct_dst_ports = set()
        stats.conn_attempts = 0
        stats.syn_only_count = 0
        stats.failed_conn = 0
        stats.syn_count = 0
        stats.ack_count = 0
        stats.rst_count = 0
        stats.fin_count = 0
        stats.flow_count = 0
        stats.flow_duration_mean = 0.0
        stats.flow_duration_m2 = 0.0
        stats.total_packets = 0
        stats.total_bytes = 0

        for pkt in buffer:
            self._update_stats(stats, pkt)

        return stats

    # ================================
    # SNAPSHOT EMITTER
    # ================================
    def _emit_snapshot(self, host_ip: str, stats: HostStats, window_start: float, window_end: float) -> HostSlidingWindowSnapshot:
        duration = window_end - window_start
        return HostSlidingWindowSnapshot(
            src_ip=host_ip,

            window_start=window_start,
            window_end=window_end,
            window_duration=duration,

            packet_count=stats.total_packets,
            byte_count=stats.total_bytes,
            packets_per_sec=(stats.total_packets / duration if duration > 0 else 0.0),

            unique_dst_ips=len(stats.distinct_dst_ips),
            unique_dst_ports=len(stats.distinct_dst_ports),
            port_entropy=self._port_entropy(stats.dst_port_counter),

            connection_attempts=stats.conn_attempts,
            connection_rate=(stats.conn_attempts / duration if duration > 0 else 0.0),
            failed_connection_ratio=(stats.failed_conn / stats.conn_attempts if stats.conn_attempts > 0 else 0.0),

            syn_count=stats.syn_count,
            ack_count=stats.ack_count,
            rst_count=stats.rst_count,
            syn_only_ratio=(stats.syn_only_count / stats.syn_count if stats.syn_count > 0 else 0.0),

            mean_flow_duration=stats.flow_duration_mean,
        )

    # ================================
    # PORT ENTROPY
    # ================================
    @staticmethod
    def _port_entropy(port_counter: Dict[int, int]) -> float:
        total = sum(port_counter.values())
        if total == 0:
            return 0.0
        entropy = 0.0
        for cnt in port_counter.values():
            p = cnt / total
            entropy -= p * math.log2(p)
        return entropy

    # ================================
    # STATS UPDATE
    # ================================
    @staticmethod
    def _update_stats(stats: HostStats, pkt: PacketMeta) -> None:
        ts = pkt.timestamp
        stats.last_seen = ts
        stats.total_packets += 1
        stats.total_bytes += pkt.packet_size

        stats.distinct_dst_ips.add(pkt.dst_ip)
        stats.distinct_dst_ports.add(pkt.dst_port)
        stats.dst_port_counter[pkt.dst_port] += 1

        # connection attempts (SYN-only)
        if pkt.syn and not pkt.ack:
            stats.conn_attempts += 1
            stats.syn_only_count += 1

        # TCP flags
        if pkt.syn:
            stats.syn_count += 1
        if pkt.ack:
            stats.ack_count += 1
        if pkt.rst:
            stats.rst_count += 1
            if stats.syn_only_count > stats.failed_conn:
                stats.failed_conn += 1
        if pkt.fin:
            stats.fin_count += 1

        # flow duration (close-based heuristic)
        if pkt.fin or pkt.rst:
            duration = stats.last_seen - stats.first_seen
            stats.flow_count += 1
            diff = duration - stats.flow_duration_mean
            stats.flow_duration_mean += diff / stats.flow_count
            stats.flow_duration_m2 += diff * (duration - stats.flow_duration_mean)
