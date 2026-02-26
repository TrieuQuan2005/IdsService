from RandomJungle.Data.Labels import (
    BinaryLabel,
    HostAttackLabel,
    FlowAttackLabel,
    FinalPredictionLabel,
)

from RandomJungle.Data.ModelOutputs import (
    BinaryModelOutput,
    HostMultiModelOutput,
    FlowMultiModelOutput,
)


class DecisionFusion:

    def fuse(
        self,
        host_bin_output: BinaryModelOutput | None,
        flow_bin_output: BinaryModelOutput | None,
        host_multi_output: HostMultiModelOutput | None = None,
        flow_multi_output: FlowMultiModelOutput | None = None,
    ) -> FinalPredictionLabel:

        # Normalize None branch
        if host_bin_output is None:
            host_bin_output = BinaryModelOutput(
                label=BinaryLabel.Benign,
                confidence=1.0,
                attack_probability=0.0,
                probabilities={
                    BinaryLabel.Benign: 1.0,
                    BinaryLabel.Attack: 0.0,
                },
            )

        if flow_bin_output is None:
            flow_bin_output = BinaryModelOutput(
                label=BinaryLabel.Benign,
                confidence=1.0,
                attack_probability=0.0,
                probabilities={
                    BinaryLabel.Benign: 1.0,
                    BinaryLabel.Attack: 0.0,
                },
            )

        # Case 1: Both benign
        if host_bin_output.label == BinaryLabel.Benign and flow_bin_output.label == BinaryLabel.Benign:
            return FinalPredictionLabel.Benign

        candidates = []

        # Host branch
        if host_bin_output.label == BinaryLabel.Attack and host_multi_output is not None:
            candidates.append(host_multi_output)

        # Flow branch
        if flow_bin_output.label == BinaryLabel.Attack and flow_multi_output is not None:
            candidates.append(flow_multi_output)

        # Only one attack branch
        if len(candidates) == 1:
            return self._map_to_final(candidates[0])

        # Both attack → compare confidence
        if len(candidates) == 2:
            if candidates[0].confidence >= candidates[1].confidence:
                return self._map_to_final(candidates[0])
            else:
                return self._map_to_final(candidates[1])

        # Fallback
        return FinalPredictionLabel.Benign

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

            if multi_output.label == FlowAttackLabel.TcpFlood:
                return FinalPredictionLabel.TcpFlood

            if multi_output.label == FlowAttackLabel.UdpFlood:
                return FinalPredictionLabel.UdpFlood

        return FinalPredictionLabel.Benign