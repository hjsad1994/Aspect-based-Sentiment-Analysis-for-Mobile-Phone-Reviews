# Vietnamese Text Normalization Scripts

## Overview
This directory contains Python scripts for normalizing Vietnamese text by replacing abbreviations, slang, and spelling errors with standard Vietnamese expressions.

## Scripts

### 1. `text_normalization.py`
Main script that performs text normalization on the dataset.

**Features:**
- Loads replacement mappings from `KEY.csv` (Column A → Column B)
- Processes all text columns in the dataset
- Uses case-insensitive word boundary matching
- Handles both single words and multi-word phrases
- Outputs normalized dataset with `_normalized` suffix

**Usage:**
```bash
python scripts/text_normalization.py
```

**Input:**
- `data/KEY.csv` - Mapping file with columns:
  - `ACol`: Words to replace (abbreviations, slang, errors)
  - `BCol`: Standard Vietnamese replacements
- `data/Dataset Text Normalization 14k.csv` - Dataset to normalize

**Output:**
- `data/Dataset Text Normalization 14k_normalized.csv` - Normalized dataset

### 2. `verify_normalization.py`
Verification script that shows examples of applied normalizations.

**Usage:**
```bash
python scripts/verify_normalization.py
```

**Output:**
- Shows side-by-side comparison of original vs normalized text
- Displays statistics about changes made
- Lists sample mappings from KEY.csv

### 3. `export_sample_data.py`
Export script to create a sample CSV file with 20 rows from the normalized dataset.

**Usage:**
```bash
python scripts/export_sample_data.py
```

**Output:**
- `data/Sample_20_rows_normalized.csv` - CSV file containing 20 sample rows
- Displays file statistics and preview of first 5 rows

## Replacement Examples

The script replaces:
- `update` → `cập nhật`
- `cs kh` → `chăm sóc khách hàng`
- `ok` → `tốt`
- `thanks` → `cảm ơn`
- `sp` → `sản phẩm`
- `dt` → `điện thoại`
- And 60+ more mappings...

## Requirements

Install required packages:
```bash
pip install -r requirements.txt
```

Required packages:
- pandas >= 2.0.0
- numpy >= 1.24.0

## Notes

- The script uses word boundary matching to avoid partial replacements
- Replacements are case-insensitive
- Multi-word phrases are prioritized over single words
- All text columns in the dataset are processed
- Original file is preserved; output is saved separately

