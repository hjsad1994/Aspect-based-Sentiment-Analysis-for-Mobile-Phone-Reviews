#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to process CSV files and extract 'data' and 'Audio' columns.
Handles missing files, missing columns, and various data formats.
"""

import pandas as pd
import logging
import os
from pathlib import Path
from typing import List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('process_audio_data.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def process_csv_file(file_path: str) -> Tuple[pd.DataFrame, int]:
    """
    Process a single CSV file and extract 'data' and 'Audio' columns.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Tuple of (DataFrame with extracted columns, number of records processed)
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"File không tồn tại: {file_path}")
            return pd.DataFrame(), 0
        
        # Read CSV file
        logger.info(f"Đang đọc file: {file_path}")
        df = pd.read_csv(file_path, encoding='utf-8')
        
        initial_records = len(df)
        logger.info(f"Số bản ghi trong file: {initial_records}")
        
        # Check for required columns
        available_columns = df.columns.tolist()
        logger.info(f"Các cột có trong file: {available_columns}")
        
        result_df = pd.DataFrame()
        
        # Extract 'data' column
        if 'data' in available_columns:
            result_df['data'] = df['data']
            logger.info(f"✓ Đã trích xuất cột 'data'")
        else:
            logger.warning(f"⚠ Cột 'data' không tồn tại trong file {file_path}")
            result_df['data'] = None
        
        # Extract 'Audio' column
        if 'Audio' in available_columns:
            result_df['Audio'] = df['Audio']
            logger.info(f"✓ Đã trích xuất cột 'Audio'")
        else:
            logger.warning(f"⚠ Cột 'Audio' không tồn tại trong file {file_path}. Tạo cột rỗng.")
            result_df['Audio'] = None
        
        # Remove rows where both columns are empty/null
        initial_count = len(result_df)
        result_df = result_df.dropna(how='all')
        final_count = len(result_df)
        
        if initial_count != final_count:
            logger.info(f"Đã loại bỏ {initial_count - final_count} dòng trống")
        
        logger.info(f"✓ Xử lý thành công: {final_count} bản ghi từ {file_path}")
        return result_df, final_count
        
    except pd.errors.EmptyDataError:
        logger.error(f"File rỗng hoặc không có dữ liệu: {file_path}")
        return pd.DataFrame(), 0
    except pd.errors.ParserError as e:
        logger.error(f"Lỗi phân tích CSV tại {file_path}: {str(e)}")
        return pd.DataFrame(), 0
    except Exception as e:
        logger.error(f"Lỗi không xác định khi xử lý {file_path}: {str(e)}")
        return pd.DataFrame(), 0


def merge_and_save_data(dataframes: List[pd.DataFrame], output_file: str) -> bool:
    """
    Merge multiple DataFrames and save to CSV file.
    
    Args:
        dataframes: List of DataFrames to merge
        output_file: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Filter out empty DataFrames
        valid_dataframes = [df for df in dataframes if not df.empty]
        
        if not valid_dataframes:
            logger.error("Không có dữ liệu hợp lệ để ghi vào file output")
            return False
        
        # Concatenate all DataFrames
        logger.info(f"Đang gộp {len(valid_dataframes)} DataFrame...")
        merged_df = pd.concat(valid_dataframes, ignore_index=True)
        
        total_records = len(merged_df)
        logger.info(f"Tổng số bản ghi sau khi gộp: {total_records}")
        
        # Save to CSV
        logger.info(f"Đang lưu dữ liệu vào {output_file}...")
        merged_df.to_csv(output_file, index=False, encoding='utf-8')
        
        logger.info(f"✓ Đã lưu thành công {total_records} bản ghi vào {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Lỗi khi gộp và lưu dữ liệu: {str(e)}")
        return False


def main():
    """Main function to process all CSV files."""
    
    logger.info("=" * 80)
    logger.info("BẮT ĐẦU XỬ LÝ DỮ LIỆU AUDIO")
    logger.info("=" * 80)
    
    # Define input files
    base_path = "D:/AI_Tranning/trainning_data_split/phase_1"
    input_files = [
        os.path.join(base_path, "sub_phase_1/sub_phase_1.csv"),
        os.path.join(base_path, "sub_phase_2/sub_phase_2.csv"),
        os.path.join(base_path, "sub_phase_3/sub_phase_3.csv")
    ]
    
    # Output file
    output_file = "D:/AI_Tranning/processed_audio_data.csv"
    
    logger.info(f"Số file cần xử lý: {len(input_files)}")
    logger.info(f"File output: {output_file}")
    logger.info("-" * 80)
    
    # Process each file
    all_dataframes = []
    total_processed = 0
    
    for idx, file_path in enumerate(input_files, 1):
        logger.info(f"\n[{idx}/{len(input_files)}] Xử lý file: {file_path}")
        df, count = process_csv_file(file_path)
        
        if not df.empty:
            all_dataframes.append(df)
            total_processed += count
            logger.info(f"✓ Đã xử lý {count} bản ghi từ file {idx}")
        else:
            logger.warning(f"⚠ Không có dữ liệu từ file {idx}")
        
        logger.info("-" * 80)
    
    # Merge and save
    logger.info(f"\nTổng số bản ghi đã xử lý: {total_processed}")
    
    if all_dataframes:
        success = merge_and_save_data(all_dataframes, output_file)
        
        if success:
            logger.info("\n" + "=" * 80)
            logger.info("✓ HOÀN THÀNH XỬ LÝ DỮ LIỆU THÀNH CÔNG!")
            logger.info("=" * 80)
            
            # Display summary
            logger.info(f"\nTÓM TẮT:")
            logger.info(f"  - Số file đã xử lý: {len(input_files)}")
            logger.info(f"  - Số file hợp lệ: {len(all_dataframes)}")
            logger.info(f"  - Tổng số bản ghi: {total_processed}")
            logger.info(f"  - File output: {output_file}")
        else:
            logger.error("\n✗ Lỗi khi lưu file output!")
    else:
        logger.error("\n✗ Không có dữ liệu nào để xử lý!")
    
    logger.info("\nKiểm tra file log để biết chi tiết: process_audio_data.log")


if __name__ == "__main__":
    main()
