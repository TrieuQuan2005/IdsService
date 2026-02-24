import csv
import os
import time
from dataclasses import asdict

from NetworkReader.Services.PacketCaptureService import PacketCaptureService
from NetworkReader.Services.PacketParserService import PacketParserService
from NetworkReader.Data.ValueObjects.PacketMeta import PacketMeta

from NetworkReader.Services.FlowBased.FlowTableService import FlowTableService
from NetworkReader.Services.FlowBased.FlowSlidingWindowService import FlowSlidingWindowService
from NetworkReader.Services.FlowBased.FlowFeatureExtractService import FlowFeatureExtractService

from NetworkReader.Services.HostBased.HostBehaviorService import HostBehaviorService
from NetworkReader.Services.HostBased.HostSlidingWindowService import HostSlidingWindowService
from NetworkReader.Services.HostBased.HostFeatureExtractService import HostFeatureExtractService


# =========================================================
# CSV WRITER
# =========================================================
class DatasetWriter:
    def __init__(self, flow_path: str, host_path: str):
        self.flow_path = flow_path
        self.host_path = host_path

        self.flow_file = open(flow_path, "a", newline="", encoding="utf-8")
        self.host_file = open(host_path, "a", newline="", encoding="utf-8")

        self.flow_writer = None
        self.host_writer = None

    # ---------- FLOW ----------
    def write_flow(self, feature):
        data = asdict(feature)

        # flatten FlowKey
        fk = data.pop("flow_key")
        if isinstance(fk, dict):
            data["src_ip"] = fk["src_ip"]
            data["dst_ip"] = fk["dst_ip"]
            data["dst_port"] = fk["dst_port"]
            data["protocol"] = fk["protocol"]
            data["direction"] = fk["direction"]
        else:
            data["src_ip"] = fk.src_ip
            data["dst_ip"] = fk.dst_ip
            data["dst_port"] = fk.dst_port
            data["protocol"] = fk.protocol
            data["direction"] = fk.direction

        if self.flow_writer is None:
            self.flow_writer = csv.DictWriter(self.flow_file, fieldnames=data.keys())
            if os.stat(self.flow_path).st_size == 0:
                self.flow_writer.writeheader()

        self.flow_writer.writerow(data)
        self.flow_file.flush()

    # ---------- HOST ----------
    def write_host(self, feature):
        data = asdict(feature)

        if self.host_writer is None:
            self.host_writer = csv.DictWriter(self.host_file, fieldnames=data.keys())
            if os.stat(self.host_path).st_size == 0:
                self.host_writer.writeheader()

        self.host_writer.writerow(data)
        self.host_file.flush()

    def close(self):
        self.flow_file.close()
        self.host_file.close()


# =========================================================
# PIPELINE
# =========================================================
class NetworkPipeline:
    def __init__(
        self,
        _capture: PacketCaptureService,
        _parser: PacketParserService,
        _flow_table: FlowTableService,
        _flow_window: FlowSlidingWindowService,
        _flow_extractor: FlowFeatureExtractService,
        _host_behavior: HostBehaviorService,
        _host_window: HostSlidingWindowService,
        _host_extractor: HostFeatureExtractService,
    ):
        self.capture = capture
        self.parser = parser

        # Flow path
        self.flow_table = flow_table
        self.flow_window = flow_window
        self.flow_extractor = flow_extractor

        # Host path
        self.host_behavior = host_behavior
        self.host_window = host_window
        self.host_extractor = host_extractor

        # CSV writer
        self.writer = DatasetWriter(
            flow_path="flowBenignGame.csv",
            host_path="host_BenignGame.csv"
        )

    # =====================================================
    def run(self, duration_seconds: int = 20):
        self.capture.start()
        print(f"Capture started... Recording for {duration_seconds}s")
        print("Press Ctrl+C to stop early\n")

        start_time = time.time()
        last_heartbeat = start_time

        packet_counter = 0
        flow_counter = 0
        host_counter = 0

        try:
            while True:
                now = time.time()

                # ===== AUTO STOP =====
                if now - start_time >= duration_seconds:
                    print("\n⏱ Auto stop reached!")
                    break

                # ===== HEARTBEAT =====
                if now - last_heartbeat >= 2:
                    print(".", end="", flush=True)
                    last_heartbeat = now

                item = self.capture.next_packet(timeout=1.0)
                if item is None:
                    continue

                packet_counter += 1
                raw_bytes, ts = item

                pkt: PacketMeta | None = self.parser.parse(raw_bytes, ts)
                if pkt is None:
                    continue

                # update states
                self.flow_table.on_packet(pkt)
                self.host_behavior.on_packet(pkt)

                # ---------- FLOW ----------
                flow_snaps = self.flow_window.process_packet(pkt)
                for snap in flow_snaps:
                    feature = self.flow_extractor.extract(snap)
                    self.writer.write_flow(feature)
                    flow_counter += 1

                # ---------- HOST ----------
                host_snaps = self.host_window.process_packet(pkt)
                for snap in host_snaps:
                    feature = self.host_extractor.extract(snap)
                    self.writer.write_host(feature)
                    host_counter += 1

        except KeyboardInterrupt:
            print("\nManual stop!")

        finally:
            self.capture.stop()
            self.writer.close()

            print("\n===== SUMMARY =====")
            print("Packets captured:", packet_counter)
            print("Flow features:", flow_counter)
            print("Host features:", host_counter)
            print("Dataset saved successfully!")


# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":

    LOCAL_IP = {"192.168.1.165"}   # chỉnh lại nếu IP đổi
    IFACE = "Ethernet"             # đổi nếu dùng WiFi

    # I/O
    capture = PacketCaptureService(IFACE, 10000)
    parser = PacketParserService(LOCAL_IP)

    # Flow pipeline
    flow_table = FlowTableService(flow_timeout=30)
    flow_window = FlowSlidingWindowService(window_size=10)
    flow_extractor = FlowFeatureExtractService(window_size=10)

    # Host pipeline
    host_behavior = HostBehaviorService(host_timeout=30)
    host_window = HostSlidingWindowService(window_size=10)
    host_extractor = HostFeatureExtractService(window_size=10)

    pipe = NetworkPipeline(
        capture,
        parser,
        flow_table,
        flow_window,
        flow_extractor,
        host_behavior,
        host_window,
        host_extractor
    )

    pipe.run(900)
