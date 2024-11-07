# Training a logistic regression model using the CIC-IoT-2023 dataset

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
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.exceptions import ConvergenceWarning

DATASET_DIRECTORY = '../datasets/CIC-IoT-2023/CSV/MERGED_CSV/'


# Importing dataset

df_sets = [k for k in os.listdir(DATASET_DIRECTORY) if k.endswith('.csv')]
df_sets.sort()
training_sets = df_sets[:int(len(df_sets)*.8)]
test_sets = df_sets[int(len(df_sets)*.8):]

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

for train_set in tqdm(training_sets):
    d = pd.read_csv(DATASET_DIRECTORY + train_set)
    d = d[d['Rate'] != np.inf]
    scaler.fit(d[X_columns])


# Functions to train and test the model

def train(model, label_dict={}):
    for train_set in tqdm(training_sets):
        d = pd.read_csv(DATASET_DIRECTORY + train_set)
        d = d[d['Rate'] != np.inf] # some entries presented the value 'inf' for the 'Rate' variable, we simply delete them
        d[X_columns] = scaler.transform(d[X_columns])

        if len(label_dict) > 0:
            new_y = [label_dict[k] for k in d[y_column]]
            d[y_column] = new_y

        model.fit(d[X_columns], d[y_column])
        del d

def test(model, label_dict={}):
    y_test = []
    y_pred = []
    for test_set in tqdm(test_sets):
        d_test = pd.read_csv(DATASET_DIRECTORY + test_set)
        d_test = d_test[d_test['Rate'] != np.inf]
        d_test[X_columns] = scaler.transform(d_test[X_columns])

        if len(label_dict) > 0:
            new_y = [label_dict[k] for k in d_test[y_column]]
            d_test[y_column] = new_y

        y_test += list(d_test[y_column].values)
        y_pred += list(model.predict(d_test[X_columns]))

        del d_test

    print(classification_report(y_test, y_pred, target_names=["Attack", "Benign"]))


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

model = LogisticRegression(n_jobs=-1)
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=ConvergenceWarning)
    train(model, dict_2classes)
test(model, dict_2classes)


# Metrics

print('Metrics')
print(getrusage(RUSAGE_SELF))

