import os
import pandas as pd

from RandomJungle.Models.RfFlowBin import RfFlowBin
from RandomJungle.Models.RfFlowMulti import RfFlowMulti
from RandomJungle.Models.RfHostBin import RfHostBin
from RandomJungle.Models.RfHostMulti import RfHostMulti

from RandomJungle.Data.FeatureSets import FlowMultiFeatures, FlowBinaryFeatures, HostBinaryFeatures, HostMultiFeatures

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

        X = self.df[HostBinaryFeatures.FEATURE_NAMES].values
        y = (self.df["Label"] != "Benign").astype(int).values

        self.hostBin.fit(X, y)
        self.hostBin.save(os.path.join(self.output_dir, "hostBin.pkl"))

        print("Host Binary trained.")

    # FLOW BINARY
    def train_flow_binary(self):

        print("Training Flow Binary...")

        X = self.df[FlowBinaryFeatures.FEATURE_NAMES].values
        y = (self.df["Label"] != "Benign").astype(int).values

        self.flowBin.fit(X, y)
        self.flowBin.save(os.path.join(self.output_dir, "flowBin.pkl"))

        print("Flow Binary trained.")

    # HOST MULTI (PortScan / BruteForce)
    def train_host_multi(self):

        print("Training Host Multi...")

        df_host = self.df[self.df["Label"].isin(["PortScan", "Brute Force"])]

        X = df_host[HostMultiFeatures.FEATURE_NAMES].values

        y = df_host["Label"].map({
            "PortScan": 0,
            "Brute Force": 1
        }).values

        self.hostMulti.fit(X, y)
        self.hostMulti.save(os.path.join(self.output_dir, "hostMulti.pkl"))

        print("Host Multi trained.")

    def train_flow_multi(self):

        print("Training Flow Multi...")

        df_flow = self.df[self.df["Label"].isin(["TcpFlood", "UdpFlood"])]

        X = df_flow[FlowMultiFeatures.FEATURE_NAMES].values

        y = df_flow["Label"].map({
            "TcpFlood": 0,
            "UdpFlood": 1
        }).values

        self.flowMulti.fit(X, y)
        self.flowMulti.save(os.path.join(self.output_dir, "flowMulti.pkl"))

        print("Flow Multi trained.")