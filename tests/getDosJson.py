import pandas as pd
import json

CSV_PATH = "../data/raw/CICIDS2017.csv"
OUTPUT_JSON = "dos_19_features.json"

SELECTED_FEATURES = [
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Flow Bytes/s",
    "Flow Packets/s",
    "Average Packet Size",
    "Packet Length Variance",
    "Flow IAT Mean",
    "Flow IAT Std",
    "Fwd IAT Mean",
    "Bwd IAT Mean",
    "Min Packet Length",
    "Max Packet Length",
    "SYN Flag Count",
    "ACK Flag Count",
    "RST Flag Count",
    "Down/Up Ratio",
    "Active Mean",
    "Idle Mean"
]

# Load dataset
df = pd.read_csv(CSV_PATH)
df.columns = df.columns.str.strip()

# Lọc DoS
dos_df = df[df["Label"].str.contains("DoS", case=False)]

if dos_df.empty:
    raise Exception("❌ Không tìm thấy mẫu DoS")

# Lấy 1 mẫu DoS thật
sample = dos_df.sample(1)

# Chỉ lấy 19 feature
sample_19 = sample[SELECTED_FEATURES]

# Convert sang dict
sample_dict = sample_19.iloc[0].to_dict()

# Save JSON
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(sample_dict, f, indent=2)

print("✅ DoS sample (19 features):")
print(json.dumps(sample_dict, indent=2))