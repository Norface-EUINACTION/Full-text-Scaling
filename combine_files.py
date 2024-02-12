import datetime
import os
import time
import sys
import re
import numpy as np
import random
import pandas as pd
import nltk
import numpy as np
import glob 
data_base_path = '/ceph/sobaidul/data/aligned_finals'
write_base_path = '/ceph/sobaidul/data/proposal_final_scaling'

file_name = glob.glob(f'{write_base_path}/*.csv')




df_list = list()
for i in file_name:
  temp_df = pd.read_csv(i, sep=',')
  if 'COM_match.1' in temp_df.columns:
    temp_df  = temp_df.rename(columns={'COM_match.1': 'COM_match_final'})
    print('Replace COM value for: ' + i.split('/')[-1])

  if 'EP_match.1' in temp_df.columns:
    temp_df  = temp_df .rename(columns={'EP_match.1': 'EP_match_final'})
    print('Replace EP value for: ' + i.split('/')[-1])

  if 'Council_match.1' in temp_df.columns:
    temp_df  = temp_df .rename(columns={'Council_match.1': 'Council_match_final'})
    print('Replace Council value for: ' + i.split('/')[-1])

  if 'Proposal_match' in temp_df.columns:
    temp_df  = temp_df .rename(columns={'Proposal_match': 'Proposal_match_final'})
    print('Replace Proposal Match value for: ' + i.split('/')[-1])

  df_list.append(temp_df)

df_all = pd.concat(df_list, ignore_index=True)
df_all.to_csv(f'{write_base_path}/proposal_final_diff.csv', sep=',', index=False)
#####################################################'''
