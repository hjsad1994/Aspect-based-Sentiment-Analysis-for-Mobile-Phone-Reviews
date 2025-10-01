#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utility to verify column counts in the dataset CSV."""

import csv
from pathlib import Path
from typing import List, Tuple
import sys

def main():
    path = Path('data') / 'Dataset Text Normalization 14k.csv'
    if not path.exists():
        print(f"File not found: {path}")
        return

    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    counts = {}
    inconsistent: List[Tuple[int, int, List[str]]] = []

    with path.open(encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        expected = len(header)
        for idx, row in enumerate(reader, start=2):
            cols = len(row)
            counts[cols] = counts.get(cols, 0) + 1
            if cols != expected:
                inconsistent.append((idx, cols, row))

    print(f"Header column count: {expected}")
    print("Column count frequencies:")
    for cols, freq in sorted(counts.items()):
        print(f"  {cols}: {freq}")

    print(f"\nRows with incorrect column count: {len(inconsistent)}")
    for idx, cols, row in inconsistent[:10]:
        print(f"Row {idx} has {cols} columns -> {row}")

if __name__ == '__main__':
    main()
