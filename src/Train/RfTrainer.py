import os
import pandas as pd
import numpy as np

from RandomJungle.Models.RfFlowBin import RfFlowBin
from RandomJungle.Models.RfFlowMulti import RfFlowMulti
from RandomJungle.Models.RfHostBin import RfHostBin
from RandomJungle.Models.RfHostMulti import RfHostMulti


class RfTrainer:

    def __init__(self, data_path: str, output_dir: str):
        self.data_path = data_path
        self.output_dir = output_dir

        self.hostBin = RfHostBin()
        self.flowBin = RfFlowBin()
        self.hostMulti = RfHostMulti()
        self.flowMulti = RfFlowMulti()

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.df = pd.read_csv(self.data_path)

        if "Label" not in self.df.columns:
            raise ValueError("Dataset must contain 'Label' column")

    # HOST BINARY
    def train_host_binary(self):

        print("Training Host Binary...")

        X = self.df[self._host_binary_columns()].values
        y = (self.df["Label"] != "BENIGN").astype(int).values

        self.hostBin.fit(X, y)
        self.hostBin.save(os.path.join(self.output_dir, "hostBin.pkl"))

        print("Host Binary trained.")

    # FLOW BINARY
    def train_flow_binary(self):

        print("Training Flow Binary...")

        X = self.df[self._flow_binary_columns()].values
        y = (self.df["Label"] != "Benign").astype(int).values

        self.flowBin.fit(X, y)
        self.flowBin.save(os.path.join(self.output_dir, "flowBin.pkl"))

        print("Flow Binary trained.")

    # HOST MULTI (PortScan / BruteForce)
    def train_host_multi(self):

        print("Training Host Multi...")

        df_host = self.df[self.df["Label"].isin(["PortScan", "Brute Force"])]

        X = df_host[self._host_multi_columns()].values

        y = df_host["Label"].map({
            "PortScan": 0,
            "Brute Force": 1
        }).values

        self.hostMulti.fit(X, y)
        self.hostMulti.save(os.path.join(self.output_dir, "hostMulti.pkl"))

        print("Host Multi trained.")

    # FLOW MULTI (DoS / DDoS)
    def train_flow_multi(self):

        print("Training Flow Multi...")

        df_flow = self.df[self.df["Label"].str.contains("DoS|DDoS", na=False)]

        X = df_flow[self._flow_multi_columns()].values

        y = df_flow["Label"].apply(
            lambda x: 1 if "DDoS" in x else 0
        ).values

        self.flowMulti.fit(X, y)
        self.flowMulti.save(os.path.join(self.output_dir, "flowMulti.pkl"))

        print("Flow Multi trained.")

    # TRAIN ALL
    def train_all(self):

        print("=== START TRAINING ALL MODELS ===")

        self.train_host_binary()
        self.train_flow_binary()
        self.train_host_multi()
        self.train_flow_multi()

        print("=== ALL MODELS TRAINED SUCCESSFULLY ===")

    # FEATURE COLUMN DEFINITIONS
    @staticmethod
    def _host_binary_columns():
        return [
            "packets_per_second",
            "unique_dst_ports",
            "port_entropy",
            "connections_per_second",
            "failed_connection_ratio",
            "syn_ratio",
        ]

    @staticmethod
    def _flow_binary_columns():
        return [
            "packets_per_second",
            "bytes_per_second",
            "packet_count",
            "flow_duration",
            "forward_ratio",
            "syn_ratio",
        ]

    @staticmethod
    def _host_multi_columns():
        return [
            "unique_dst_ports",
            "port_entropy",
            "failed_connection_ratio",
            "connections_per_second",
            "mean_flow_duration",
            "syn_ratio",
        ]

    @staticmethod
    def _flow_multi_columns():
        return [
            "packets_per_second",
            "bytes_per_second",
            "packet_count",
            "forward_ratio",
            "syn_ratio",
            "rst_ratio",
        ]
