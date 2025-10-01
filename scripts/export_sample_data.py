#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to export 20 sample rows from normalized dataset
Xuất 20 dữ liệu mẫu từ dataset đã được chuẩn hóa
"""

import pandas as pd
import os
import sys

# Set UTF-8 encoding for console output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def export_sample_data(input_file: str, output_file: str, num_rows: int = 20):
    """
    Export sample rows from the normalized dataset
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
        num_rows: Number of rows to export (default: 20)
    """
    print(f"Đang đọc dữ liệu từ: {input_file}")
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    print(f"Tổng số dòng trong dataset: {len(df)}")
    print(f"Số cột: {len(df.columns)}")
    print(f"Tên các cột: {list(df.columns)}")
    
    # Get first num_rows rows (including header)
    df_sample = df.head(num_rows)
    
    print(f"\nĐang xuất {num_rows} dòng đầu tiên...")
    
    # Save to output file
    df_sample.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"Hoàn thành! Đã xuất dữ liệu ra file: {output_file}")
    print(f"\nThông tin file xuất:")
    print(f"  - Số dòng dữ liệu: {len(df_sample)}")
    print(f"  - Số cột: {len(df_sample.columns)}")
    print(f"  - Kích thước file: {os.path.getsize(output_file) / 1024:.2f} KB")

def main():
    """Main function"""
    # Define file paths
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(base_path, 'data', 'Dataset Text Normalization 14k_normalized.csv')
    output_file = os.path.join(base_path, 'data', 'Sample_20_rows_normalized.csv')
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Lỗi: Không tìm thấy file {input_file}")
        return
    
    print("=" * 80)
    print("XUẤT DỮ LIỆU MẪU - EXPORT SAMPLE DATA")
    print("=" * 80)
    
    # Export 20 rows
    export_sample_data(input_file, output_file, num_rows=20)
    
    print("\n" + "=" * 80)
    print("PREVIEW - Xem trước 5 dòng đầu tiên:")
    print("=" * 80)
    
    # Show preview
    df_preview = pd.read_csv(output_file)
    print(df_preview.head().to_string(max_colwidth=60))

if __name__ == "__main__":
    main()

