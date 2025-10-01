import pandas as pd
import numpy as np
from collections import Counter
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import List, Dict

def clean_text(text):
    # Clean text for comparison
    if pd.isna(text):
        return ""
    
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def check_duplicates(csv_file):
    print("🔍 Đang đọc file CSV...")
    
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        print(f"✅ Đọc thành công file CSV")
        print(f"📊 Tổng số dòng: {len(df)}")
        print(f"📊 Tổng số cột: {len(df.columns)}")
        print(f"📊 Tên các cột: {list(df.columns)}")
        
        if 'data' not in df.columns:
            print("❌ Không tìm thấy cột 'data' trong file CSV")
            return
        
        print(f"\n🔍 Phân tích dữ liệu trùng lặp...")
        
        # Check exact duplicates
        print("\n1️⃣ KIỂM TRA TRÙNG LẶP HOÀN TOÀN:")
        exact_duplicates = df.duplicated(subset=['data'], keep=False)
        exact_duplicate_count = exact_duplicates.sum()
        
        if exact_duplicate_count > 0:
            print(f"⚠️  Tìm thấy {exact_duplicate_count} dòng bị trùng lặp hoàn toàn")
            
            duplicate_rows = df[exact_duplicates]
            duplicate_groups = duplicate_rows.groupby('data').size().sort_values(ascending=False)
            
            print(f"📋 Chi tiết các nhóm trùng lặp:")
            for i, (content, count) in enumerate(duplicate_groups.head(10).items(), 1):
                print(f"   {i}. Xuất hiện {count} lần:")
                print(f"      \"{content[:100]}{'...' if len(str(content)) > 100 else ''}\"")
                print()
        else:
            print("✅ Không có dữ liệu trùng lặp hoàn toàn")
        
        # Create clean data
        print("\n2️⃣ TẠO DỮ LIỆU SẠCH (LOẠI BỎ DUMP):")
        
        clean_df = df[~df.duplicated(subset=['data'], keep='first')].copy()
        clean_count = len(clean_df)
        removed_count = len(df) - clean_count
        
        print(f"📊 Số dòng sau khi loại bỏ dump: {clean_count}")
        print(f"📊 Số dòng đã loại bỏ: {removed_count}")
        print(f"📊 Tỷ lệ dữ liệu sạch: {(clean_count / len(df)) * 100:.2f}%")
        
        # Statistics
        print("\n3️⃣ THỐNG KÊ TỔNG QUAN:")
        print(f"📊 Tổng số dòng gốc: {len(df)}")
        print(f"📊 Số dòng trùng lặp (dump): {exact_duplicate_count}")
        print(f"📊 Số dòng duy nhất (sạch): {clean_count}")
        print(f"📊 Tỷ lệ dump: {(exact_duplicate_count / len(df)) * 100:.2f}%")
        print(f"📊 Tỷ lệ dữ liệu sạch: {(clean_count / len(df)) * 100:.2f}%")
        
        # Check empty data
        print("\n4️⃣ KIỂM TRA DỮ LIỆU TRỐNG:")
        empty_count = df['data'].isna().sum()
        empty_string_count = (df['data'] == '').sum()
        print(f"📊 Số dòng có giá trị null: {empty_count}")
        print(f"📊 Số dòng có chuỗi rỗng: {empty_string_count}")
        
        # Save results
        print("\n5️⃣ LƯU KẾT QUẢ:")
        
        if exact_duplicate_count > 0:
            frequency_count = df['data'].value_counts()
            frequency_df = pd.DataFrame({
                'content': frequency_count.index,
                'frequency': frequency_count.values
            })
            
            duplicates_only = frequency_df[frequency_df['frequency'] > 1].copy()
            duplicates_only = duplicates_only.sort_values('frequency', ascending=False)
            
            duplicates_only.to_csv('duplicates_exact.csv', index=False, encoding='utf-8')
            print("✅ Đã lưu file 'duplicates_exact.csv' chứa dữ liệu dump (đã sắp xếp theo tần suất)")
            
            print(f"\n🏆 TOP 10 DỮ LIỆU DUMP NHIỀU NHẤT:")
            for i, row in duplicates_only.head(10).iterrows():
                content = str(row['content'])
                if len(content) > 80:
                    content = content[:80] + "..."
                print(f"   {i+1:2d}. Xuất hiện {row['frequency']:3d} lần: \"{content}\"")
        
        clean_df.to_csv('clean_data.csv', index=False, encoding='utf-8')
        print(f"✅ Đã lưu file 'clean_data.csv' chứa {len(clean_df)} dòng dữ liệu sạch (đã loại bỏ dump)")
        
    except Exception as e:
        print(f"❌ Lỗi khi đọc file: {str(e)}")

def main():
    DATA_FILE = Path("data") / "Dataset Text Normalization 14k.csv"
    if not DATA_FILE.exists():
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
        print(f"Không tìm thấy file: {DATA_FILE}")
        return

    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 60)
    print("🔍 KIỂM TRA DỮ LIỆU TRÙNG LẶP TRONG FILE CSV")
    print("=" * 60)
    
    check_duplicates(DATA_FILE)
    
    print("\n" + "=" * 60)
    print("✅ HOÀN THÀNH KIỂM TRA")
    print("=" * 60)

if __name__ == "__main__":
    main()
