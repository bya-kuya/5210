# -*- coding:utf-8 -*-
import re
import pandas as pd
from fuzzywuzzy import fuzz

def preprocess_text(text: str) -> str:
    """
    Preprocesses the input text by converting it to lowercase,
    removing special characters, and stripping whitespace.

    Parameters:
    text (str): The input text to be preprocessed.

    Returns:
    str: The preprocessed text.
    """
    text = text.lower()
    text = re.sub(r'[\W_]+', ' ', text)
    text = text.strip()
    return text


def format_zip_code(zip_code):
    """
    Formats a zip code to ensure it is a string and contains exactly 5 digits.

    Parameters:
    zip_code (str or int): The zip code to be formatted.

    Returns:
    str: The formatted zip code.
    """
    zip_code = str(zip_code)
    return zip_code[:5].zfill(5)  # Ensure 5 characters


def standardize_address(address):
    """
    Standardizes and cleans the address, gracefully handling NaN values.

    Parameters:
    address (str or pd.Series): The address to be standardized and cleaned.

    Returns:
    str: The standardized and cleaned address, or an empty string if address is NaN.
    """
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


def generate_block_keys(df):
    """
    Generate block keys by combining several fields.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the fields for creating block keys.

    Returns:
    pd.DataFrame: The DataFrame with a new column 'block_key' containing the generated block keys.
    """
    df['block_key'] = df.apply(lambda x:
                               (x['name'][0].lower() if pd.notna(x['name']) and x['name'] != "" else '0') +
                               "_" + (x['state'].upper() if pd.notna(x['state']) else 'Unknown') +
                               "_" + (x['city'][0].lower() if pd.notna(x['city']) and x['city'] != "" else '0') +
                               "_" + (str(x['zip_code'])[:5] if pd.notna(x['zip_code']) else '00000'), axis=1)
    return df


def find_best_match(query, candidate_choices, minimum_score):
    """
    Searches for the best match for a query string from a set of candidate choices based on a similarity score.

    Args:
        query (str): The query string to be matched.
        candidate_choices (dict): A dictionary of candidate strings with their indices as keys.
        minimum_score (int): The score threshold above which a match is considered valid.

    Returns:
        tuple: A tuple containing the index of the best matching string and the highest similarity score.
    """
    best_result = {"index": None, "score": None}

    for index, candidate in candidate_choices.items():
        current_score = fuzz.WRatio(query, candidate)
        if current_score >= minimum_score:
            if best_result["score"] is None or current_score > best_result["score"]:
                best_result["score"] = current_score
                best_result["index"] = index

    return best_result["index"], best_result["score"]


def perform_fuzzy_matching(source_df, target_df, threshold=85):
    """
    Perform fuzzy matching between two dataframes using specified blocking keys to reduce the comparison space.

    Args:
        source_df (DataFrame): Source dataframe.
        target_df (DataFrame): Target dataframe.
        threshold (int): The similarity score threshold to determine a valid match.

    Returns:
        DataFrame: A dataframe containing the matching results with entity IDs and scores.
    """
    match_results = []
    common_blocks = set(source_df['block_key']).intersection(target_df['block_key'])

    for block in common_blocks:
        source_block_df = source_df[source_df['block_key'] == block]
        target_block_df = target_df[target_df['block_key'] == block]

        for _, source_row in source_block_df.iterrows():
            best_match_idx, best_match_score = find_best_match(
                query=source_row['combined'],
                candidate_choices={idx: row['combined'] for idx, row in target_block_df.iterrows()},
                minimum_score=threshold
            )

            if best_match_score:
                match_data = {
                    'source_entity_id': source_row['entity_id'],
                    'target_entity_id': target_block_df.loc[best_match_idx]['business_id'],
                    'confidence_score': best_match_score
                }
                match_results.append(match_data)

    return pd.DataFrame(match_results)
