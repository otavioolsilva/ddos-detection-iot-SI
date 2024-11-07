# Training a hoeffding tree model using the CIC-IoT-2023 dataset

# This script is based on the example provided in the used dataset, which can be found at:
# https://www.unb.ca/cic/datasets/iotdataset-2023.html

import os
from resource import *
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from tqdm import tqdm

from sklearn.preprocessing import MinMaxScaler, StandardScaler
from river.tree import HoeffdingTreeClassifier
from river.metrics import ClassificationReport

DATASET_DIRECTORY = '../datasets/CIC-IoT-2023/CSV/MERGED_CSV/'


# Importing dataset

df_sets = [k for k in os.listdir(DATASET_DIRECTORY) if k.endswith('.csv')]
df_sets.sort()

X_columns = [
    'Header_Length', 'Protocol Type', 'Time_To_Live', 'Rate', 'fin_flag_number',
    'syn_flag_number', 'rst_flag_number', 'psh_flag_number', 'ack_flag_number',
    'ece_flag_number', 'cwr_flag_number', 'ack_count', 'syn_count', 'fin_count',
    'rst_count', 'HTTP', 'HTTPS', 'DNS', 'Telnet', 'SMTP', 'SSH', 'IRC', 'TCP',
    'UDP', 'DHCP', 'ARP', 'ICMP', 'IGMP', 'IPv', 'LLC', 'Tot sum', 'Min', 'Max',
    'AVG', 'Std', 'Tot size', 'IAT', 'Number', 'Variance'
]

y_column = 'Label'


# Scaling

print('Scaling')

scaler = StandardScaler()

for df_set in tqdm(df_sets):
    d = pd.read_csv(DATASET_DIRECTORY + df_set)
    d = d[d['Rate'] != np.inf]
    scaler.fit(d[X_columns])


# Function to train and test the model

def train_and_test(model, label_dict={}):
    report = ClassificationReport()

    for df_set in tqdm(df_sets):
        d = pd.read_csv(DATASET_DIRECTORY + df_set)
        d = d[d['Rate'] != np.inf]
        d[X_columns] = scaler.transform(d[X_columns])

        if len(label_dict) > 0:
            new_y = [label_dict[k] for k in d[y_column]]
            d[y_column] = new_y

        y = d[y_column]
        X = d.drop(y_column, axis=1)

        for i, x in X.iterrows():
            predicted_y = model.predict_one(x)

            if type(predicted_y) == type(y[i]):
                report.update(y[i], predicted_y)

            model.learn_one(x, y[i])

        del d

    print(report)


# Dictionary to convert labels from different attacks to only one category

dict_2classes = {}

dict_2classes['DDOS-RSTFINFLOOD'] = 'Attack'
dict_2classes['DDOS-PSHACK_FLOOD'] = 'Attack'
dict_2classes['DDOS-SYN_FLOOD'] = 'Attack'
dict_2classes['DDOS-UDP_FLOOD'] = 'Attack'
dict_2classes['DDOS-TCP_FLOOD'] = 'Attack'
dict_2classes['DDOS-ICMP_FLOOD'] = 'Attack'
dict_2classes['DDOS-SYNONYMOUSIP_FLOOD'] = 'Attack'
dict_2classes['DDOS-ACK_FRAGMENTATION'] = 'Attack'
dict_2classes['DDOS-UDP_FRAGMENTATION'] = 'Attack'
dict_2classes['DDOS-ICMP_FRAGMENTATION'] = 'Attack'
dict_2classes['DDOS-SLOWLORIS'] = 'Attack'
dict_2classes['DDOS-HTTP_FLOOD'] = 'Attack'

dict_2classes['DOS-UDP_FLOOD'] = 'Attack'
dict_2classes['DOS-SYN_FLOOD'] = 'Attack'
dict_2classes['DOS-TCP_FLOOD'] = 'Attack'
dict_2classes['DOS-HTTP_FLOOD'] = 'Attack'


dict_2classes['MIRAI-GREETH_FLOOD'] = 'Attack'
dict_2classes['MIRAI-GREIP_FLOOD'] = 'Attack'
dict_2classes['MIRAI-UDPPLAIN'] = 'Attack'

dict_2classes['RECON-PINGSWEEP'] = 'Attack'
dict_2classes['RECON-OSSCAN'] = 'Attack'
dict_2classes['RECON-PORTSCAN'] = 'Attack'
dict_2classes['VULNERABILITYSCAN'] = 'Attack'
dict_2classes['RECON-HOSTDISCOVERY'] = 'Attack'

dict_2classes['DNS_SPOOFING'] = 'Attack'
dict_2classes['MITM-ARPSPOOFING'] = 'Attack'

dict_2classes['BENIGN'] = 'Benign'

dict_2classes['BROWSERHIJACKING'] = 'Attack'
dict_2classes['BACKDOOR_MALWARE'] = 'Attack'
dict_2classes['XSS'] = 'Attack'
dict_2classes['UPLOADING_ATTACK'] = 'Attack'
dict_2classes['SQLINJECTION'] = 'Attack'
dict_2classes['COMMANDINJECTION'] = 'Attack'

dict_2classes['DICTIONARYBRUTEFORCE'] = 'Attack'


# Running the model

print('\nTraining and testing the model')

model = HoeffdingTreeClassifier()
train_and_test(model, dict_2classes)


# To get metrics about the execution

print('Metrics')
print(getrusage(RUSAGE_SELF))

