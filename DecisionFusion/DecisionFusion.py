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
                label=BinaryLabel.BENIGN,
                confidence=1.0,
                attack_probability=0.0,
                probabilities={
                    BinaryLabel.BENIGN: 1.0,
                    BinaryLabel.ATTACK: 0.0,
                },
            )

        if flow_bin_output is None:
            flow_bin_output = BinaryModelOutput(
                label=BinaryLabel.BENIGN,
                confidence=1.0,
                attack_probability=0.0,
                probabilities={
                    BinaryLabel.BENIGN: 1.0,
                    BinaryLabel.ATTACK: 0.0,
                },
            )

        # Case 1: Both benign
        if host_bin_output.label == BinaryLabel.BENIGN and flow_bin_output.label == BinaryLabel.BENIGN:
            return FinalPredictionLabel.BENIGN

        candidates = []

        # Host branch
        if host_bin_output.label == BinaryLabel.ATTACK and host_multi_output is not None:
            candidates.append(host_multi_output)

        # Flow branch
        if flow_bin_output.label == BinaryLabel.ATTACK and flow_multi_output is not None:
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
        return FinalPredictionLabel.BENIGN

    # Map multi-class output → FinalPredictionLabel
    @staticmethod
    def _map_to_final(multi_output) -> FinalPredictionLabel:

        if isinstance(multi_output, HostMultiModelOutput):

            if multi_output.label == HostAttackLabel.PORT_SCAN:
                return FinalPredictionLabel.PORT_SCAN

            if multi_output.label == HostAttackLabel.BRUTE_FORCE:
                return FinalPredictionLabel.BRUTE_FORCE

        if isinstance(multi_output, FlowMultiModelOutput):

            if multi_output.label == FlowAttackLabel.TcpFlood:
                return FinalPredictionLabel.TcpFlood

            if multi_output.label == FlowAttackLabel.UdpFlood:
                return FinalPredictionLabel.UdpFlood

        return FinalPredictionLabel.BENIGN