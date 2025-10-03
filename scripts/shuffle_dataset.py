#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Shuffle rows in a CSV dataset while preserving the header."""

from __future__ import annotations

import argparse
import csv
import os
import random
import sys
import tempfile
from pathlib import Path
from typing import List, Sequence


def ensure_utf8_stdout() -> None:
    if sys.stdout and sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")


def read_dataset(path: Path) -> tuple[List[str], List[List[str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ValueError("Dataset is empty") from exc
        rows = list(reader)
    return header, rows


def write_dataset(path: Path, header: Sequence[str], rows: Sequence[Sequence[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def shuffle_rows(rows: List[List[str]], seed: int | None) -> None:
    rng = random.Random(seed) if seed is not None else random
    rng.shuffle(rows)


def shuffle_dataset(input_path: Path, output_path: Path | None, seed: int | None) -> Path:
    header, rows = read_dataset(input_path)
    if not rows:
        raise ValueError("Dataset contains only the header row; nothing to shuffle.")

    shuffle_rows(rows, seed)

    if output_path is None or output_path == input_path:
        fd, tmp_name = tempfile.mkstemp(dir=input_path.parent, suffix=input_path.suffix)
        os.close(fd)
        tmp_path = Path(tmp_name)
        try:
            write_dataset(tmp_path, header, rows)
            tmp_path.replace(input_path)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
        return input_path

    if output_path.exists() and output_path.is_dir():
        output_path = output_path / input_path.name

    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_dataset(output_path, header, rows)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Shuffle rows in a CSV dataset.")
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the CSV dataset to shuffle.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path. Defaults to shuffling in place.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for reproducibility.",
    )
    return parser.parse_args()


def main() -> None:
    ensure_utf8_stdout()
    args = parse_args()

    input_path: Path = args.input
    output_path: Path | None = args.output
    seed: int | None = args.seed

    if not input_path.exists():
        print(f"File not found: {input_path}")
        sys.exit(1)

    try:
        destination = shuffle_dataset(input_path, output_path, seed)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    print(f"✅ Shuffled {input_path} -> {destination}")


if __name__ == "__main__":
    main()
