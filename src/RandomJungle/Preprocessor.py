import math
from typing import Tuple

from NetworkReader.Data.ValueObjects.FlowBased.FlowFeatureVector import FlowFeatureVector
from NetworkReader.Data.ValueObjects.HostBased.HostFeatureVector import HostFeatureVector

from Data.FeatureSets import (
    HostBinaryFeatures,
    FlowBinaryFeatures,
    HostMultiFeatures,
    FlowMultiFeatures,
)


class Preprocessor:

    def __init__(self):
        self._eps = 1e-6
        self._global_cap = 1e9  # prevent extreme overflow values

    def transform(
        self,
        host: HostFeatureVector,
        flow: FlowFeatureVector
    ) -> Tuple[
        HostBinaryFeatures,
        FlowBinaryFeatures,
        HostMultiFeatures,
        FlowMultiFeatures
    ]:

        host_bin = self._build_host_binary(host)
        flow_bin = self._build_flow_binary(flow)
        host_multi = self._build_host_multi(host)
        flow_multi = self._build_flow_multi(flow)

        return host_bin, flow_bin, host_multi, flow_multi

    def _build_host_binary(self, h: HostFeatureVector) -> HostBinaryFeatures:
        return HostBinaryFeatures(
            packets_per_second=self._clean_numeric(h.packets_per_second),
            unique_dst_ports=self._clean_int(h.unique_dst_ports),
            port_entropy=self._clean_numeric(h.port_entropy, 0.0, 15.0),
            connections_per_second=self._clean_numeric(h.connections_per_second),
            failed_connection_ratio=self._clip_ratio(h.failed_connection_ratio),
            syn_ratio=self._clip_ratio(h.syn_ratio),
        )

    def _build_flow_binary(self, f: FlowFeatureVector) -> FlowBinaryFeatures:
        return FlowBinaryFeatures(
            packets_per_second=self._clean_numeric(f.packets_per_second),
            bytes_per_second=self._log_transform(f.bytes_per_second),
            packet_count=self._clean_int(f.packet_count),
            flow_duration=self._clean_numeric(f.flow_duration),
            forward_ratio=self._clip_ratio(f.forward_ratio),
            syn_ratio=self._clip_ratio(f.syn_ratio),
        )

    def _build_host_multi(self, h: HostFeatureVector) -> HostMultiFeatures:
        return HostMultiFeatures(
            unique_dst_ports=self._clean_int(h.unique_dst_ports),
            port_entropy=self._clean_numeric(h.port_entropy, 0.0, 15.0),
            failed_connection_ratio=self._clip_ratio(h.failed_connection_ratio),
            connections_per_second=self._clean_numeric(h.connections_per_second),
            mean_flow_duration=self._clean_numeric(h.mean_flow_duration),
            syn_ratio=self._clip_ratio(h.syn_ratio),
        )

    def _build_flow_multi(self, f: FlowFeatureVector) -> FlowMultiFeatures:
        return FlowMultiFeatures(
            packets_per_second=self._clean_numeric(f.packets_per_second),
            bytes_per_second=self._log_transform(f.bytes_per_second),
            packet_count=self._clean_int(f.packet_count),
            forward_ratio=self._clip_ratio(f.forward_ratio),
            syn_ratio=self._clip_ratio(f.syn_ratio),
            rst_ratio=self._clip_ratio(f.rst_ratio),
        )

    def _clean_numeric(self,value: float,min_val: float = 0.0,max_val: float = None) -> float:
        if value is None:
            return min_val

        try:
            value = float(value)
        except (ValueError, TypeError):
            return min_val

        if math.isnan(value) or math.isinf(value):
            return min_val

        # prevent extreme overflow
        if value > self._global_cap:
            value = self._global_cap

        if value < min_val:
            value = min_val

        if max_val is not None and value > max_val:
            value = max_val

        return value

    def _clean_int(self, value: float) -> int:
        value = self._clean_numeric(value, min_val=0.0)
        return int(value)

    @staticmethod
    def _clip_ratio(value: float) -> float:
        if value is None:
            return 0.0

        try:
            value = float(value)
        except (ValueError, TypeError):
            return 0.0

        if math.isnan(value) or math.isinf(value):
            return 0.0

        return max(0.0, min(value, 1.0))

    def _log_transform(self, value: float) -> float:
        value = self._clean_numeric(value, min_val=0.0)

        if value <= 0:
            return 0.0

        return math.log(value + self._eps)
