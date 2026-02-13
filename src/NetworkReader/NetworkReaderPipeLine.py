from Services.PacketCaptureService import PacketCaptureService
from Services.PacketParserService import PacketParserService
from Data.ValueObjects.PacketMeta import PacketMeta

from Services.FlowBased.FlowTableService import FlowTableService
from Services.FlowBased.FlowSlidingWindowService import FlowSlidingWindowService
from Services.FlowBased.FlowFeatureExtractService import FlowFeatureExtractService

from Services.HostBased.HostBehaviorService import HostBehaviorService
from Services.HostBased.HostSlidingWindowService import HostSlidingWindowService
from Services.HostBased.HostFeatureExtractService import HostFeatureExtractService


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
        # I/O
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

    def run(self):
        self.capture.start()
        print("Capture started... Press Ctrl+C to stop")

        try:
            while True:
                item = self.capture.next_packet(timeout=1.0)
                if item is None:
                    continue

                raw_bytes, ts = item

                pkt: PacketMeta | None = self.parser.parse(raw_bytes, ts)
                if pkt is None:
                    continue

                # update state
                self.flow_table.on_packet(pkt)
                self.host_behavior.on_packet(pkt)

                # flow pipeline
                flow_snaps = self.flow_window.process_packet(pkt)
                for snap in flow_snaps:
                    print(self.flow_extractor.extract(snap))

                # host pipeline
                host_snaps = self.host_window.process_packet(pkt)
                for snap in host_snaps:
                    print(self.host_extractor.extract(snap))



        except KeyboardInterrupt:
            print("Stopping capture...")

        finally:
            self.capture.stop()


if __name__ == "__main__":
    LOCAL_IP = {"192.168.1.165"}
    IFACE = "Ethernet"
    # IO
    capture = PacketCaptureService(IFACE, 10000)
    parser = PacketParserService(LOCAL_IP)

    # Flow path
    flow_table = FlowTableService(flow_timeout= 30)
    flow_window = FlowSlidingWindowService(window_size= 10)
    flow_extractor = FlowFeatureExtractService(window_size= 10)

    # Host path
    host_behavior = HostBehaviorService(host_timeout= 30)
    host_window = HostSlidingWindowService(window_size= 10)
    host_extractor = HostFeatureExtractService(window_size= 10)

    # Pipeline
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

    pipe.run()