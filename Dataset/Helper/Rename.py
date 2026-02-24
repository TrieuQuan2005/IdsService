import os
import pandas as pd

INPUT_FOLDER = "OfficalDataset"
OUTPUT_FOLDER = "OfficalDataset"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def convert_label(df):
    # Chuẩn hóa về string
    df["Label"] = df["Label"].astype(str)

    # Đổi tất cả nhãn khác Benign thành Attack
    df["Label"] = df["Label"].apply(
        lambda x: "Benign" if x.strip().lower() == "benign" else "Attack"
    )
    return df


for file in os.listdir(INPUT_FOLDER):
    if file.endswith(".csv"):
        input_path = os.path.join(INPUT_FOLDER, file)
        output_path = os.path.join(OUTPUT_FOLDER, file)

        print(f"Processing {file}...")

        df = pd.read_csv(input_path)
        df = convert_label(df)
        df.to_csv(output_path, index=False)

print("Done converting all files.")