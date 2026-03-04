import struct
import socket
from typing import Optional, Set

from NetworkReader.Data.Enums.L4Protocol import L4Protocol
from NetworkReader.Data.Enums.Direction import Direction
from NetworkReader.Data.ValueObjects.PacketMeta import PacketMeta
from NetworkReader.Services.PacketCaptureService import PacketCaptureService

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

        # WinDivert: raw_packet bắt đầu từ IPv4 header
        if len(raw_packet) < IP_MIN_HEADER_LEN:
            return None

        iph = struct.unpack(
            "!BBHHHBBH4s4s",
            raw_packet[:IP_MIN_HEADER_LEN]
        )

        version_ihl = iph[0]
        version = version_ihl >> 4
        if version != 4:
            return None

        ihl = (version_ihl & 0x0F) * 4
        total_length = iph[2]
        protocol = iph[6]

        # Drop fragmented packets
        flags_frag = iph[4]
        fragment_offset = flags_frag & 0x1FFF
        if fragment_offset != 0:
            return None

        if len(raw_packet) < ihl:
            return None

        src_ip = socket.inet_ntoa(iph[8])
        dst_ip = socket.inet_ntoa(iph[9])

        direction = self._resolve_direction(src_ip, dst_ip)
        if direction is None:
            return None

        packet_size = min(total_length, len(raw_packet))

        # ================= TCP =================
        if protocol == L4Protocol.TCP.value:

            tcp_start = ihl
            if len(raw_packet) < tcp_start + TCP_MIN_HEADER_LEN:
                return None

            tcph = struct.unpack(
                "!HHLLBBHHH",
                raw_packet[tcp_start:tcp_start + TCP_MIN_HEADER_LEN]
            )

            src_port = tcph[0]
            dst_port = tcph[1]

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

        # ================= UDP =================
        if protocol == L4Protocol.UDP.value:

            udp_start = ihl
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


def debug_dump_packet( raw_packet: bytes):
    print("\n========== PACKET DUMP ==========")
    print("Total raw length:", len(raw_packet))
    print("First 64 bytes:", raw_packet[:64].hex())

    if len(raw_packet) < 20:
        print("Too short for IPv4")
        return

    # IPv4 header
    version_ihl = raw_packet[0]
    version = version_ihl >> 4
    ihl = (version_ihl & 0x0F) * 4

    total_length = struct.unpack("!H", raw_packet[2:4])[0]
    protocol = raw_packet[9]
    src_ip = socket.inet_ntoa(raw_packet[12:16])
    dst_ip = socket.inet_ntoa(raw_packet[16:20])

    print("---- IPv4 ----")
    print("Version:", version)
    print("IHL:", ihl)
    print("Total Length:", total_length)
    print("Protocol:", protocol)
    print("Src IP:", src_ip)
    print("Dst IP:", dst_ip)

    if protocol == 6 and len(raw_packet) >= ihl + 20:
        tcp_start = ihl

        src_port, dst_port = struct.unpack(
            "!HH",
            raw_packet[tcp_start:tcp_start+4]
        )

        data_offset = (raw_packet[tcp_start + 12] >> 4) * 4
        flags = raw_packet[tcp_start + 13]

        print("---- TCP ----")
        print("TCP start offset:", tcp_start)
        print("Raw TCP header:", raw_packet[tcp_start:tcp_start + 20].hex())
        print("Src Port:", src_port)
        print("Dst Port:", dst_port)
        print("Data Offset:", data_offset)
        print("Flags byte (hex):", hex(flags))
        print("Byte[12]:", hex(raw_packet[tcp_start + 12]))
        print("Byte[13]:", hex(raw_packet[tcp_start + 13]))
        print("SYN:", bool(flags & 0x02))
        print("ACK:", bool(flags & 0x10))
        print("RST:", bool(flags & 0x04))
        print("FIN:", bool(flags & 0x01))

    print("=================================\n")
if __name__ == "__main__":
    capture = PacketCaptureService(filter_str="tcp.Syn == 1 and tcp.Ack == 0")
    capture.start()

    try:
        while True:
            pkt = capture.next_packet(timeout=5.0)
            if pkt is None:
                print("No packet received...")
                continue

            raw_bytes, ts = pkt
            debug_dump_packet(raw_bytes)


            break

    finally:
        capture.stop()