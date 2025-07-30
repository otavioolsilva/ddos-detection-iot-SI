# Training a Hoeffding Tree using the CIC-IoT-2023 dataset
# and exporting the model parameters

# This script is based on the example provided in the used dataset,
# which can be found at: https://www.unb.ca/cic/datasets/iotdataset-2023.html

import os
import sys
from resource import *
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from tqdm import tqdm

from sklearn.preprocessing import MinMaxScaler, StandardScaler
from river.tree import HoeffdingTreeClassifier
from river.metrics import ClassificationReport

import joblib

DATASET_DIRECTORY = './'
if len(sys.argv) > 1:
    FILENAME_MODEL = sys.argv[1]
else:
    FILENAME_MODEL = 'ht.pkl'


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


# Function to train the model and perform reference test

def train(model):
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

            model.learn_one(x, y[i])

        del d

    print(report)


# Running the model

print('\nTraining the model')

model = HoeffdingTreeClassifier(remove_poor_attrs=True, max_size=65.0)
train(model)


# Exporting model parameters

joblib.dump(model, FILENAME_MODEL)


# To get metrics about the execution

print('Metrics')
print(getrusage(RUSAGE_SELF))


