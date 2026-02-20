from src.Train.RfTrainer import RfTrainer
from pathlib import Path

def main():
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    data_path = PROJECT_ROOT / "src/Dataset/flowBenignLabeled.csv"
    dest_dir = PROJECT_ROOT / "src/Train"

    trainer = RfTrainer(str(data_path), str(dest_dir))
    trainer.train_flow_binary()

if __name__ == "__main__":
    main()
