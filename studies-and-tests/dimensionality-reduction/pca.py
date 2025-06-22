# Applies Principal Component Analysis (PCA) on the CIC-IoT-2023 dataset

import os
from resource import *
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from tqdm import tqdm

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

DATASET_DIRECTORY = ''


# Importing dataset
print('Importing dataset...')

df_sets = [k for k in os.listdir(DATASET_DIRECTORY) if k.endswith('.csv')]
df_sets.sort()

d_indv = []
for df_set in tqdm(df_sets):
    d_indv.append(pd.read_csv(DATASET_DIRECTORY + df_set))
    d_indv[-1] = d_indv[-1][d_indv[-1]['Rate'] != np.inf]

d = pd.concat(d_indv)

for d_i in d_indv:
    del d_i
del d_indv


# Dropping label
print('Dropping label...')

y = d.pop('Label')


# Scaling
print('Scaling...')

scaler = StandardScaler()
d[d.columns] = scaler.fit_transform(d[d.columns])


# PCA
print('Computing PCA...')

pca = PCA(random_state=0)
X_pca = pca.fit_transform(d)


# Metrics about the execution

print(f'\n\nMetrics')
print(getrusage(RUSAGE_SELF))

