"""
Script để chuẩn hóa format CSV - đảm bảo tất cả các trường đều có dấu ngoặc kép
"""
import csv
import sys
import io
from pathlib import Path

# Fix console encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def normalize_csv(input_file, output_file):
    """
    Chuẩn hóa file CSV - sửa các hàng thiếu dấu ngoặc kép hoặc bị ngắt dòng
    
    Args:
        input_file: Đường dẫn file CSV đầu vào
        output_file: Đường dẫn file CSV đầu ra
    """
    print(f"Đang đọc file: {input_file}")
    
    # Đọc file gốc và sửa các hàng bị lỗi
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    total_lines = len(lines)
    fixed_count = 0
    
    while i < total_lines:
        line = lines[i]
        
        # Bỏ qua dòng trống
        if not line.strip():
            i += 1
            continue
        
        # Kiểm tra nếu dòng không bắt đầu bằng dấu ngoặc kép
        if not line.startswith('"'):
            # Trường hợp 1: Thiếu dấu ngoặc kép ở đầu nhưng có ở cuối
            if '","' in line or line.endswith('"'):
                # Thêm dấu ngoặc kép vào đầu
                line = '"' + line
                fixed_count += 1
                print(f"Đã sửa hàng {i+1}: Thêm dấu ngoặc kép ở đầu")
            # Trường hợp 2: Dòng này là phần tiếp theo của dòng trước (bị ngắt dòng)
            elif i > 0 and fixed_lines:
                # Gộp với dòng trước đó
                fixed_lines[-1] = fixed_lines[-1].rstrip() + ' ' + line
                fixed_count += 1
                print(f"Đã sửa hàng {i+1}: Gộp với hàng trước")
                i += 1
                continue
        
        fixed_lines.append(line)
        i += 1
    
    # Ghi lại file với encoding UTF-8 có BOM để Excel đọc được
    print(f"\nĐang ghi file mới: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        for line in fixed_lines:
            f.write(line + '\n')
    
    print(f"\nHoàn thành!")
    print(f"- Tổng số dòng gốc: {total_lines}")
    print(f"- Số dòng đã sửa: {fixed_count}")
    print(f"- Tổng số dòng trong file mới: {len(fixed_lines)}")
    
    # Kiểm tra và đọc lại file để xác nhận
    print(f"\nĐang kiểm tra file đã chuẩn hóa...")
    error_count = 0
    with open(output_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        row_count = 0
        for idx, row in enumerate(reader, 1):
            row_count += 1
            # Kiểm tra số cột (nên có 10 cột)
            if len(row) != 10:
                print(f"⚠ Cảnh báo: Hàng {idx} có {len(row)} cột (nên có 10 cột)")
                error_count += 1
    
    print(f"- Số hàng trong file mới: {row_count}")
    if error_count == 0:
        print("✓ File CSV đã được chuẩn hóa thành công!")
    else:
        print(f"⚠ Có {error_count} hàng cần kiểm tra thêm")

def main():
    # Xác định đường dẫn
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    input_file = project_root / "data" / "Dataset Text Normalization 14k.csv"
    output_file = project_root / "data" / "Dataset Text Normalization 14k_normalized.csv"
    
    # Kiểm tra file đầu vào có tồn tại không
    if not input_file.exists():
        print(f"❌ Lỗi: Không tìm thấy file {input_file}")
        sys.exit(1)
    
    # Chạy chuẩn hóa
    normalize_csv(input_file, output_file)
    
    print(f"\n📁 File đã lưu tại: {output_file}")

if __name__ == "__main__":
    main()

