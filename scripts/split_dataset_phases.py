#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Split Dataset.csv into labeling phases and sub-phases."""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import List

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "trainning_data_split" / "Dataset.csv"
PHASE_1_DIR = BASE_DIR / "trainning_data_split" / "phase_1"
PHASE_2_DIR = BASE_DIR / "trainning_data_split" / "phase_2"

PHASE_1_SUBPHASE_COUNT = 5
PHASE_1_SUBPHASE_SIZE = 200

TARGET_PHASE2_CHUNK = 3500  # desired chunk size for phase 2
MIN_PHASE2_CHUNK = 3000
MAX_PHASE2_CHUNK = 4000


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def compute_phase2_chunk_sizes(total_rows: int) -> List[int]:
    if total_rows <= 0:
        return []

    chunk_count = max(1, round(total_rows / TARGET_PHASE2_CHUNK))

    # Adjust to keep chunk sizes within desired range when possible
    while chunk_count > 1 and total_rows / chunk_count > MAX_PHASE2_CHUNK:
        chunk_count += 1
    while chunk_count > 1 and total_rows / chunk_count < MIN_PHASE2_CHUNK:
        chunk_count -= 1

    base = total_rows // chunk_count
    remainder = total_rows % chunk_count

    chunk_sizes = [base + (1 if i < remainder else 0) for i in range(chunk_count)]

    # If last chunk falls below minimum, merge with previous chunk if possible
    if len(chunk_sizes) >= 2 and chunk_sizes[-1] < MIN_PHASE2_CHUNK:
        chunk_sizes[-2] += chunk_sizes[-1]
        chunk_sizes.pop()

    return chunk_sizes


def split_phase_1(df: pd.DataFrame) -> int:
    ensure_dir(PHASE_1_DIR)
    phase1_rows = PHASE_1_SUBPHASE_COUNT * PHASE_1_SUBPHASE_SIZE

    phase1_df = df.iloc[:phase1_rows]

    for idx in range(PHASE_1_SUBPHASE_COUNT):
        start = idx * PHASE_1_SUBPHASE_SIZE
        end = start + PHASE_1_SUBPHASE_SIZE
        sub_df = phase1_df.iloc[start:end]

        sub_dir = PHASE_1_DIR / f"sub_phase_{idx + 1}"
        ensure_dir(sub_dir)
        output_file = sub_dir / f"sub_phase_{idx + 1}.csv"
        sub_df.to_csv(output_file, index=False, encoding="utf-8")
        print(f"Phase 1 - Sub-phase {idx + 1}: {len(sub_df)} rows -> {output_file}")

    return phase1_rows


def split_phase_2(df: pd.DataFrame, start_row: int) -> None:
    ensure_dir(PHASE_2_DIR)
    phase2_df = df.iloc[start_row:]
    total_phase2 = len(phase2_df)

    chunk_sizes = compute_phase2_chunk_sizes(total_phase2)

    print(f"Phase 2 total rows: {total_phase2}")
    print(f"Phase 2 chunk sizes: {chunk_sizes}")

    current_index = 0
    for idx, size in enumerate(chunk_sizes, start=1):
        sub_df = phase2_df.iloc[current_index:current_index + size]
        sub_dir = PHASE_2_DIR / f"chunk_{idx}"
        ensure_dir(sub_dir)
        output_file = sub_dir / f"phase_2_chunk_{idx}.csv"
        sub_df.to_csv(output_file, index=False, encoding="utf-8")
        print(f"Phase 2 - Chunk {idx}: {len(sub_df)} rows -> {output_file}")
        current_index += size


def main() -> None:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}")

    print(f"Loading dataset from {DATASET_PATH}...")
    df = pd.read_csv(DATASET_PATH, encoding="utf-8")
    total_rows = len(df)
    print(f"Total rows in dataset: {total_rows}")

    phase1_rows = split_phase_1(df)
    split_phase_2(df, phase1_rows)

    print("\nDataset has been split into phase_1 and phase_2 directories.")


if __name__ == "__main__":
    main()
