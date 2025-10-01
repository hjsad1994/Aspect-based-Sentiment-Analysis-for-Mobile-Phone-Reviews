#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix rows that are missing commas by padding empty columns."""

import csv
from pathlib import Path
import shutil
import sys
from typing import List

DATA_FILE = Path('data') / 'Dataset Text Normalization 14k.csv'
BACKUP_FILE = Path('data') / 'Dataset Text Normalization 14k_before_padding.csv'
OUTPUT_FILE = Path('data') / 'Dataset Text Normalization 14k.csv'

EXPECTED_COLUMNS: List[str] = [
    'data', 'Pricing', 'Shipping', 'Performance', 'Battery',
    'Packaging', 'Warranty', 'Design', 'camera', 'Others'
]


def ensure_utf8_stdout() -> None:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')


def pad_row(row: List[str], expected_len: int) -> List[str]:
    if len(row) >= expected_len:
        return row[:expected_len]
    return row + [''] * (expected_len - len(row))


def main() -> None:
    ensure_utf8_stdout()

    if not DATA_FILE.exists():
        print(f"File not found: {DATA_FILE}")
        return

    print("Backing up original file...")
    shutil.copy2(DATA_FILE, BACKUP_FILE)
    print(f"Backup saved to {BACKUP_FILE}")

    expected_len = len(EXPECTED_COLUMNS)
    padded_rows = 0
    truncated_rows = 0
    total_rows = 0

    temp_file = DATA_FILE.with_suffix('.tmp')

    with DATA_FILE.open(encoding='utf-8', newline='') as src, temp_file.open('w', encoding='utf-8', newline='') as dst:
        reader = csv.reader(src)
        writer = csv.writer(dst)

        header = next(reader)
        total_rows += 1

        if len(header) != expected_len:
            print("Header does not match expected columns. Overwriting header with expected list.")
            writer.writerow(EXPECTED_COLUMNS)
        else:
            writer.writerow(header)

        for row in reader:
            total_rows += 1
            original_len = len(row)
            if original_len != expected_len:
                if original_len < expected_len:
                    row = pad_row(row, expected_len)
                    padded_rows += 1
                else:
                    row = row[:expected_len]
                    truncated_rows += 1
            writer.writerow(row)

    temp_file.replace(OUTPUT_FILE)

    print(f"Processed {total_rows - 1} data rows.")
    print(f"Rows padded: {padded_rows}")
    if truncated_rows:
        print(f"Rows truncated: {truncated_rows}")
    print("Done. Updated dataset saved.")


if __name__ == '__main__':
    main()
