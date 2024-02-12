# -*- coding: utf-8 -*-
"""scaling-trilogs-roberta.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19-n8SclgV9SfPh1TWJLZsl6m1ZAg0Kbo
"""
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
import json
import glob
import torch
from torch.utils.data import Dataset, DataLoader, random_split, RandomSampler, SequentialSampler
torch.manual_seed(50)

from datasets.dataset_dict import DatasetDict
from datasets import load_metric, load_dataset, Dataset 
from transformers import RobertaTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments

from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import statistics

from collections import Counter

nltk.download('punkt')
'''
#from google.colab import drive
#drive.mount('/content/drive', force_remount=True)
token_list = ["$deleted$", "$Paragraph 5 is deleted$", 
      "$Article 13 is deleted$", "$<bi>[no change]</bi>$", 
      "$[no change]$", "$no changes proposed by the Commission$",
      "$No corresponding proposal by the Commission$", "$deleted$",
      "$<bi>deleted</bi>$", "$Not amended$", "$<bi>[no change]</bi>$",
      "$<bi>[no chang</bi><bi>e]</bi>$" , "$No Change$", "$[No change]$", 
      "$no change$", "$DELETED$", "<b>$Not amended$</b>" ,
      "$[moved to Art. 1 a below]$", "$Idem$", "$No changes to COM proposal$", 
      "$no changes to the Commission's text$", "$no change to Commission text$", 
      "<i>$Unchanged$</i>", "$Unchanged$" , "$Deleted and replaced by$", "$As COM$", 
      "$AS COM$",  "$deleted (Amendment 3)$", "$Not acceptable. There is no corresponding article in the text.", 
      "$Not acceptable", "$Acceptable with modifications$", "$Not Acceptable", "$Keep the text from COM proposal$", 
      "$Need to be further discussed.$", "$Need to be further discussed.$", 
      "$Keep Council text (i.e. deletion )", "$Keep the text from COM proposal$",
      "$Not acceptable Keep the text from COM proposal", "$Acceptable$", "$reject$", 
      "$accept$", "$Amendment acceptable$", "$Not acceptable.$", "$<b>Acceptable</b>$", 
      "$<b>Not acceptable</b>$", "$Commission text retained$", "$Commission Text retained$", 
      "$(deleted)$", "$Accept EP amendment$", "$Not $Accept EP amendment$$",
      "$Merged with recital 21$", "$Deleted (merged with Article 8)$",
      "$Deleted (merged with Article 7)$",
      "$[transferred in modified form to recitals 11a-11d]$", 
      "$Point 7 has been deleted$"]

#deleted = [token for token in token_list if "deleted" in token.lower()]
#no_change = [token for token in token_list if "change" in token.lower()]
#agree = [token for token in token_list if "com" in token.lower()]

def pre_process(coms, eps, council):
  regex = r'\W+'
  html = re.compile(r'<[^>]+>')
  c = list()
  e = list()
  d = list()
  for i, j, k  in zip(coms, eps, council):
     i = re.sub("\s\s+" , " ", i)
     i = re.sub(html, " ", i)
     i = re.sub(regex, " ", i)
     j = re.sub(html , " ", j)
     j = re.sub(regex, " ", j)
     k = re.sub(html, " ", k)
     k = re.sub(regex, " ", k)
     c.append(i)
     e.append(j)
     d.append(k)
     
  return c, e, d
'''

data_base_path = '/ceph/sobaidul/data/new_legislation_final'
write_base_path = '/ceph/sobaidul/data/new_legislation_final_scaled'
model_base_path = '/work/sobaidul/trilog_classifier/trilog_training_data_all_clean/Roberta-large-upscaling-pos-new'
#!unzip /content/drive/MyDrive/trilog_training_data/upscaling-roberta.zip -d /content/drive/MyDrive/trilog_training_data

'''
def preprocess_function(batch):
    return tokenizer(batch["text"], truncation=True, padding="max_length")


def get_tokenized_data(position):
    try:
        # Explicitly specify the data type for the 'text' column
        df_dataset = pd.DataFrame(position, columns=['text'], dtype=str)
        dataset = Dataset.from_pandas(df_dataset)
        dataset = DatasetDict({'test': dataset})
        
        tokenized_data = dataset.map(preprocess_function, batched=True)
        return tokenized_data
    except Exception as e:  
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno)
  

def run_prediction(trainer,tokenized_data):
  predictions = trainer.predict(test_dataset=tokenized_data["test"])
  preds = predictions.predictions.argmax(-1)
  #print(predictions[0])
  score = (np.exp(predictions[0])/np.exp(predictions[0]).sum(-1,keepdims=True)).max(1)
  scores = (np.exp(predictions[0])/np.exp(predictions[0]).sum(-1,keepdims=True))
  #print(scores)
  return preds, score, scores

def get_scores_for_labels(scores):
  scores_0 = list()
  scores_1 = list()
  scores_2 = list()
  for i in scores:
    scores_0.append(i[0])
    scores_1.append(i[1])
    scores_2.append(i[2])


  return scores_0, scores_1, scores_2

def filename(f):
  l = f.split('/')
  return l[-1]


print('Loading Tokenizer and Model#\n')
tokenizer = RobertaTokenizer.from_pretrained("roberta-large")
model = AutoModelForSequenceClassification.from_pretrained(model_base_path, num_labels=3)


#driver code
file_list = glob.glob(f'{data_base_path}/*.csv')

print('Loading Trainer\n')
trainer = Trainer(model=model)
logf = open(f"{write_base_path}/error.log", "w")
for i in file_list:
  trilog_name = filename(i)
  try:
    df = pd.read_csv(i, sep=',')
    df.columns
    trilog_name = filename(i)
    print('Running for File: ' + trilog_name + '\n')
    df1 = df.copy()
    df1 = df1.fillna('empty')
    text_list = list(df1.text)
    #text_list = [str(x) for x in text_list]


    test_dataset = get_tokenized_data(text_list)
    predictions, probs, all_probs = run_prediction(trainer, test_dataset)
    probs_0, probs_1, probs_2 = get_scores_for_labels(all_probs)
      
    print(type(predictions))
    df['prediction'] = predictions
    df['prob'] = probs
    df['prob_0'] = probs_0
    df['prob_1'] = probs_1
    df['prob_2'] = probs_2

    df.to_csv(f'{write_base_path}/scaled_{trilog_name}', sep=',', index=False)
  except Exception as e:
    print("Exception: " + str(e))
    print("For file: " + str(trilog_name))
    logf.write("Failed to open and run {0}: {1}\n".format(str(i), str(e)))
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(exc_tb.tb_lineno)

    try:
      df = pd.read_csv(i, sep=',', encoding='unicode_escape')
      trilog_name = filename(i)
      df1 = df.copy()
      df1 = df1.fillna('')
      text_list = list(df1.text)


      test_dataset = get_tokenized_data(text_list)
      predictions, probs, all_probs = run_prediction(trainer, test_dataset)
      probs_0, probs_1, probs_2 = get_scores_for_labels(all_probs)
      df['prediction'] = predictions
      df['prob'] = probs
      df['prob_0'] = probs_0
      df['prob_1'] = probs_1
      df['prob_2'] = probs_2

      df.to_csv(f'{write_base_path}/scaled_{trilog_name}.csv', sep=',', index=False)
    except Exception as e:
      print("Exception: " + str(e))
      print("For file: " + str(trilog_name))
      logf.write("Cannot open and run with encoding parameter {0}: {1}\n".format(str(i), str(e)))

logf.close()
'''
#print('------------------FINISHED----------------')

####################################################
#combine all files

file_name = glob.glob(f'{write_base_path}/*.csv')

df_list = list()
for i in file_name:
  temp_df = pd.read_csv(i, sep=',')
  cod_name = i.split('/')[-1]
  cod_name = cod_name.split('_')[-1]
  temp_df['cod'] = [cod_name] * len(temp_df.index)
  df_list.append(temp_df)

df_all = pd.concat(df_list, ignore_index=True)
df_all.to_csv(f'{write_base_path}/final_combined.csv', sep=',', index=False)
#####################################################