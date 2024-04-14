#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import re

def clean_text(text):
    """Lowercase, remove special characters, and strip whitespace."""
    import re
    text = text.lower()
    text = re.sub(r'[\W_]+', ' ', text)  # Replace all non-word characters with space
    return text.strip()

# In[ ]:


def standardize_zip_code(zip_code):
    """Ensure zip code is a string, truncate or pad to 5 digits."""
    zip_code = str(zip_code)
    return zip_code[:5].zfill(5)  # Pad or truncate to ensure 5 characters

# In[ ]:

import pandas as pd
import re

def clean_address(address):
    """Standardize and clean the address, handling NaN values gracefully."""
    if pd.isna(address):
        return ""  # Return an empty string or some other placeholder for NaN addresses
    address = address.lower()  # Convert to lowercase
    address = re.sub(r'\bstreet\b', 'st', address)
    address = re.sub(r'\broad\b', 'rd', address)
    address = re.sub(r'\bavenue\b', 'ave', address)
    address = re.sub(r'\bdrive\b', 'dr', address)
    address = re.sub(r'[^a-zA-Z0-9\s]', '', address)  # Remove non-alphanumeric characters except space
    address = re.sub(r'\s+', ' ', address).strip()  # Replace multiple spaces with a single space
    return address

# In[ ]:


def create_enhanced_block_keys(df):
    """Generate block keys by combining several fields."""
    df['block_key'] = df.apply(lambda x: 
                                (x['name'][0].lower() if pd.notna(x['name']) and x['name'] != "" else '0') + 
                                "_" + (x['state'].upper() if pd.notna(x['state']) else 'Unknown') +
                                "_" + (x['city'][0].lower() if pd.notna(x['city']) and x['city'] != "" else '0') +
                                "_" + (str(x['zip_code'])[:5] if pd.notna(x['zip_code']) else '00000'), axis=1)
    return df


# In[ ]:

from rapidfuzz import process, fuzz

def fuzzy_match_with_rapidfuzz(left_df, right_df, threshold=85):
    results = []
    # Identify common blocks to minimize comparisons
    common_blocks = set(left_df['block_key']).intersection(set(right_df['block_key']))
    
    # Perform matching within each common block
    for block in common_blocks:
        left_block = left_df[left_df['block_key'] == block]
        right_block = right_df[right_df['block_key'] == block]
        for _, left_row in left_block.iterrows():
            # Using RapidFuzz to find the best match in the right block
            best_match = process.extractOne(
                left_row['combined'], 
                {idx: row['combined'] for idx, row in right_block.iterrows()}, 
                scorer=fuzz.WRatio,
                score_cutoff=threshold
            )
            if best_match:
                # Accessing details of the best match
                match_data = {
                    'left_dataset': left_row['entity_id'],
                    'right_dataset': right_block.loc[best_match[2]]['business_id'],
                    'confidence_score': best_match[1]
                }
                results.append(match_data)
                
    return pd.DataFrame(results)

