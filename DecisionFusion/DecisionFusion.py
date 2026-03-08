from RandomJungle.Data.Labels import (
    BinaryLabel,
    HostAttackLabel,
    FlowAttackLabel,
    FinalPredictionLabel,
)

from RandomJungle.Data.ModelOutputs import (
    HostMultiModelOutput,
    FlowMultiModelOutput,
)


class DecisionFusion:

    def fuse(
            self,
            host_bin_output,
            flow_bin_output,
            host_multi_output=None,
            flow_multi_output=None,
    ):

        # Both benign
        if (host_bin_output.label == BinaryLabel.Benign and
                flow_bin_output.label == BinaryLabel.Benign):
            return FinalPredictionLabel.Benign, 1.0

        candidates = []

        # Flow attack
        if flow_bin_output.label == BinaryLabel.Attack and flow_multi_output is not None:
            candidates.append(
                (self._map_to_final(flow_multi_output), flow_multi_output.confidence)
            )

        # Host attack
        if host_bin_output.label == BinaryLabel.Attack and host_multi_output is not None:
            candidates.append(
                (self._map_to_final(host_multi_output), host_multi_output.confidence)
            )

        # Nếu có 2 candidate → chọn confidence cao hơn
        if len(candidates) == 2:
            flowScore = flow_bin_output.confidence*candidates[0][1]
            host_score = host_bin_output.confidence*candidates[1][1]
            if flowScore>= host_score:
                return candidates[0]
            else:
                return candidates[1]

        # Nếu chỉ có 1 candidate
        if len(candidates) == 1:
            return candidates[0]

        # Không đủ thông tin
        return FinalPredictionLabel.Suspicious, 0.5

    # Map multi-class output → FinalPredictionLabel
    @staticmethod
    def _map_to_final(multi_output) -> FinalPredictionLabel:

        if isinstance(multi_output, HostMultiModelOutput):

            if multi_output.label == HostAttackLabel.SynScan:
                return FinalPredictionLabel.SynScan
            if multi_output.label == HostAttackLabel.UdpScan:
                return FinalPredictionLabel.UdpScan
            if multi_output.label == HostAttackLabel.FullScan:
                return FinalPredictionLabel.FullScan
            if multi_output.label == HostAttackLabel.BruteForce:
                return FinalPredictionLabel.BruteForce

        if isinstance(multi_output, FlowMultiModelOutput):

            if multi_output.label == FlowAttackLabel.SynFlood:
                return FinalPredictionLabel.SynFlood

            if multi_output.label == FlowAttackLabel.UdpFlood:
                return FinalPredictionLabel.UdpFlood

        return FinalPredictionLabel.Suspicious