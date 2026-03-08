"""Quick analysis for FlowMultiDataset features vs labels.
Prints per-label counts and stats for features used by FlowMultiFeatures and a small decision-tree separability test.
"""
import pandas as pd
import os
import math

PATH = os.path.join(os.path.dirname(__file__), '..', 'Dataset', 'FlowMultiDataset.csv')
PATH = os.path.normpath(PATH)
FEATURES = [
    "packets_per_second",
    "bytes_per_second",
    "packet_count",
    "forward_ratio",
    "syn_ratio",
    "rst_ratio",
]
EXTRA = ['protocol']

if not os.path.exists(PATH):
    print('File not found:', PATH)
    raise SystemExit(1)

print('Reading', PATH)
# try to read with a moderate memory footprint
usecols = FEATURES + ['Label'] + EXTRA
try:
    df = pd.read_csv(PATH, usecols=usecols)
except Exception as e:
    print('Error reading CSV:', e)
    raise

print('\nTotal rows read:', len(df))
print('\nLabel value counts:')
print(df['Label'].value_counts(dropna=False).to_string())

# Missing values
print('\nMissing values per feature:')
print(df[FEATURES].isna().sum())

# Per-label stats
labels = df['Label'].unique()
for lbl in sorted(labels.astype(str)):
    sub = df[df['Label'] == lbl]
    print('\n=== Label:', lbl, 'rows=', len(sub), '===')
    for f in FEATURES:
        col = sub[f]
        cnt = col.count()
        if cnt == 0:
            print(f'  {f}: no data')
            continue
        mean = col.mean()
        std = col.std()
        mn = col.min()
        mx = col.max()
        pct0 = (col == 0).sum() / len(sub) * 100
        pct1 = (col == 1).sum() / len(sub) * 100
        uniq = col.nunique(dropna=True)
        print(f'  {f}: n={len(sub)}, count={cnt}, uniq={uniq}, mean={mean:.4f}, std={std:.4f}, min={mn}, max={mx}, %==0={pct0:.2f}%, %==1={pct1:.2f}%')

# Check protocol distribution for labels
if 'protocol' in df.columns:
    print('\nProtocol per label (sample):')
    for lbl in sorted(labels.astype(str)):
        sub = df[df['Label'] == lbl]
        print('  ', lbl, sub['protocol'].value_counts().to_dict())

# Quick separability test for SynFlood vs UdpFlood
try:
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.model_selection import cross_val_score
    import numpy as np
    mask = df['Label'].isin(['SynFlood', 'UdpFlood'])
    df2 = df[mask].copy()
    if len(df2) == 0:
        print('\nNo SynFlood/UdpFlood rows to test')
    else:
        X = df2[FEATURES].fillna(0).values
        y = (df2['Label'] == 'SynFlood').astype(int).values
        clf = DecisionTreeClassifier(max_depth=4)
        scores = cross_val_score(clf, X, y, cv=5, scoring='accuracy')
        print('\nDecisionTree CV accuracy (SynFlood vs UdpFlood):', scores.mean(), scores)
        clf.fit(X, y)
        try:
            importances = clf.feature_importances_
            print('Feature importances:')
            for f,imp in sorted(zip(FEATURES, importances), key=lambda x:-x[1]):
                print(' ', f, imp)
        except Exception:
            pass
except Exception as e:
    print('\nCould not run sklearn separability test:', e)

print('\nAnalysis complete')

