import pandas as pd
from glob import glob

files = glob("../data/raw/CICIDS2017.csv")
print(files)

dfs = []
for f in files:
    df = pd.read_csv(f)
    print(f, df['Label'].unique())
    dfs.append(df)

full = pd.concat(dfs, ignore_index=True)
print("ALL LABELS:", full['Label'].value_counts())