import pandas as pd
import glob
import os

# Map dataset label variants -> canonical labels expected by code
LABEL_MAP = {
    'TcpFlood': 'SynFlood',
    'SshBruteForce': 'BruteForce',
}

CSV_GLOBS = [
    'Dataset/*.csv'
]

OUT_SUFFIX = '.normalized.csv'


def normalize_file(path):
    print('Processing', path)
    df = pd.read_csv(path)
    if 'Label' not in df.columns:
        print('  No Label column; skipping')
        return
    # Map labels
    df['Label'] = df['Label'].replace(LABEL_MAP)

    out_path = path.replace('.csv', OUT_SUFFIX)
    df.to_csv(out_path, index=False)
    print('  Wrote', out_path)


if __name__ == '__main__':
    for g in CSV_GLOBS:
        for p in glob.glob(g):
            normalize_file(p)
    print('Done')

