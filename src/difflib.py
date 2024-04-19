import pandas as pd
import re
from difflib import SequenceMatcher

def clean_text(text):
    """Lowercase, remove special characters, and strip whitespace."""
    text = text.lower()
    text = re.sub(r'[\W_]+', ' ', text)  # Replace all non-word characters with space
    return text.strip()

def standardize_zip_code(zip_code):
    """Ensure zip code is a string, truncate or pad to 5 digits."""
    zip_code = str(zip_code)
    return zip_code[:5].zfill(5)  # Pad or truncate to ensure 5 characters

def clean_address(address):
    """Standardize and clean the address, handling NaN values gracefully."""
    if pd.isna(address):
        return ""
    address = address.lower()
    address = re.sub(r'\bstreet\b', 'st', address)
    address = re.sub(r'\broad\b', 'rd', address)
    address = re.sub(r'\bavenue\b', 'ave', address)
    address = re.sub(r'\bdrive\b', 'dr', address)
    address = re.sub(r'[^a-zA-Z0-9\s]', '', address)
    address = re.sub(r'\s+', ' ', address).strip()
    return address

def create_enhanced_block_keys(df):
    """Generate block keys by combining several fields."""
    df['block_key'] = df.apply(lambda x:
                                (x['name'][0].lower() if pd.notna(x['name']) and x['name'] != "" else '0') +
                                "_" + (x['state'].upper() if pd.notna(x['state']) else 'Unknown') +
                                "_" + (x['city'][0].lower() if pd.notna(x['city']) and x['city'] != "" else '0') +
                                "_" + (str(x['zip_code'])[:5] if pd.notna(x['zip_code']) else '00000'), axis=1)
    return df

def fuzzy_match_with_difflib(left_df, right_df, threshold=0.80):
    results = []
    common_blocks = set(left_df['block_key']).intersection(set(right_df['block_key']))

    for block in common_blocks:
        left_block = left_df[left_df['block_key'] == block]
        right_block = right_df[right_df['block_key'] == block]
        for _, left_row in left_block.iterrows():
            best_match = None
            best_score = threshold
            for _, right_row in right_block.iterrows():
                score = SequenceMatcher(None, left_row['combined'], right_row['combined']).ratio()
                if score > best_score:
                    best_score = score
                    best_match = right_row['business_id']

            if best_match:
                match_data = {
                    'left_id': left_row['entity_id'],
                    'right_id': best_match,
                    'match_score': best_score
                }
                results.append(match_data)

    return pd.DataFrame(results)

