import os
import pandas as pd
from pandas.errors import EmptyDataError


def clean_and_shuffle_csv(file_path: str, random_state: int = 42):
    print(f"\nĐang xử lý: {file_path}")

    try:
        df = pd.read_csv(file_path)
    except EmptyDataError:
        print("File rỗng")
        return
    except Exception as e:
        print(f"Lỗi đọc file: {e}")
        return

    if df.empty:
        print("File không có dữ liệu → bỏ qua")
        return

    before = len(df)

    # Xoá duplicate
    df = df.drop_duplicates()

    after_dedup = len(df)

    # Shuffle
    df = df.sample(frac=1, random_state=random_state).reset_index(drop=True)

    df.to_csv(file_path, index=False)

    print(f"Ban đầu: {before}")
    print(f"Sau xoá dup: {after_dedup}")
    print(f"Đã xoá: {before - after_dedup}")

def process_all_csv(root_folder: str):
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                clean_and_shuffle_csv(file_path)

process_all_csv("../Helper")
