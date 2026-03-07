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
    def from_proba(probs, classes):
        prob_map = dict(zip(classes, probs))

        p_benign = float(prob_map.get("Benign", 0))
        p_attack = float(prob_map.get("Attack", 0))

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
    def from_proba(probs, classes):
        prob_map = dict(zip(classes, probs))

        p_benign = float(prob_map.get("Benign", 0))
        p_attack = float(prob_map.get("Attack", 0))

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