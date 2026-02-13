from typing import Dict
from collections import defaultdict

from NetworkReader.Data.ValueObjects.PacketMeta import PacketMeta
from NetworkReader.Data.ValueObjects.HostBased.HostKey import HostKey
from NetworkReader.Data.ValueObjects.HostBased.HostStats import HostStats
from NetworkReader.Data.Enums.L4Protocol import L4Protocol


class HostBehaviorService:
    def __init__(self, host_timeout: float):
        self.host_timeout = host_timeout
        self._hosts: Dict[HostKey, HostStats] = {}

    def on_packet(self, packet: PacketMeta) -> None:
        key = HostKey(src_ip=packet.src_ip)
        now = packet.timestamp

        host = self._hosts.get(key)
        if host is None:
            host = HostStats(first_seen=now, last_seen=now)
            host.dst_port_counter = defaultdict(int)
            self._hosts[key] = host

        self._update_host(host, packet)

    def cleanup(self, now: float) -> None:
        expired = [
            hk for hk, h in self._hosts.items()
            if now - h.last_seen > self.host_timeout
        ]
        for hk in expired:
            del self._hosts[hk]

    def get_active_hosts(self) -> Dict[HostKey, HostStats]:
        return dict(self._hosts)

    @staticmethod
    def _update_host(host: HostStats, packet: PacketMeta) -> None:
        now = packet.timestamp
        host.last_seen = now

        host.total_packets += 1
        host.total_bytes += packet.packet_size

        host.distinct_dst_ips.add(packet.dst_ip)
        host.distinct_dst_ports.add(packet.dst_port)
        host.dst_port_counter[packet.dst_port] += 1

        if packet.protocol == L4Protocol.TCP:
            if packet.syn:
                host.syn_count += 1

            # SYN-only → connection attempt
            if packet.syn and not packet.ack:
                host.syn_only_count += 1
                host.conn_attempts += 1

            if packet.ack:
                host.ack_count += 1

            if packet.rst and not packet.ack:
                host.rst_count += 1
                if host.syn_only_count > host.failed_conn:
                    host.failed_conn += 1

            if packet.fin:
                host.fin_count += 1
