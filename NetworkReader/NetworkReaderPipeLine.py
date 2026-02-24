from NetworkReader.Services.PacketCaptureService import PacketCaptureService
from NetworkReader.Services.PacketParserService import PacketParserService
from NetworkReader.Data.ValueObjects.PacketMeta import PacketMeta

from NetworkReader.Services.FlowBased.FlowTableService import FlowTableService
from NetworkReader.Services.FlowBased.FlowSlidingWindowService import FlowSlidingWindowService
from NetworkReader.Services.FlowBased.FlowFeatureExtractService import FlowFeatureExtractService

from NetworkReader.Services.HostBased.HostBehaviorService import HostBehaviorService
from NetworkReader.Services.HostBased.HostSlidingWindowService import HostSlidingWindowService
from NetworkReader.Services.HostBased.HostFeatureExtractService import HostFeatureExtractService


class NetworkReader:
    """
    Packet → Flow pipeline
           → Host pipeline

    read() sẽ:
    - Capture packet
    - Update state
    - Nếu có snapshot hoàn chỉnh → extract feature
    - Return (host_features, flow_features)
    """

    def __init__(
        self,
        capture: PacketCaptureService,
        parser: PacketParserService,
        flow_table: FlowTableService,
        flow_window: FlowSlidingWindowService,
        flow_extractor: FlowFeatureExtractService,
        host_behavior: HostBehaviorService,
        host_window: HostSlidingWindowService,
        host_extractor: HostFeatureExtractService,
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

    # MAIN ENTRY
    def read(self):

        packet = self.capture.next_packet(timeout=1.0)

        if packet is None:
            return None

        raw_bytes, ts = packet

        if raw_bytes is None:
            return None

        pkt = self.parser.parse(raw_bytes, ts)

        if pkt is None:
            return None

        # Update state
        self.flow_table.on_packet(pkt)
        self.host_behavior.on_packet(pkt)

        # Flow pipeline
        flow_features = None
        flow_snaps = self.flow_window.process_packet(pkt)
        if flow_snaps:
            snap = flow_snaps[-1]
            flow_features = self.flow_extractor.extract(snap)

        # Host pipeline
        host_features = None
        host_snaps = self.host_window.process_packet(pkt)
        if host_snaps:
            snap = host_snaps[-1]
            host_features = self.host_extractor.extract(snap)

        if flow_features is None and host_features is None:
            return None

        return host_features, flow_features