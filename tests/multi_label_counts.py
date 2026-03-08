import pandas as pd

paths = ['../Dataset/FlowMultiDataset.csv','../Dataset/HostMultiDataset.csv']
for p in paths:
    try:
        df = pd.read_csv(p)
        print('FILE:', p)
        print('Total rows:', len(df))
        if 'Label' in df.columns:
            print(df['Label'].value_counts())
        else:
            print('No Label column')
        print('\n')
    except Exception as e:
        print('Error reading', p, e)

