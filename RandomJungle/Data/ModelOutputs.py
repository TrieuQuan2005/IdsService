from dataclasses import dataclass
from typing import Dict

import numpy as np

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
        p_benign = float(probs[0])
        p_attack = float(probs[1])

        label = (
            BinaryLabel.Attack if p_attack >= p_benign
            else BinaryLabel.Benign
        )

        return BinaryModelOutput(
            label=label,
            confidence=max(p_benign, p_attack),
            attack_probability=p_attack,
            probabilities={
                BinaryLabel.Benign: p_benign,
                BinaryLabel.Attack: p_attack,
            }
        )

@dataclass(slots=True)
class HostMultiModelOutput:
    label: HostAttackLabel
    confidence: float
    probabilities: Dict[HostAttackLabel, float]

    @staticmethod
    def from_proba(probs, classes):
        probs = np.asarray(probs)

        idx = int(np.argmax(probs))
        confidence = float(probs[idx])

        label = HostAttackLabel(classes[idx])

        probabilities = {
            HostAttackLabel(classes[i]): float(p)
            for i, p in enumerate(probs)
        }

        return HostMultiModelOutput(
            label=label,
            confidence=confidence,
            probabilities=probabilities
        )

@dataclass(slots=True)
class FlowMultiModelOutput:
    label: FlowAttackLabel
    confidence: float
    probabilities: Dict[FlowAttackLabel, float]

    @staticmethod
    def from_proba(probs):
        p_tcpFlood = float(probs[0])
        p_udpFlood = float(probs[1])

        if p_tcpFlood >= p_udpFlood:
            label = FlowAttackLabel.TcpFlood
            confidence = p_tcpFlood
        else:
            label = FlowAttackLabel.UdpFlood
            confidence = p_udpFlood

        return FlowMultiModelOutput(
            label=label,
            confidence=confidence,
            probabilities={
                FlowAttackLabel.TcpFlood: p_tcpFlood,
                FlowAttackLabel.UdpFlood: p_udpFlood,
            }
        )
