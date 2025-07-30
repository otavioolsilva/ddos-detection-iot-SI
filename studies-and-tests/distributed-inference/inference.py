# Testing a ML model through imported parameters using joblib

import os
import sys
from resource import *

import joblib

import numpy as np
import pandas as pd
from tqdm import tqdm

from sklearn.preprocessing import StandardScaler
from river.tree import HoeffdingTreeClassifier
from river.metrics import ClassificationReport

DATASET_DIRECTORY = './'


# Importing model

if len(sys.argv) < 2:
    print(sys.argv[0], ": Necessary to inform model parameters file path", sep='')
    exit(1)

model = joblib.load(sys.argv[1])


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


# Function to test the model

def test(model):
    report = ClassificationReport()

    for df_set in tqdm(df_sets):
        d = pd.read_csv(DATASET_DIRECTORY + df_set)
        d = d[d['Rate'] != np.inf]
        d[X_columns] = scaler.transform(d[X_columns])

        y = d[y_column]
        X = d.drop(y_column, axis=1)

        for i, x in X.iterrows():
            predicted_y = model.predict_one(x)

            if type(predicted_y) == type(y[i]):
                report.update(y[i], predicted_y)

        del d

    print(report)


# Running the model

print('\nTesting the model')
test(model)


# To get metrics about the execution

print('Metrics')
print(getrusage(RUSAGE_SELF))

