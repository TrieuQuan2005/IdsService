import time
import numpy as np
from dataclasses import asdict

from NetworkReader.Services.FlowBased.FlowFeatureExtractService import FlowFeatureExtractService
from NetworkReader.Services.FlowBased.FlowSlidingWindowService import FlowSlidingWindowService
from NetworkReader.Services.FlowBased.FlowTableService import FlowTableService

from NetworkReader.Services.HostBased.HostBehaviorService import HostBehaviorService
from NetworkReader.Services.HostBased.HostFeatureExtractService import HostFeatureExtractService
from NetworkReader.Services.HostBased.HostSlidingWindowService import HostSlidingWindowService

from NetworkReader.Services.PacketCaptureService import PacketCaptureService
from NetworkReader.Services.PacketParserService import PacketParserService

from NetworkReader.NetworkReaderPipeLine import NetworkReader

from RandomJungle.Data.ModelOutputs import (
    BinaryModelOutput,
    FlowMultiModelOutput
)

from RandomJungle.Preprocessor import Preprocessor
from DecisionFusion.DecisionFusion import DecisionFusion

from RandomJungle.Models.RfHostBin import RfHostBin
from RandomJungle.Models.RfFlowBin import RfFlowBin
from RandomJungle.Models.RfHostMulti import RfHostMulti
from RandomJungle.Models.RfFlowMulti import RfFlowMulti


class IdsConsoleApp:

    def __init__(self):

        # ==============================
        # Load ML Models
        # ==============================
        self.host_bin = RfHostBin()
        self.flow_bin = RfFlowBin()
        self.host_multi = RfHostMulti()
        self.flow_multi = RfFlowMulti()

        self.host_bin.load("Train/hostBin.pkl")
        self.flow_bin.load("Train/flowBin.pkl")
        self.host_multi.load("Train/hostMulti.pkl")
        self.flow_multi.load("Train/flowMulti.pkl")

        # ==============================
        # Network Config
        # ==============================
        self.LOCAL_IP = {"192.168.1.165"}
        self.IFACE = "Ethernet"

        self.capture = PacketCaptureService(self.IFACE, 10000)
        self.parser = PacketParserService(self.LOCAL_IP)

        # ==============================
        # Flow Pipeline
        # ==============================
        self.flow_table = FlowTableService(flow_timeout=30)
        self.flow_window = FlowSlidingWindowService(window_size=10)
        self.flow_extractor = FlowFeatureExtractService(window_size=10)

        # ==============================
        # Host Pipeline
        # ==============================
        self.host_behavior = HostBehaviorService(host_timeout=30)
        self.host_window = HostSlidingWindowService(window_size=10)
        self.host_extractor = HostFeatureExtractService(window_size=10)

        # ==============================
        # Reader + Core
        # ==============================
        self.reader = NetworkReader(
            self.capture,
            self.parser,
            self.flow_table,
            self.flow_window,
            self.flow_extractor,
            self.host_behavior,
            self.host_window,
            self.host_extractor
        )

        self.preprocessor = Preprocessor()
        self.fusion = DecisionFusion()

        print("🚀 IDS Ready.\n")

    # ==========================================================
    # FLOW PREDICTION
    # ==========================================================
    def predict_flow(self, host_features, flow_features):

        # ---------- Preprocess ----------
        host_bin_f, flow_bin_f, host_multi_f, flow_multi_f = \
            self.preprocessor.transform(host_features, flow_features)

        flow_bin_array = np.array(
            list(asdict(flow_bin_f).values())
        ).reshape(1, -1)

        flow_multi_array = np.array(
            list(asdict(flow_multi_f).values())
        ).reshape(1, -1)

        # ---------- Binary Stage ----------
        bin_probs = self.flow_bin.model.predict_proba(flow_bin_array)[0]
        flow_bin_output = BinaryModelOutput.from_proba(bin_probs)

        flow_multi_output = None

        # ---------- Multi Stage ----------
        if flow_bin_output.label.value == 1:  # ATTACK
            multi_probs = self.flow_multi.model.predict_proba(flow_multi_array)[0]
            flow_multi_output = FlowMultiModelOutput.from_proba(multi_probs)

        # ---------- Fusion ----------
        final_label = self.fusion.fuse(
            host_bin=None,
            flow_bin=flow_bin_output,
            host_multi=None,
            flow_multi=flow_multi_output
        )

        return final_label, flow_bin_output.confidence

    # MAIN LOOP
    def run(self):

        print("🟢 Monitoring started...\n")
        self.capture.start()
        while True:
            try:
                result = self.reader.read()

                if result is None:
                    continue

                host_features, flow_features = result

                final_label, confidence = self.predict_flow(
                    host_features,
                    flow_features
                )

                print(
                    f"[{time.strftime('%H:%M:%S')}] "
                    f" {flow_features.flow_key} "
                    f" {host_features.src_ip}"
                    f"→ {final_label.name} "
                    f"(conf={confidence:.2f})"
                )

            except KeyboardInterrupt:
                print("\n🛑 IDS Stopped.")
                break

            except Exception as e:
                print("❌ Error:", e)


if __name__ == "__main__":
    app = IdsConsoleApp()
    app.run()