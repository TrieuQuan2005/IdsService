import time
import numpy as np
from dataclasses import asdict
from collections import Counter

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

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
    FlowMultiModelOutput,
    HostMultiModelOutput
)

from RandomJungle.Preprocessor import Preprocessor
from DecisionFusion.DecisionFusion import DecisionFusion

from RandomJungle.Models.RfHostBin import RfHostBin
from RandomJungle.Models.RfFlowBin import RfFlowBin
from RandomJungle.Models.RfHostMulti import RfHostMulti
from RandomJungle.Models.RfFlowMulti import RfFlowMulti


class Evaluation:

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

        # Network Config
        self.LOCAL_IP = {"192.168.1.78"}
        self.IFACE = "Wi-Fi"

        self.capture = PacketCaptureService(self.IFACE, 10000)
        self.parser = PacketParserService(self.LOCAL_IP)

        # Flow Pipeline
        self.flow_table = FlowTableService(flow_timeout=30)
        self.flow_window = FlowSlidingWindowService(window_size=10)
        self.flow_extractor = FlowFeatureExtractService(window_size=10)

        # Host Pipeline
        self.host_behavior = HostBehaviorService(host_timeout=30)
        self.host_window = HostSlidingWindowService(window_size=10)
        self.host_extractor = HostFeatureExtractService(window_size=10)

        # Session Configuration
        self.session_label = "DOS"  # hoặc BENIGN
        self.evaluation_duration = 60  # giây

        self.sample_count = 0
        self.start_time = None


        # Reader
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

        # METRICS STORAGE
        self.y_true = []
        self.y_pred = []

        print("IDS Ready.\n")


    # HYBRID PREDICTION
    def predict_hybrid(self, host_features, flow_features):

        host_bin_f, flow_bin_f, host_multi_f, flow_multi_f = \
            self.preprocessor.transform(host_features, flow_features)

        host_bin_array = np.array(list(asdict(host_bin_f).values())).reshape(1, -1)
        flow_bin_array = np.array(list(asdict(flow_bin_f).values())).reshape(1, -1)
        host_multi_array = np.array(list(asdict(host_multi_f).values())).reshape(1, -1)
        flow_multi_array = np.array(list(asdict(flow_multi_f).values())).reshape(1, -1)

        host_bin_output = BinaryModelOutput.from_proba(
            self.host_bin.predict_proba(host_bin_array)[0]
        )

        flow_bin_output = BinaryModelOutput.from_proba(
            self.flow_bin.predict_proba(flow_bin_array)[0]
        )

        host_multi_output = None
        flow_multi_output = None

        if host_bin_output.label.value == 1 or flow_bin_output.label.value == 1:
            host_multi_output = HostMultiModelOutput.from_proba(
                self.host_multi.predict_proba(host_multi_array)[0],
                self.host_multi.model.classes_
            )

            flow_multi_output = FlowMultiModelOutput.from_proba(
                self.flow_multi.predict_proba(flow_multi_array)[0]
            )

        final_label = self.fusion.fuse(
            host_bin_output=host_bin_output,
            flow_bin_output=flow_bin_output,
            host_multi_output=host_multi_output,
            flow_multi_output=flow_multi_output
        )

        confidence = max(
            host_bin_output.confidence,
            flow_bin_output.confidence
        )

        return final_label, confidence

    def print_metrics(self):

        if self.sample_count == 0:
            print("No samples collected.")
            return

        print("\n========== SESSION RESULT ==========")
        print(f"Total Samples: {self.sample_count}")

        # Binary conversion
        y_true_bin = [0 if y == "BENIGN" else 1 for y in self.y_true]
        y_pred_bin = [0 if y == "BENIGN" else 1 for y in self.y_pred]

        acc = accuracy_score(y_true_bin, y_pred_bin)
        pre = precision_score(y_true_bin, y_pred_bin)
        rec = recall_score(y_true_bin, y_pred_bin)
        f1 = f1_score(y_true_bin, y_pred_bin)

        print(f"Accuracy : {acc:.4f}")
        print(f"Precision: {pre:.4f}")
        print(f"Recall   : {rec:.4f}")
        print(f"F1 Score : {f1:.4f}")

        print("\nConfusion Matrix:")
        print(confusion_matrix(y_true_bin, y_pred_bin))

        print("=====================================\n")

    # MAIN LOOP
    def run(self):

        print("🟢 Evaluation Started")
        print(f"Session Label: {self.session_label}")
        print(f"Duration: {self.evaluation_duration}s\n")

        self.capture.start()
        self.start_time = time.time()

        while True:

            # Dừng khi hết thời gian
            if time.time() - self.start_time >= self.evaluation_duration:
                print("\nEvaluation Finished.")
                self.print_metrics()
                break

            try:
                result = self.reader.read()

                if result is None:
                    continue

                if len(result) == 3:
                    host_features, flow_features, true_label = result
                else:
                    host_features, flow_features = result
                    true_label = self.session_label  # fallback theo config

                final_label, confidence = self.predict_hybrid(
                    host_features,
                    flow_features
                )

                # Lưu dữ liệu đánh giá
                self.y_true.append(true_label.upper())
                self.y_pred.append(final_label.name.upper())

                self.sample_count += 1

            except Exception as e:
                print("Error:", e)


if __name__ == "__main__":
    app = Evaluation()
    app.run()