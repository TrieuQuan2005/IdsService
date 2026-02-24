# RandomJungle/Data/FeatureSets.py

from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass(slots=True)
class HostBinaryFeatures:
    packets_per_second: float
    unique_dst_ports: int
    port_entropy: float
    connections_per_second: float
    failed_connection_ratio: float
    syn_ratio: float
    mean_flow_duration: float

    FEATURE_NAMES  = [
        "unique_dst_ports",
        "port_entropy",
        "connections_per_second",
        "failed_connection_ratio",
        "syn_ratio",
        "mean_flow_duration",
    ]

    def to_array(self) -> np.ndarray:
        return np.array([
            float(self.packets_per_second),
            float(self.unique_dst_ports),
            float(self.port_entropy),
            float(self.connections_per_second),
            float(self.failed_connection_ratio),
            float(self.syn_ratio),
            float(self.mean_flow_duration),
        ], dtype=np.float32)


@dataclass(slots=True)
class FlowBinaryFeatures:
    packets_per_second: float
    bytes_per_second: float
    packet_count: int
    flow_duration: float
    forward_ratio: float
    syn_ratio: float

    FEATURE_NAMES = [
        "packets_per_second",
        "bytes_per_second",
        "packet_count",
        "inter_arrival_variance",
        "forward_ratio",
        "syn_ratio",
    ]

    def to_array(self) -> np.ndarray:
        return np.array([
            float(self.packets_per_second),
            float(self.bytes_per_second),
            float(self.packet_count),
            float(self.flow_duration),
            float(self.forward_ratio),
            float(self.syn_ratio),
        ], dtype=np.float32)


@dataclass(slots=True)
class HostMultiFeatures:
    unique_dst_ports: int
    port_entropy: float
    failed_connection_ratio: float
    connections_per_second: float
    mean_flow_duration: float
    syn_ratio: float

    FEATURE_NAMES = [
        "unique_dst_ports",
        "port_entropy",
        "failed_connection_ratio",
        "connections_per_second",
        "mean_flow_duration",
        "syn_ratio",
    ]

    def to_array(self) -> np.ndarray:
        return np.array([
            float(self.unique_dst_ports),
            float(self.port_entropy),
            float(self.failed_connection_ratio),
            float(self.connections_per_second),
            float(self.mean_flow_duration),
            float(self.syn_ratio),
        ], dtype=np.float32)



@dataclass(slots=True)
class FlowMultiFeatures:
    packets_per_second: float
    bytes_per_second: float
    packet_count: int
    forward_ratio: float
    syn_ratio: float
    rst_ratio: float

    FEATURE_NAMES = [
        "packets_per_second",
        "bytes_per_second",
        "packet_count",
        "forward_ratio",
        "syn_ratio",
        "rst_ratio",
    ]

    def to_array(self) -> np.ndarray:
        return np.array([
            float(self.packets_per_second),
            float(self.bytes_per_second),
            float(self.packet_count),
            float(self.forward_ratio),
            float(self.syn_ratio),
            float(self.rst_ratio),
        ], dtype=np.float32)

