#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verification script to show examples of text normalization
"""

import pandas as pd
import sys

# Set UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')

def main():
    # Load both files
    df_orig = pd.read_csv('data/Dataset Text Normalization 14k.csv')
    df_norm = pd.read_csv('data/Dataset Text Normalization 14k_normalized.csv')
    
    print("=" * 80)
    print("TEXT NORMALIZATION VERIFICATION")
    print("=" * 80)
    
    # Find rows where changes occurred
    changes_found = 0
    examples_shown = 0
    max_examples = 5
    
    for idx in range(min(100, len(df_orig))):  # Check first 100 rows
        orig_text = str(df_orig.loc[idx, 'data'])
        norm_text = str(df_norm.loc[idx, 'data'])
        
        if orig_text != norm_text:
            changes_found += 1
            if examples_shown < max_examples:
                print(f"\nExample {examples_shown + 1} (Row {idx + 2}):")
                print("-" * 80)
                print(f"ORIGINAL: {orig_text[:200]}")
                print(f"NORMALIZED: {norm_text[:200]}")
                examples_shown += 1
    
    print("\n" + "=" * 80)
    print(f"Total changes found in first 100 rows: {changes_found}")
    print(f"Total rows in dataset: {len(df_orig)}")
    print("=" * 80)
    
    # Show some statistics about the KEY.csv mappings used
    key_df = pd.read_csv('data/KEY.csv')
    print(f"\nTotal replacement mappings in KEY.csv: {len(key_df)}")
    print("\nSample mappings:")
    for i, row in key_df.head(10).iterrows():
        print(f"  '{row['ACol']}' → '{row['BCol']}'")

if __name__ == "__main__":
    main()

