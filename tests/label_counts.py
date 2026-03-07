import pandas as pd

df = pd.read_csv('Dataset/FlowBinDataset.csv')
print('Total rows:', len(df))
print('\nLabel value counts:')
print(df['Label'].value_counts())

# show counts for multi classes
print('\nFlow multi classes counts:')
print(df[df['Label'].isin(['SynFlood','UdpFlood'])]['Label'].value_counts())
print('\nHost multi classes counts:')
print(df[df['Label'].isin(['SynScan','UdpScan','FullScan','BruteForce'])]['Label'].value_counts())

