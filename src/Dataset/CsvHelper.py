import pandas as pd
from pathlib import Path

# ===== sửa path tại đây =====
INPUT_FILE = "flowBenignDownloadD.csv"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_FILE = PROJECT_ROOT / "src/Dataset/flowBenignLabeled.csv"
LABEL_NAME = "BENIGN"
LABEL_COLUMN = "Label"
# ============================

def main():
    print("Reading dataset...")
    df = pd.read_csv(INPUT_FILE)

    print("Rows:", len(df))

    # tạo hoặc ghi đè cột Label
    df[LABEL_COLUMN] = LABEL_NAME

    print("Label column added.")

    # lưu file mới
    Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("Saved to:", OUTPUT_FILE)

if __name__ == "__main__":
    main()
