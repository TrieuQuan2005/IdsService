import os, sys
# Ensure project root is on sys.path for imports when running the test directly
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from NetworkReader.Data.ValueObjects.PacketMeta import PacketMeta
from NetworkReader.Data.Enums.Direction import Direction
from NetworkReader.Data.Enums.L4Protocol import L4Protocol
from NetworkReader.Services.HostBased.HostSlidingWindowService import HostSlidingWindowService


def main():
    svc = HostSlidingWindowService(window_size=10.0)
    base_ts = 1000.0
    attacker_ip = "10.0.0.5"
    victim_ip = "192.168.1.10"
    client_port = 40000

    print("Sending forward SYNs to many destination ports (simulating SynScan)")
    for i, port in enumerate(range(1000, 1010)):
        pkt = PacketMeta(
            timestamp=base_ts + i * 0.01,
            direction=Direction.FORWARD,
            src_ip=attacker_ip,
            src_port=client_port,
            dst_ip=victim_ip,
            dst_port=port,
            protocol=L4Protocol.TCP,
            packet_size=60,
            syn=True,
            ack=False,
            rst=False,
            fin=False,
        )
        snaps = svc.process_packet(pkt)
        if snaps:
            snap = snaps[-1]
            print(f"After pkt to port {port}: unique_dst_ports={snap.unique_dst_ports}, port_entropy={snap.port_entropy:.3f}")

    print("--- Now send a BACKWARD packet (simulated reply) to ensure BACKWARD handling")
    # Simulate a response packet coming back from victim to attacker (BACKWARD)
    # For BACKWARD direction PacketMeta.src_port should be the original destination port
    pkt_resp = PacketMeta(
        timestamp=base_ts + 1.0,
        direction=Direction.BACKWARD,
        src_ip=victim_ip,
        src_port=1000,  # original destination port
        dst_ip=attacker_ip,
        dst_port=client_port,
        protocol=L4Protocol.TCP,
        packet_size=60,
        syn=True,
        ack=True,
        rst=False,
        fin=False,
    )
    snaps = svc.process_packet(pkt_resp)
    if snaps:
        snap = snaps[-1]
        print(f"After BACKWARD pkt: unique_dst_ports={snap.unique_dst_ports}, port_entropy={snap.port_entropy:.3f}")


if __name__ == '__main__':
    main()

