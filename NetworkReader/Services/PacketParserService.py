import struct
import socket
from typing import Optional, Set

from NetworkReader.Data.Enums.L4Protocol import L4Protocol
from NetworkReader.Data.Enums.Direction import Direction
from NetworkReader.Data.ValueObjects.PacketMeta import PacketMeta


ETH_HEADER_LEN = 14
ETH_TYPE_IPV4 = 0x0800

IP_MIN_HEADER_LEN = 20
TCP_MIN_HEADER_LEN = 20
UDP_HEADER_LEN = 8


class PacketParserService:

    def __init__(self, local_ips: Set[str]):
        self._local_ips = local_ips



    def _resolve_direction(self, src_ip: str, dst_ip: str) -> Optional[Direction]:
        src_local = src_ip in self._local_ips
        dst_local = dst_ip in self._local_ips

        if src_local and not dst_local:
            return Direction.FORWARD
        if not src_local and dst_local:
            return Direction.BACKWARD

        return None


    def parse(self, raw_packet: bytes, timestamp: float) -> Optional[PacketMeta]:

        # [0;13] Ethernet Header
        if len(raw_packet) < ETH_HEADER_LEN:
            return None

        eth_type = struct.unpack("!H", raw_packet[12:14])[0]
        if eth_type != ETH_TYPE_IPV4:
            return None

        # [14;....] IPv4 Header
        ip_start = ETH_HEADER_LEN
        if len(raw_packet) < ip_start + IP_MIN_HEADER_LEN:
            return None

        iph = struct.unpack(
            "!BBHHHBBH4s4s",
            raw_packet[ip_start:ip_start + IP_MIN_HEADER_LEN]
        )

        version_ihl = iph[0]
        version = version_ihl >> 4
        if version != 4:
            return None

        ihl = (version_ihl & 0x0F) * 4
        total_length = iph[2]
        protocol = iph[6]

        # Drop fragmented packets (no reassembly)
        flags_frag = iph[4]
        fragment_offset = flags_frag & 0x1FFF
        if fragment_offset != 0:
            return None

        if len(raw_packet) < ip_start + ihl:
            return None

        src_ip = socket.inet_ntoa(iph[8])
        dst_ip = socket.inet_ntoa(iph[9])

        direction = self._resolve_direction(src_ip, dst_ip)
        if direction is None:
            return None

        # Clamp packet size to actual buffer length
        packet_size = min(total_length, len(raw_packet) - ip_start)

        # [...;...]TCP
        if protocol == L4Protocol.TCP.value:
            tcp_start = ip_start + ihl
            if len(raw_packet) < tcp_start + TCP_MIN_HEADER_LEN:
                return None

            tcph = struct.unpack(
                "!HHLLBBHHH",
                raw_packet[tcp_start:tcp_start + TCP_MIN_HEADER_LEN]
            )

            src_port = tcph[0]
            dst_port = tcph[1]

            # Normalize service port by direction
            flow_dst_port = (
                dst_port if direction == Direction.FORWARD else src_port
            )

            data_offset = (tcph[4] >> 4) * 4
            flags = tcph[5]

            if len(raw_packet) < tcp_start + data_offset:
                return None

            return PacketMeta(
                timestamp=timestamp,
                direction=direction,
                src_ip=src_ip,
                dst_ip=dst_ip,
                src_port=src_port,
                dst_port=flow_dst_port,
                protocol=L4Protocol.TCP,
                packet_size=packet_size,
                syn=bool(flags & 0x02),
                ack=bool(flags & 0x10),
                rst=bool(flags & 0x04),
                fin=bool(flags & 0x01),
            )

        # [...;...]UDP
        if protocol == L4Protocol.UDP.value:
            udp_start = ip_start + ihl
            if len(raw_packet) < udp_start + UDP_HEADER_LEN:
                return None

            udph = struct.unpack(
                "!HHHH",
                raw_packet[udp_start:udp_start + UDP_HEADER_LEN]
            )

            src_port = udph[0]
            dst_port = udph[1]

            flow_dst_port = (
                dst_port if direction == Direction.FORWARD else src_port
            )

            return PacketMeta(
                timestamp=timestamp,
                direction=direction,
                src_ip=src_ip,
                dst_ip=dst_ip,
                src_port=src_port,
                dst_port=flow_dst_port,
                protocol=L4Protocol.UDP,
                packet_size=packet_size,
                syn=None,
                ack=None,
                rst=None,
                fin=None,
            )

        return None
