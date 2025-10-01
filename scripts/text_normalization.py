#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Text Normalization Script for Vietnamese Text
Replaces abbreviations, slang, and spelling errors with standard Vietnamese expressions
using a mapping dictionary from KEY.csv
"""

import pandas as pd
import re
import os
from typing import Dict, List

def load_replacement_dict(key_file: str) -> Dict[str, str]:
    """
    Load the replacement dictionary from KEY.csv
    
    Args:
        key_file: Path to the KEY.csv file
        
    Returns:
        Dictionary mapping words to replace (ACol) to their replacements (BCol)
    """
    print(f"Loading replacement dictionary from {key_file}...")
    df = pd.read_csv(key_file)
    
    # Create dictionary from ACol to BCol
    replacement_dict = {}
    for _, row in df.iterrows():
        # Strip whitespace and handle empty values
        key = str(row['ACol']).strip()
        value = str(row['BCol']).strip()
        if key and value and key != 'nan' and value != 'nan':
            replacement_dict[key] = value
    
    print(f"Loaded {len(replacement_dict)} replacement mappings")
    return replacement_dict

def normalize_text(text: str, replacement_dict: Dict[str, str]) -> str:
    """
    Normalize text by replacing words according to the replacement dictionary
    Uses word boundary matching to avoid partial replacements
    
    Args:
        text: Text to normalize
        replacement_dict: Dictionary of replacements
        
    Returns:
        Normalized text
    """
    if pd.isna(text) or text == '':
        return text
    
    normalized = str(text)
    
    # Sort replacements by length (longest first) to handle multi-word replacements first
    sorted_replacements = sorted(replacement_dict.items(), key=lambda x: len(x[0]), reverse=True)
    
    for old_word, new_word in sorted_replacements:
        # Create regex pattern with word boundaries
        # Handle special regex characters by escaping them
        escaped_old = re.escape(old_word)
        
        # Use word boundary (\b) for single words, or flexible matching for phrases
        if ' ' in old_word:
            # For phrases, use direct replacement with case insensitive matching
            pattern = re.compile(re.escape(old_word), re.IGNORECASE)
            normalized = pattern.sub(new_word, normalized)
        else:
            # For single words, use word boundaries to avoid partial matches
            pattern = re.compile(r'\b' + escaped_old + r'\b', re.IGNORECASE)
            normalized = pattern.sub(new_word, normalized)
    
    return normalized

def process_dataset(input_file: str, output_file: str, replacement_dict: Dict[str, str]):
    """
    Process the dataset CSV file and normalize all text columns
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
        replacement_dict: Dictionary of replacements
    """
    print(f"\nReading dataset from {input_file}...")
    df = pd.read_csv(input_file)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Process each column (normalize all text columns)
    total_cells = 0
    for column in df.columns:
        if df[column].dtype == 'object':  # Text columns
            print(f"\nNormalizing column: {column}")
            df[column] = df[column].apply(lambda x: normalize_text(x, replacement_dict))
            total_cells += df[column].notna().sum()
    
    print(f"\nTotal cells processed: {total_cells}")
    
    # Save the normalized dataset
    print(f"Saving normalized dataset to {output_file}...")
    df.to_csv(output_file, index=False, encoding='utf-8')
    print("Normalization complete!")

def main():
    """Main function to run the text normalization"""
    # Define file paths
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    key_file = os.path.join(base_path, 'data', 'KEY.csv')
    input_file = os.path.join(base_path, 'data', 'Dataset Text Normalization 14k.csv')
    output_file = os.path.join(base_path, 'data', 'Dataset Text Normalization 14k_normalized.csv')
    
    # Check if files exist
    if not os.path.exists(key_file):
        print(f"Error: KEY.csv not found at {key_file}")
        return
    
    if not os.path.exists(input_file):
        print(f"Error: Dataset file not found at {input_file}")
        return
    
    # Load replacement dictionary
    replacement_dict = load_replacement_dict(key_file)
    
    # Process dataset
    process_dataset(input_file, output_file, replacement_dict)
    
    print(f"\n{'='*60}")
    print(f"Output saved to: {output_file}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

