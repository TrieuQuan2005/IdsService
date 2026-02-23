from src.Train.RfTrainer import RfTrainer
from pathlib import Path

def main():
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    dest_dir = PROJECT_ROOT / "src/RandomJungle/Models"

    trainer = RfTrainer(
        str(PROJECT_ROOT / "src/Dataset/FlowBinDataset.csv"),
        str(dest_dir)
    )
    trainer.train_flow_binary()

if __name__ == "__main__":
    main()
