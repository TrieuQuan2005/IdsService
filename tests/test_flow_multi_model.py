import pandas as pd
path = r'Dataset\FlowMultiDataset.csv'
df = pd.read_csv(path, usecols=['timestamp','packets_per_second','bytes_per_second','packet_count','forward_ratio','syn_ratio','rst_ratio','protocol','Label'])
# anomalies
syn0_synf = df[(df['Label']=='SynFlood') & (df['syn_ratio']==0.0)]
syn1_udpf = df[(df['Label']=='UdpFlood') & (df['syn_ratio']==1.0)]
print('Total rows:', len(df))
print('SynFlood total:', (df['Label']=='SynFlood').sum())
print('UdpFlood total:', (df['Label']=='UdpFlood').sum())
print('\nSynFlood rows with syn_ratio==0:', len(syn0_synf))
print(syn0_synf.head(10).to_string(index=False))
print('\nUdpFlood rows with syn_ratio==1:', len(syn1_udpf))
print(syn1_udpf.head(10).to_string(index=False))
# show unique protocols in anomalies
print('\nProtocols in SynFlood with syn_ratio==0:', syn0_synf['protocol'].value_counts().to_dict())
print('Protocols in UdpFlood with syn_ratio==1:', syn1_udpf['protocol'].value_counts().to_dict())
