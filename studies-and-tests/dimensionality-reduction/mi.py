# Applies Mutual Information on the CIC-IoT-2023 dataset

import os
from resource import *
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from tqdm import tqdm

from sklearn.feature_selection import mutual_info_classif

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


# Converting labels to 0 (benign) and 1 (malicious)
print('Converting labels...')

y = [0 if k == 'BENIGN' else 1 for k in d['Label']]
d.pop('Label')


# Computing mutual information
print('Computing mutual information...')

discrete_features = [pd.api.types.is_integer_dtype(t) for t in d.dtypes]
mi_scores = mutual_info_classif(d, y, discrete_features=discrete_features, random_state=0, n_jobs=-1)
mi_scores = pd.Series(mi_scores, name="MI Scores", index = d.columns)
mi_scores = mi_scores.sort_values(ascending=False)
print(mi_scores)


# Metrics about the execution

print(f'\n\nMetrics')
print(getrusage(RUSAGE_SELF))

