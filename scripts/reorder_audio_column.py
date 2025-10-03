#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to reorder columns in Dataset.csv to place 'Audio' between 'Price' and 'Warranty'.
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
        logging.FileHandler('reorder_audio_column.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def reorder_audio_column(file_path: str, backup: bool = True) -> bool:
    """
    Reorder columns to place 'Audio' between 'Price' and 'Warranty'.
    
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
        logger.info("BẮT ĐẦU SẮP XẾP LẠI CỘT 'AUDIO'")
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
        
        # Check if 'Audio' column exists
        if 'Audio' not in df.columns:
            logger.warning(f"\n⚠ Cột 'Audio' không tồn tại. Đang thêm cột...")
            df['Audio'] = None
        
        # Reorder columns to place 'Audio' between 'Price' and 'Warranty'
        logger.info(f"\nĐang sắp xếp lại thứ tự các cột...")
        logger.info(f"Mục tiêu: Audio nằm giữa 'Price' và 'Warranty'")
        
        # Define the desired column order
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
        
        logger.info(f"\nThứ tự cột mới:")
        for i, col in enumerate(df.columns.tolist(), 1):
            marker = " ← Audio" if col == 'Audio' else ""
            logger.info(f"  {i}. {col}{marker}")
        
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
        
        # Find position of Audio column
        if 'Audio' in df_verify.columns:
            audio_index = df_verify.columns.tolist().index('Audio')
            cols_list = df_verify.columns.tolist()
            
            logger.info(f"\n✓ Vị trí cột 'Audio': {audio_index + 1}/{final_cols}")
            
            # Show surrounding columns
            if audio_index > 0:
                logger.info(f"  Trước: {cols_list[audio_index - 1]}")
            logger.info(f"  → Audio")
            if audio_index < len(cols_list) - 1:
                logger.info(f"  Sau: {cols_list[audio_index + 1]}")
            
            # Verify correct position (between Price and Warranty)
            if audio_index > 0 and cols_list[audio_index - 1] == 'Price':
                if audio_index < len(cols_list) - 1 and cols_list[audio_index + 1] == 'Warranty':
                    logger.info(f"\n✓ HOÀN THÀNH THÀNH CÔNG!")
                    logger.info(f"✓ Cột 'Audio' đã được đặt đúng vị trí giữa 'Price' và 'Warranty'")
                    if backup:
                        logger.info(f"✓ File backup: {backup_path}")
                    return True
                else:
                    logger.warning(f"⚠ Cột 'Audio' không nằm trước 'Warranty'")
            else:
                logger.warning(f"⚠ Cột 'Audio' không nằm sau 'Price'")
                logger.warning(f"Vị trí hiện tại có thể không phải mong muốn")
            
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
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    """Main function."""
    
    # File path
    file_path = "D:/AI_Tranning/trainning_data_split/Dataset.csv"
    
    # Reorder Audio column
    success = reorder_audio_column(file_path, backup=True)
    
    if success:
        logger.info("\n" + "=" * 80)
        logger.info("Thao tác hoàn tất!")
        logger.info("=" * 80)
    else:
        logger.error("\n" + "=" * 80)
        logger.error("Thao tác thất bại!")
        logger.error("=" * 80)
    
    logger.info(f"\nKiểm tra file log để biết chi tiết: reorder_audio_column.log")


if __name__ == "__main__":
    main()
