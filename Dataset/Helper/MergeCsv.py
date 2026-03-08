import pandas as pd
import os
from typing import List, Tuple


def merge_csv_with_individual_sampling(
    files_with_count: List[Tuple[str, int]],
    output_file: str,
    random_state: int = 42
):

    merged_data = []

    for file_path, num_rows in files_with_count:

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue

        print(f"\nĐang đọc: {file_path}")
        df = pd.read_csv(file_path)

        # Nếu số lượng yêu cầu > số dòng thực tế
        if num_rows > len(df):
            print(f"Yêu cầu {num_rows} dòng nhưng file chỉ có {len(df)} dòng -> lấy toàn bộ.")
            sampled_df = df
        else:
            sampled_df = df.sample(
                n=num_rows,
                random_state=random_state
            )

        merged_data.append(sampled_df)

    if not merged_data:
        print("Không có dữ liệu để merge.")
        return

    final_df = pd.concat(merged_data, ignore_index=True)
    final_df.to_csv(output_file, index=False)

    print(f"\nMerge hoàn tất: {output_file}")
    print(f"Tổng số dòng: {len(final_df)}")


if __name__ == "__main__":
    files_config = [
        ("FlowSynFlood.csv", 9000),
        ("FlowUdpFlood.csv", 9000),

    ]

    merge_csv_with_individual_sampling(
        files_with_count=files_config,
        output_file="../FlowMultiDataset.csv"
    )