#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Normalize icon/emoticon usage in Dataset Text Normalization 14k."""

from __future__ import annotations

import os
import sys
from typing import Dict

import pandas as pd


def ensure_utf8_stdout() -> None:
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")


def load_icon_mapping(icon_file: str) -> Dict[str, str]:
    print(f"Đang đọc bảng Icon từ: {icon_file}")
    df = pd.read_csv(icon_file, encoding="utf-8")

    mapping: Dict[str, str] = {}
    for _, row in df.iterrows():
        icon = str(row.get("A", "")).strip()
        replacement = str(row.get("B", "")).strip()
        if not icon or not replacement or icon.lower() == "nan" or replacement.lower() == "nan":
            continue
        # Ưu tiên mapper cuối cùng nếu có trùng
        mapping[icon] = replacement

    print(f"Tổng số biểu tượng cần thay thế: {len(mapping)}")
    return mapping


def normalize_icons_in_text(text: object, mapping: Dict[str, str]) -> object:
    if pd.isna(text):
        return text

    normalized = str(text)
    for icon, replacement in mapping.items():
        if icon in normalized:
            normalized = normalized.replace(icon, replacement)
    return normalized


def process_dataset(dataset_file: str, icon_file: str, output_file: str) -> None:
    print(f"\nĐang đọc dataset: {dataset_file}")
    df = pd.read_csv(dataset_file, encoding="utf-8")
    print(f"Kích thước dataset: {df.shape}")

    mapping = load_icon_mapping(icon_file)

    text_columns = [col for col in df.columns if df[col].dtype == "object"]
    print(f"Các cột dạng văn bản sẽ được chuẩn hoá: {text_columns}")

    total_replacements = 0
    for column in text_columns:
        def _normalize_cell(cell: object) -> object:
            nonlocal total_replacements
            if pd.isna(cell):
                return cell
            original = str(cell)
            normalized = normalize_icons_in_text(original, mapping)
            if normalized != original:
                total_replacements += 1
            return normalized

        df[column] = df[column].apply(_normalize_cell)

    print(f"Số ô dữ liệu đã thay đổi: {total_replacements}")

    print(f"\nĐang lưu kết quả chuẩn hoá vào: {output_file}")
    df.to_csv(output_file, index=False, encoding="utf-8")
    print("Hoàn thành chuẩn hoá biểu tượng!")


def main() -> None:
    ensure_utf8_stdout()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)

    dataset_file = os.path.join(project_root, "data", "Dataset Text Normalization 14k.csv")
    icon_file = os.path.join(project_root, "data", "Icon.csv")
    output_file = os.path.join(project_root, "data", "Dataset Text Normalization 14k_icon_normalized.csv")

    if not os.path.exists(dataset_file):
        print(f"Không tìm thấy dataset: {dataset_file}")
        return
    if not os.path.exists(icon_file):
        print(f"Không tìm thấy file icon: {icon_file}")
        return

    process_dataset(dataset_file, icon_file, output_file)

    print("\n========================================")
    print(f"File đã được lưu tại: {output_file}")
    print("========================================")


if __name__ == "__main__":
    main()
