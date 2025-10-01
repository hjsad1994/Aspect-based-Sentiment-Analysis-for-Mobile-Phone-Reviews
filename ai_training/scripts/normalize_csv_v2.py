"""
Script để chuẩn hóa format CSV - đảm bảo tất cả các trường đều có dấu ngoặc kép
Phiên bản 2: Sử dụng csv module để xử lý đúng cách
"""
import csv
import sys
import io
from pathlib import Path

# Fix console encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def normalize_csv_v2(input_file, output_file):
    """
    Chuẩn hóa file CSV - đảm bảo tất cả các trường đều được quoted
    
    Args:
        input_file: Đường dẫn file CSV đầu vào
        output_file: Đường dẫn file CSV đầu ra
    """
    print(f"Đang đọc file: {input_file}")
    
    rows_read = 0
    rows_written = 0
    error_rows = []
    
    # Đọc file CSV với csv.reader
    with open(input_file, 'r', encoding='utf-8', newline='') as infile:
        # Sử dụng csv.reader để parse đúng cách
        reader = csv.reader(infile)
        
        # Ghi ra file mới với tất cả các trường được quoted
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as outfile:
            writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)
            
            for row_num, row in enumerate(reader, 1):
                rows_read += 1
                
                # Kiểm tra số cột
                if len(row) != 10:
                    error_rows.append((row_num, len(row)))
                    if len(error_rows) <= 10:  # Chỉ in 10 hàng lỗi đầu tiên
                        print(f"⚠ Hàng {row_num} có {len(row)} cột: {row[0][:100] if row else '(trống)'}...")
                
                # Ghi hàng ra file mới (csv.writer sẽ tự động thêm dấu ngoặc kép)
                writer.writerow(row)
                rows_written += 1
                
                # In progress mỗi 1000 hàng
                if rows_read % 1000 == 0:
                    print(f"Đã xử lý {rows_read} hàng...", end='\r')
    
    print(f"\n\nHoàn thành!")
    print(f"- Số hàng đã đọc: {rows_read}")
    print(f"- Số hàng đã ghi: {rows_written}")
    print(f"- Số hàng có vấn đề: {len(error_rows)}")
    
    if error_rows:
        print(f"\n⚠ Có {len(error_rows)} hàng không có đúng 10 cột.")
        print("Các hàng này có thể cần xem xét thêm.")
    else:
        print("\n✓ Tất cả các hàng đều có đúng 10 cột!")
    
    return len(error_rows) == 0

def main():
    # Xác định đường dẫn
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    input_file = project_root / "data" / "Dataset Text Normalization 14k.csv"
    output_file = project_root / "data" / "Dataset_Text_Normalization_14k_normalized.csv"
    
    # Kiểm tra file đầu vào có tồn tại không
    if not input_file.exists():
        print(f"❌ Lỗi: Không tìm thấy file {input_file}")
        sys.exit(1)
    
    # Chạy chuẩn hóa
    success = normalize_csv_v2(input_file, output_file)
    
    print(f"\n📁 File đã lưu tại: {output_file}")
    
    if success:
        print("✓ File CSV đã được chuẩn hóa thành công!")
    else:
        print("⚠ File CSV đã được xuất nhưng có một số hàng cần kiểm tra.")

if __name__ == "__main__":
    main()

