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
        p_benign = float(probs[0])
        p_attack = float(probs[1])

        label = (
            BinaryLabel.ATTACK if p_attack >= p_benign
            else BinaryLabel.BENIGN
        )

        return BinaryModelOutput(
            label=label,
            confidence=max(p_benign, p_attack),
            attack_probability=p_attack,
            probabilities={
                BinaryLabel.BENIGN: p_benign,
                BinaryLabel.ATTACK: p_attack,
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
