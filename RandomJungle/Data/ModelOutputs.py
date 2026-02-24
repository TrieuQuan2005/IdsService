from dataclasses import dataclass
from typing import Dict
from RandomJungle.Data.Labels import (
    BinaryLabel,
    HostAttackLabel,
    FlowAttackLabel,
)

@dataclass(slots=True)
class BinaryModelOutput:
    label: BinaryLabel
    confidence: float
    attack_probability: float
    probabilities: Dict[BinaryLabel, float]

    @staticmethod
    def from_proba(probs):
        benign_prob = float(probs[0])
        attack_prob = float(probs[1])

        label = (
            BinaryLabel.ATTACK if attack_prob >= benign_prob
            else BinaryLabel.BENIGN
        )

        return BinaryModelOutput(
            label=label,
            confidence=max(benign_prob, attack_prob),
            attack_probability=attack_prob,
            probabilities={
                BinaryLabel.BENIGN: benign_prob,
                BinaryLabel.ATTACK: attack_prob,
            }
        )

@dataclass(slots=True)
class HostMultiModelOutput:
    label: HostAttackLabel
    confidence: float
    probabilities: Dict[HostAttackLabel, float]

    @staticmethod
    def from_proba(probs):
        p_portscan = float(probs[0])
        p_bruteforce = float(probs[1])

        if p_portscan >= p_bruteforce:
            label = HostAttackLabel.PORT_SCAN
            confidence = p_portscan
        else:
            label = HostAttackLabel.BRUTE_FORCE
            confidence = p_bruteforce

        return HostMultiModelOutput(
            label=label,
            confidence=confidence,
            probabilities={
                HostAttackLabel.PORT_SCAN: p_portscan,
                HostAttackLabel.BRUTE_FORCE: p_bruteforce,
            }
        )

@dataclass(slots=True)
class FlowMultiModelOutput:
    label: FlowAttackLabel
    confidence: float
    probabilities: Dict[FlowAttackLabel, float]

    @staticmethod
    def from_proba(probs):
        p_dos = float(probs[0])
        p_ddos = float(probs[1])

        if p_dos >= p_ddos:
            label = FlowAttackLabel.DOS
            confidence = p_dos
        else:
            label = FlowAttackLabel.DDOS
            confidence = p_ddos

        return FlowMultiModelOutput(
            label=label,
            confidence=confidence,
            probabilities={
                FlowAttackLabel.DOS: p_dos,
                FlowAttackLabel.DDOS: p_ddos,
            }
        )
