import pandas as pd
import os
from typing import List, Tuple


def merge_csv_with_individual_sampling(
    files_with_ratio: List[Tuple[str, float]],
    output_file: str,
    random_state: int = 42
):

    merged_data = []

    for file_path, percent in files_with_ratio:

        if not os.path.exists(file_path):
            print(f"File not found : {file_path}")
            continue

        print(f"\nĐang đọc: {file_path}")
        df = pd.read_csv(file_path)


        df = df.sample(
            frac=percent / 100,
            random_state=random_state
        )

        merged_data.append(df)

    if not merged_data:
        print("Không có dữ liệu để merge.")
        return

    final_df = pd.concat(merged_data, ignore_index=True)
    final_df.to_csv(output_file, index=False)

    print(f"\nMerge hoàn tất  {output_file}")
    print(f"Tổng số dòng: {len(final_df)}")


if __name__ == "__main__":
    files_config = [
        ("DoS/FlowDoS.csv", 100)
    ]
    merge_csv_with_individual_sampling(
        files_with_ratio=files_config,
        output_file="../FlowMultiDataset.csv"
    )