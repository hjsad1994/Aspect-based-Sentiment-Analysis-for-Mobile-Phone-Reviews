"""
Script để xóa dấu ngoặc kép ở các trường rỗng trong CSV
Chuyển từ: "","",""  sang: ,,,
"""
import csv
import sys
import io
from pathlib import Path

# Fix console encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def remove_empty_quotes(input_file, output_file=None):
    """
    Xóa dấu ngoặc kép ở các trường rỗng
    
    Args:
        input_file: Đường dẫn file CSV đầu vào
        output_file: Đường dẫn file CSV đầu ra (nếu None, sẽ ghi đè file gốc)
    """
    print(f"Đang đọc file: {input_file}")
    
    # Đọc file CSV
    with open(input_file, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    total_rows = len(rows)
    print(f"Tổng số rows: {total_rows}")
    
    # Xác định file đầu ra
    if output_file is None:
        output_file = input_file
        print(f"⚠ Sẽ ghi đè file gốc")
    else:
        print(f"File đầu ra: {output_file}")
    
    # Ghi lại file với QUOTE_MINIMAL (chỉ quote khi cần thiết)
    print(f"\nĐang xử lý và ghi file...")
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        for row in rows:
            # Thay thế empty strings để không bị quote
            processed_row = [cell if cell else '' for cell in row]
            writer.writerow(processed_row)
    
    print(f"\n✓ Hoàn thành!")
    print(f"File đầu ra: {output_file}")

def main():
    """Hàm chính"""
    # Parse arguments
    if len(sys.argv) < 2:
        print("❌ Lỗi: Cần chỉ định file đầu vào")
        print(f"\nCách sử dụng:")
        print(f"  python {Path(__file__).name} <file_input> [file_output]")
        print(f"\nVí dụ:")
        print(f"  # Ghi đè file gốc")
        print(f"  python {Path(__file__).name} data/test.csv")
        print(f"\n  # Tạo file mới")
        print(f"  python {Path(__file__).name} data/test.csv data/test_clean.csv")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) >= 3 else None
    
    # Kiểm tra file
    if not input_file.exists():
        print(f"❌ Lỗi: Không tìm thấy file {input_file}")
        sys.exit(1)
    
    # Xử lý
    try:
        remove_empty_quotes(input_file, output_file)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()


