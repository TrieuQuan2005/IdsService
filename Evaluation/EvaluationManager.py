from BinaryMetrics import BinaryMetric
from MultiClassMetrics import MultiClassMetric
from SystemMetrics import SystemMetric

class EvaluationManager:

    def __init__(self):

        # Binary layer
        self.host_bin = BinaryMetric("Host Binary")
        self.flow_bin = BinaryMetric("Flow Binary")

        # Multi layer
        self.host_multi = MultiClassMetric("Host Multi")
        self.flow_multi = MultiClassMetric("Flow Multi")

        # Hybrid system
        self.system = SystemMetric("Hybrid System")

        self.enabled = True   # cho phép bật/tắt evaluation

    # Update Binary Metrics
    def update_binary(self, y_true, host_pred, flow_pred):
        if not self.enabled:
            return

        self.host_bin.update(y_true, host_pred)
        self.flow_bin.update(y_true, flow_pred)

    # Update Multi Metrics
    def update_multi(self, y_true_label, host_multi_pred=None, flow_multi_pred=None):
        if not self.enabled:
            return

        if host_multi_pred is not None:
            self.host_multi.update(y_true_label, host_multi_pred)

        if flow_multi_pred is not None:
            self.flow_multi.update(y_true_label, flow_multi_pred)

    # Update Hybrid System
    def update_system(self, y_true_binary, system_pred_binary):
        if not self.enabled:
            return

        self.system.update(y_true_binary, system_pred_binary)

    # Print Report
    def report(self):
        print("       EVALUATION REPORT      ")
        self.host_bin.report()
        self.flow_bin.report()
        self.host_multi.report()
        self.flow_multi.report()
        self.system.report()
        print("==============================\n")