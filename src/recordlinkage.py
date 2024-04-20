#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import recordlinkage
from recordlinkage.preprocessing import clean, phonetic


# In[2]:


def preprocess_data(df):
    for column in df.columns:
        if df[column].dtype == 'object':
            df[column] = df[column].str.replace(r'[^a-zA-Z0-9]', '', regex=True).str.lower()
    return df


# In[ ]:




