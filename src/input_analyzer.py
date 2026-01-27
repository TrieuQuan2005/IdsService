import pandas as pd
import numpy as np
from typing import Union, List, Dict


class InputAnalyzer:
    REQUIRED_FEATURES = [
        "Flow_Duration",
        "Total_Fwd_Packets",
        "Total_Bwd_Packets",
        "Flow_Packets_per_s",
        "Flow_Bytes_per_s",
        "Avg_Packet_Size",
        "Packet_Length_Variance",
        "Flow_IAT_Mean",
        "Flow_IAT_Std",
        "Fwd_IAT_Mean",
        "Bwd_IAT_Mean",
        "SYN_Flag_Count",
        "RST_Flag_Count",
        "ACK_Flag_Count",
        "Down_Up_Ratio",
        "Min_Packet_Length",
        "Max_Packet_Length",
        "Active_Mean",
        "Idle_Mean"
    ]
    FEATURE_MAPPING = {
        "Flow_Duration": "Flow Duration",
        "Total_Fwd_Packets": "Total Fwd Packets",
        "Total_Bwd_Packets": "Total Backward Packets",
        "Flow_Bytes_per_s": "Flow Bytes/s",
        "Flow_Packets_per_s": "Flow Packets/s",
        "Avg_Packet_Size": "Average Packet Size",
        "Packet_Length_Variance": "Packet Length Variance",
        "Flow_IAT_Mean": "Flow IAT Mean",
        "Flow_IAT_Std": "Flow IAT Std",
        "Fwd_IAT_Mean": "Fwd IAT Mean",
        "Bwd_IAT_Mean": "Bwd IAT Mean",
        "Min_Packet_Length": "Min Packet Length",
        "Max_Packet_Length": "Max Packet Length",
        "SYN_Flag_Count": "SYN Flag Count",
        "ACK_Flag_Count": "ACK Flag Count",
        "RST_Flag_Count": "RST Flag Count",
        "Down_Up_Ratio": "Down/Up Ratio",
        "Active_Mean": "Active Mean",
        "Idle_Mean": "Idle Mean",
    }

    def validate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate input DataFrame (training or batch inference)
        """
        # 1. Check dataset columns (CICIDS naming)
        missing = [
            dataset_col
            for dataset_col in self.FEATURE_MAPPING.values()
            if dataset_col not in df.columns
        ]

        if missing:
            raise ValueError(f"Missing dataset columns: {missing}")

        # 2. Rename dataset columns → internal feature names
        df = df.rename(columns={v: k for k, v in self.FEATURE_MAPPING.items()})

        # 3. Select features in correct order
        df = df[list(self.FEATURE_MAPPING.keys())]

        # 4. Check numeric
        self._check_numeric(df)

        return df

    def validate_single_input(self, data: Union[List, Dict]) -> pd.DataFrame:
        """
        Validate single input from API
        """
        if isinstance(data, list):
            if len(data) != len(self.REQUIRED_FEATURES):
                raise ValueError("Invalid feature vector length")
            df = pd.DataFrame([data], columns=self.REQUIRED_FEATURES)

        elif isinstance(data, dict):
            missing = set(self.REQUIRED_FEATURES) - set(data.keys())
            if missing:
                raise ValueError(f"Missing features: {missing}")
            df = pd.DataFrame([data])[self.REQUIRED_FEATURES]

        else:
            raise TypeError("Input must be list or dict")

        self._check_numeric(df)
        return df

    def _check_missing_features(self, df: pd.DataFrame):
        missing = set(self.REQUIRED_FEATURES) - set(df.columns)
        if missing:
            raise ValueError(f"Missing features: {missing}")

    def _check_numeric(self, df: pd.DataFrame):
        if not np.all(df.dtypes.apply(lambda x: np.issubdtype(x, np.number))):
            raise TypeError("All features must be numeric")
