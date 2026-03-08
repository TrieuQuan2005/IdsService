from dataclasses import dataclass
from typing import Dict, Optional, Sequence

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
    def from_proba(probs: Sequence[float], classes: Optional[Sequence] = None):
        """
        Build BinaryModelOutput from raw probability vector and model.classes_.
        This method is tolerant to different `classes` formats produced by sklearn:
        - classes may be ['Benign', 'Attack']
        - classes may be [0, 1]
        - classes may be None (assume index 0 = Benign, 1 = Attack)
        """
        probs = np.asarray(probs)

        # Default mapping: index 0 -> Benign, index 1 -> Attack
        p_benign = None
        p_attack = None

        if classes is None:
            if probs.size >= 2:
                p_benign = float(probs[0])
                p_attack = float(probs[1])
        else:
            # Try to find 'Benign'/'Attack' by name (case-insensitive)
            for i, c in enumerate(classes):
                try:
                    name = str(c)
                except Exception:
                    name = ""

                if name.lower() == "benign":
                    p_benign = float(probs[i])
                elif name.lower() == "attack":
                    p_attack = float(probs[i])

            # Fallback: classes might be numeric (0/1)
            if p_benign is None or p_attack is None:
                for i, c in enumerate(classes):
                    try:
                        if int(c) == 0 and p_benign is None:
                            p_benign = float(probs[i])
                        if int(c) == 1 and p_attack is None:
                            p_attack = float(probs[i])
                    except Exception:
                        # ignore non-int-convertible class labels
                        pass

            # Final fallback: use positional order
            if p_benign is None and probs.size >= 1:
                p_benign = float(probs[0])
            if p_attack is None and probs.size >= 2:
                p_attack = float(probs[1])

        # Ensure numbers
        if p_benign is None:
            p_benign = 0.0
        if p_attack is None:
            p_attack = 0.0

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
    def from_proba(probs: Sequence[float], classes: Optional[Sequence] = None):
        probs = np.asarray(probs)

        idx = int(np.argmax(probs))
        confidence = float(probs[idx])

        # Map class representation -> HostAttackLabel
        if classes is None:
            label = HostAttackLabel(idx)
        else:
            try:
                c = classes[idx]
                # If the class is a numeric index
                try:
                    label = HostAttackLabel(int(c))
                except Exception:
                    # If the class is a name like 'SynScan', map by name
                    try:
                        label = HostAttackLabel[c]
                    except Exception:
                        label = HostAttackLabel(idx)
            except Exception:
                label = HostAttackLabel(idx)

        probabilities = {}
        for i, p in enumerate(probs):
            try:
                if classes is None:
                    key = HostAttackLabel(i)
                else:
                    c = classes[i]
                    try:
                        key = HostAttackLabel(int(c))
                    except Exception:
                        try:
                            key = HostAttackLabel[c]
                        except Exception:
                            key = HostAttackLabel(i)
            except Exception:
                key = HostAttackLabel(i)

            probabilities[key] = float(p)

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
    def from_proba(probs: Sequence[float], classes: Optional[Sequence] = None):
        """
        Correctly build FlowMultiModelOutput from probability vector.
        Supports classes being numeric indexes or class names.
        """
        probs = np.asarray(probs)

        idx = int(np.argmax(probs))
        confidence = float(probs[idx])

        # Map to FlowAttackLabel
        if classes is None:
            label = FlowAttackLabel(idx)
        else:
            c = classes[idx]
            label = FlowAttackLabel(int(c))

        probabilities = {}
        for i, p in enumerate(probs):
            try:
                if classes is None:
                    key = FlowAttackLabel(i)
                else:
                    c = classes[i]
                    try:
                        key = FlowAttackLabel(int(c))
                    except Exception:
                        try:
                            key = FlowAttackLabel[c]
                        except Exception:
                            key = FlowAttackLabel(i)
            except Exception:
                key = FlowAttackLabel(i)

            probabilities[key] = float(p)

        return FlowMultiModelOutput(
            label=label,
            confidence=confidence,
            probabilities=probabilities
        )