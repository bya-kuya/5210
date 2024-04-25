#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import jellyfish


# In[ ]:


#Clean the data and then merge the left and right csv
def clean_and_merge(left_df, right_df):
    # Fill NaN values with empty strings
    left_df['address'] = left_df['address'].fillna('')
    right_df['address'] = right_df['address'].fillna('')

    # Convert 'postal_code' to string type to prevent the potential float issue
    left_df['postal_code'] = left_df['postal_code'].astype(str)
    right_df['zip_code'] = right_df['zip_code'].astype(str)
    
    # Create 'zip_prefix' column for both dataframes
    left_df['zip_prefix'] = left_df['postal_code'].str[:5]
    right_df['zip_prefix'] = right_df['zip_code'].str[:5]

    # Merge datasets on 'zip_prefix'
    merged_df = pd.merge(left_df, right_df, how='inner', on='zip_prefix')

    return merged_df


# In[ ]:


def calculate_similarity(row):
    left_name = row['name_x']
    left_address = row['address_x']
    right_name = row['name_y']
    right_address = row['address_y']
    
    name_similarity = jellyfish.jaro_winkler_similarity(left_name.lower(), right_name.lower())
    address_similarity = jellyfish.jaro_winkler_similarity(left_address.lower(), right_address.lower())
    
    return (name_similarity + address_similarity) / 2


# In[ ]:


# Function to calculate similarity score
#Mainly think of comparing the rate of similarity between the name, and the address using the jellyfish package
#And return the average of the similarity rate
def find_high_confidence_matches(merged_df, threshold=0.80):
    # Calculate similarity score
    merged_df['similarity_score'] = merged_df.apply(calculate_similarity, axis=1)

    # Filter high confidence outcomes
    high_confidence_matches = merged_df[merged_df['similarity_score'] > threshold]

    # Selecting only the desired columns
    high_confidence_matches = high_confidence_matches[['entity_id', 'business_id', 'similarity_score']]
    
    return high_confidence_matches
