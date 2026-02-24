from Train.RfTrainer import RfTrainer
from pathlib import Path

def main():
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    dest_dir = PROJECT_ROOT / "src/RandomJungle/Models"

    FlowBinTrainer = RfTrainer(
        str(PROJECT_ROOT / "src/Dataset/FlowBinDataset.csv"),
        str(dest_dir)
    )
    FlowBinTrainer.train_flow_binary()

    HostBinTrainer = RfTrainer(
        str(PROJECT_ROOT / "src/Dataset/HostBinDataset.csv"),
        str(dest_dir)
    )
    HostBinTrainer.train_host_binary()

    FlowMultiTrainer = RfTrainer(
        str(PROJECT_ROOT / "src/Dataset/FlowMultiDataset.csv"),
        str(dest_dir)
    )
    FlowMultiTrainer.train_flow_multi()

    HostMultiTrainer = RfTrainer(
        str(PROJECT_ROOT / "src/Dataset/HostMultiDataset.csv"),
        str(dest_dir)
    )
    HostMultiTrainer.train_host_multi()

if __name__ == "__main__":
    main()
