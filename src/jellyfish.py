#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import jellyfish


# In[ ]:


# Function to calculate similarity score
def calculate_similarity(row):
    left_name = row['name_x']
    left_address = row['address_x']
    right_name = row['name_y']
    right_address = row['address_y']
    
    name_similarity = jellyfish.jaro_winkler_similarity(left_name.lower(), right_name.lower())
    address_similarity = jellyfish.jaro_winkler_similarity(left_address.lower(), right_address.lower())
    
    return (name_similarity + address_similarity) / 2

