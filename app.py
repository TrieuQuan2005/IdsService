import time
import numpy as np
from dataclasses import asdict
import os

from NetworkReader.Services.FlowBased.FlowFeatureExtractService import FlowFeatureExtractService
from NetworkReader.Services.FlowBased.FlowSlidingWindowService import FlowSlidingWindowService
from NetworkReader.Services.FlowBased.FlowTableService import FlowTableService

from NetworkReader.Services.HostBased.HostBehaviorService import HostBehaviorService
from NetworkReader.Services.HostBased.HostFeatureExtractService import HostFeatureExtractService
from NetworkReader.Services.HostBased.HostSlidingWindowService import HostSlidingWindowService

from NetworkReader.Services.PacketCaptureService import PacketCaptureService
from NetworkReader.Services.PacketParserService import PacketParserService

from NetworkReader.NetworkReaderPipeLine import NetworkReader
from RandomJungle.Data.Labels import FinalPredictionLabel, BinaryLabel

from RandomJungle.Data.ModelOutputs import (
    BinaryModelOutput,
    FlowMultiModelOutput, HostMultiModelOutput
)

from RandomJungle.Preprocessor import Preprocessor
from DecisionFusion.DecisionFusion import DecisionFusion

from RandomJungle.Models.RfHostBin import RfHostBin
from RandomJungle.Models.RfFlowBin import RfFlowBin
from RandomJungle.Models.RfHostMulti import RfHostMulti
from RandomJungle.Models.RfFlowMulti import RfFlowMulti


class IdsConsoleApp:

    def __init__(self):

        # Load ML Models
        self.host_bin = RfHostBin()
        self.flow_bin = RfFlowBin()
        self.host_multi = RfHostMulti()
        self.flow_multi = RfFlowMulti()

        self.host_bin.load("Train/hostBin.pkl")
        self.flow_bin.load("Train/flowBin.pkl")
        self.host_multi.load("Train/hostMulti.pkl")
        self.flow_multi.load("Train/flowMulti.pkl")

        # Check whether multi-class models are valid (trained with >=2 classes)
        self.host_multi_available = self._is_multi_model_valid(self.host_multi)
        self.flow_multi_available = self._is_multi_model_valid(self.flow_multi)

        if not self.host_multi_available:
            print("WARNING: host multi-class model appears to have <2 classes and will not be used. Retrain with host multi-class dataset.")
        if not self.flow_multi_available:
            print("WARNING: flow multi-class model appears to have <2 classes and will not be used. Retrain with flow multi-class dataset.")

        # Network Config
        self.LOCAL_IP = {"192.168.1.165"}
        self.IFACE = "Ethernet"

        self.capture = PacketCaptureService()
        self.parser = PacketParserService(self.LOCAL_IP)

        # Flow Pipeline
        self.flow_table = FlowTableService(flow_timeout=30)
        self.flow_window = FlowSlidingWindowService(window_size=10)
        self.flow_extractor = FlowFeatureExtractService(window_size=10)

        # Host Pipeline
        self.host_behavior = HostBehaviorService(host_timeout=30)
        self.host_window = HostSlidingWindowService(window_size=10)
        self.host_extractor = HostFeatureExtractService(window_size=10)

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

        print("IDS Ready.\n")

    def _is_multi_model_valid(self, model) -> bool:
        """Return True if the loaded sklearn model has at least 2 classes_."""
        try:
            classes = getattr(model.model, 'classes_', None)
            if classes is None:
                return False
            return len(classes) >= 2
        except Exception:
            return False

    def predict_hybrid(self, host_features, flow_features):

        # ---------- Preprocess ----------
        host_bin_f, flow_bin_f, host_multi_f, flow_multi_f = self.preprocessor.transform(host_features, flow_features)

        host_bin_array = np.array(list(asdict(host_bin_f).values())).reshape(1, -1)
        flow_bin_array = np.array(list(asdict(flow_bin_f).values())).reshape(1, -1)
        host_multi_array = np.array(list(asdict(host_multi_f).values())).reshape(1, -1)
        flow_multi_array = np.array(list(asdict(flow_multi_f).values())).reshape(1, -1)



        host_bin_output = BinaryModelOutput.from_proba(self.host_bin.predict_proba(host_bin_array)[0], self.host_bin.model.classes_)
        flow_bin_output = BinaryModelOutput.from_proba(self.flow_bin.predict_proba(flow_bin_array)[0],self.flow_bin.model.classes_)

        host_multi_output = None
        flow_multi_output = None

        # Only call multi-class models if binary says attack AND the multi models are actually available
        if host_bin_output.label == BinaryLabel.Attack:
            host_multi_output = HostMultiModelOutput.from_proba(self.host_multi.predict_proba(host_multi_array)[0],self.host_multi.model.classes_)

            print(host_features.syn_ratio)
            if host_multi_output.label.name != "BruteForce":
                if host_features.syn_ratio >= 0:
                    host_multi_output.label = FinalPredictionLabel.UdpScan
                if host_features.syn_ratio > 0.8:
                    host_multi_output.label = FinalPredictionLabel.FullScan
                if host_features.syn_ratio > 0.95:
                    host_multi_output.label = FinalPredictionLabel.SynScan

        if flow_bin_output.label == BinaryLabel.Attack:
            flow_multi_output = FlowMultiModelOutput.from_proba(self.flow_multi.predict_proba(flow_multi_array)[0], self.flow_multi.model.classes_)

            protocol = flow_features.protocol

            if flow_multi_output.label.name == "SynFlood" and protocol != 6:
                flow_multi_output.label = FinalPredictionLabel.UdpFlood


        final_label , confidence  = self.fusion.fuse(
            host_bin_output=host_bin_output,
            flow_bin_output=flow_bin_output,
            host_multi_output=host_multi_output,
            flow_multi_output=flow_multi_output
        )

        # ---------- Local file logging ----------
        try:
            log_dir = os.path.join("Logger", "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "predictions.txt")

            # Prepare feature vector strings (host_multi, flow_multi) — values comma-separated
            try:
                host_vec_vals = host_multi_array[0].tolist()
                host_vec_str = ",".join([str(x) for x in host_vec_vals])
            except Exception:
                host_vec_str = "None"

            try:
                flow_vec_vals = flow_multi_array[0].tolist()
                flow_vec_str = ",".join([str(x) for x in flow_vec_vals])
            except Exception:
                flow_vec_str = "None"

            # Model outputs formatting
            def fmt_output(out):
                if out is None:
                    return "None:0.0"
                return f"{out.label.name}:{out.confidence:.6f}"

            host_bin_s = fmt_output(host_bin_output)
            flow_bin_s = fmt_output(flow_bin_output)
            host_multi_s = fmt_output(host_multi_output)
            flow_multi_s = fmt_output(flow_multi_output)
            final_s = f"{final_label.name}:{confidence:.6f}"

            # Single-line record — fields separated by a single space as requested
            # Order: host_feature_vector flow_feature_vector host_bin flow_bin host_multi flow_multi final
            line = f"[{host_vec_str}] [{flow_vec_str}] {host_bin_s} {flow_bin_s} {host_multi_s} {flow_multi_s} {final_s}\n"

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception as e:
            # Non-fatal: don't break prediction on logging failure
            print("Logging error:", e)

        if final_label != FinalPredictionLabel.Benign:
            print( "Flow bin:", flow_bin_output.label.name, flow_bin_output.confidence)
            if flow_multi_output is not None:
                print("Flow Multi", flow_multi_output.label.name, flow_multi_output.confidence)
            else:
                print("Ko co tan cong o muc flow")
            print("Host Bin",host_bin_output.label.name, host_bin_output.confidence)
            if host_multi_output is not None:
                print("Host Multi", host_multi_output.label.name, host_multi_output.confidence)
            else:
                print("Ko co tan cong o muc host")
        return final_label, confidence

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

                final_label, confidence = self.predict_hybrid(
                    host_features,
                    flow_features
                )
                if final_label != FinalPredictionLabel.Benign:
                    print(
                        f"[{time.strftime('%H:%M:%S')}] "
                        f" {flow_features.flow_key} "
                        f" {host_features.src_ip}"
                        f"→ {final_label.name} "
                        f"(conf={confidence:.2f})"
                    )
                    print("\n")

            except KeyboardInterrupt:
                print("\nIDS Stopped.")
                break

            except Exception as e:
                print(e)
                break


if __name__ == "__main__":
    app = IdsConsoleApp()
    app.run()