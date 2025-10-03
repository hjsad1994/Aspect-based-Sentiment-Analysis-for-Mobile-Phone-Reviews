#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to add 'Audio' column to Dataset.csv file.
Creates a backup before modifying the original file.
"""

import pandas as pd
import logging
import os
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('add_audio_column.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def add_audio_column(file_path: str, backup: bool = True) -> bool:
    """
    Add 'Audio' column to the CSV file.
    
    Args:
        file_path: Path to the CSV file
        backup: Whether to create a backup before modifying (default: True)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"File không tồn tại: {file_path}")
            return False
        
        logger.info("=" * 80)
        logger.info("BẮT ĐẦU THÊM CỘT 'AUDIO' VÀO DATASET")
        logger.info("=" * 80)
        logger.info(f"File đầu vào: {file_path}")
        
        # Create backup if requested
        if backup:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = file_path.replace('.csv', f'_backup_{timestamp}.csv')
            logger.info(f"Đang tạo backup tại: {backup_path}")
            shutil.copy2(file_path, backup_path)
            logger.info(f"✓ Backup đã được tạo thành công")
        
        # Read CSV file
        logger.info(f"\nĐang đọc file CSV...")
        df = pd.read_csv(file_path, encoding='utf-8')
        
        initial_rows = len(df)
        initial_cols = len(df.columns)
        logger.info(f"Số dòng: {initial_rows:,}")
        logger.info(f"Số cột hiện tại: {initial_cols}")
        logger.info(f"Các cột hiện tại: {df.columns.tolist()}")
        
        # Check if 'Audio' column already exists
        if 'Audio' in df.columns:
            logger.warning(f"\n⚠ Cột 'Audio' đã tồn tại trong file!")
            user_input = input("Bạn có muốn ghi đè (overwrite) cột này? (y/n): ")
            if user_input.lower() != 'y':
                logger.info("Hủy thao tác.")
                return False
            logger.info("Ghi đè cột 'Audio' hiện có...")
        
        # Add 'Audio' column (empty/null values)
        logger.info(f"\nĐang thêm cột 'Audio'...")
        df['Audio'] = None  # or you can use: df['Audio'] = ''
        
        # Reorder columns to place 'Audio' between 'Price' and 'Warranty'
        logger.info(f"Đang sắp xếp lại thứ tự các cột...")
        
        # Get the desired column order
        # Audio should be between Price and Warranty
        desired_order = []
        for col in df.columns:
            if col != 'Audio':  # Skip Audio for now
                desired_order.append(col)
                if col == 'Price':  # Insert Audio after Price
                    desired_order.append('Audio')
        
        # If Audio column exists but Price doesn't, just append at the end
        if 'Audio' not in desired_order:
            desired_order.append('Audio')
        
        # Reorder the DataFrame
        df = df[desired_order]
        
        logger.info(f"Thứ tự cột mới: {df.columns.tolist()}")
        
        # Verify the column was added and positioned correctly
        if 'Audio' in df.columns:
            audio_index = df.columns.tolist().index('Audio')
            logger.info(f"✓ Cột 'Audio' đã được thêm thành công ở vị trí {audio_index + 1}")
        else:
            logger.error(f"✗ Lỗi: Không thể thêm cột 'Audio'")
            return False
        
        # Save the modified DataFrame back to CSV
        logger.info(f"\nĐang lưu file CSV đã cập nhật...")
        df.to_csv(file_path, index=False, encoding='utf-8')
        
        # Verify the file was saved correctly
        logger.info(f"Đang kiểm tra file đã lưu...")
        df_verify = pd.read_csv(file_path, encoding='utf-8')
        
        final_rows = len(df_verify)
        final_cols = len(df_verify.columns)
        
        logger.info(f"\n" + "=" * 80)
        logger.info("KẾT QUẢ")
        logger.info("=" * 80)
        logger.info(f"Số dòng: {initial_rows:,} → {final_rows:,}")
        logger.info(f"Số cột: {initial_cols} → {final_cols}")
        logger.info(f"Các cột sau khi cập nhật: {df_verify.columns.tolist()}")
        
        if 'Audio' in df_verify.columns:
            logger.info(f"\n✓ HOÀN THÀNH THÀNH CÔNG!")
            logger.info(f"✓ Cột 'Audio' đã được thêm vào file: {file_path}")
            if backup:
                logger.info(f"✓ File backup: {backup_path}")
            return True
        else:
            logger.error(f"\n✗ Lỗi: Cột 'Audio' không xuất hiện trong file sau khi lưu")
            return False
        
    except pd.errors.EmptyDataError:
        logger.error(f"File rỗng hoặc không có dữ liệu: {file_path}")
        return False
    except pd.errors.ParserError as e:
        logger.error(f"Lỗi phân tích CSV: {str(e)}")
        return False
    except PermissionError:
        logger.error(f"Lỗi: Không có quyền ghi vào file {file_path}")
        logger.error(f"Vui lòng đóng file nếu đang mở trong Excel hoặc ứng dụng khác")
        return False
    except Exception as e:
        logger.error(f"Lỗi không xác định: {str(e)}")
        return False


def main():
    """Main function."""
    
    # File path
    file_path = "D:/AI_Tranning/trainning_data_split/Dataset.csv"
    
    # Add Audio column
    success = add_audio_column(file_path, backup=True)
    
    if success:
        logger.info("\n" + "=" * 80)
        logger.info("Thao tác hoàn tất!")
        logger.info("=" * 80)
    else:
        logger.error("\n" + "=" * 80)
        logger.error("Thao tác thất bại!")
        logger.error("=" * 80)
    
    logger.info(f"\nKiểm tra file log để biết chi tiết: add_audio_column.log")


if __name__ == "__main__":
    main()
