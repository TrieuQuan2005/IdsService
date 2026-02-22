from Data.Labels import (
    BinaryLabel,
    HostAttackLabel,
    FlowAttackLabel,
    FinalPredictionLabel,
)

from Data.ModelOutputs import (
    BinaryModelOutput,
    HostMultiModelOutput,
    FlowMultiModelOutput,
)


class DecisionFusion:

    def fuse(
        self,
        host_bin: BinaryModelOutput,
        flow_bin: BinaryModelOutput,
        host_multi: HostMultiModelOutput | None = None,
        flow_multi: FlowMultiModelOutput | None = None,
    ) -> FinalPredictionLabel:

        # ==========================
        # STAGE 1: Binary decision
        # ==========================
        if (
            host_bin.label == BinaryLabel.BENIGN
            and flow_bin.label == BinaryLabel.BENIGN
        ):
            return FinalPredictionLabel.BENIGN

        # ==========================
        # STAGE 2: Multi decision
        # ==========================

        candidates = []

        # Host branch activated
        if host_bin.label == BinaryLabel.ATTACK and host_multi is not None:
            candidates.append(("host", host_multi))

        # Flow branch activated
        if flow_bin.label == BinaryLabel.ATTACK and flow_multi is not None:
            candidates.append(("flow", flow_multi))

        # Nếu chỉ có 1 candidate
        if len(candidates) == 1:
            return self._map_to_final(candidates[0][1])

        # Nếu cả 2 đều activated
        if len(candidates) == 2:

            # So confidence
            if candidates[0][1].confidence >= candidates[1][1].confidence:
                return self._map_to_final(candidates[0][1])
            else:
                return self._map_to_final(candidates[1][1])

        # Fallback (rare case)
        return FinalPredictionLabel.BENIGN

    # ==========================
    # Mapping multi → final label
    # ==========================
    def _map_to_final(self, multi_output):

        if isinstance(multi_output, HostMultiModelOutput):
            if multi_output.label == HostAttackLabel.PORT_SCAN:
                return FinalPredictionLabel.PORT_SCAN
            else:
                return FinalPredictionLabel.BRUTE_FORCE

        if isinstance(multi_output, FlowMultiModelOutput):
            if multi_output.label == FlowAttackLabel.DOS:
                return FinalPredictionLabel.DOS
            else:
                return FinalPredictionLabel.DDOS

        return FinalPredictionLabel.BENIGN