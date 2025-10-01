"""
Script để chuyển đổi file JSON sang CSV
"""
import json
import csv
import sys
import io
from pathlib import Path

# Fix console encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def json_to_csv(json_file, csv_file):
    """
    Chuyển đổi file JSON sang CSV
    
    Args:
        json_file: Đường dẫn file JSON đầu vào
        csv_file: Đường dẫn file CSV đầu ra
    """
    print(f"Đang đọc file JSON: {json_file}")
    
    # Đọc file JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Đã đọc {len(data)} bản ghi")
    
    if not data:
        print("⚠ File JSON trống!")
        return
    
    # Lấy tất cả các key từ bản ghi đầu tiên làm header
    headers = list(data[0].keys())
    print(f"Các cột: {', '.join(headers)}")
    
    # Ghi ra file CSV
    print(f"\nĐang ghi file CSV: {csv_file}")
    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers, quoting=csv.QUOTE_ALL)
        
        # Ghi header
        writer.writeheader()
        
        # Ghi các hàng dữ liệu
        for row in data:
            writer.writerow(row)
    
    print(f"\n✓ Đã chuyển đổi thành công!")
    print(f"- Số bản ghi: {len(data)}")
    print(f"- Số cột: {len(headers)}")
    print(f"- File đầu ra: {csv_file}")

def main():
    """Hàm chính"""
    # Xác định đường dẫn
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # Đường dẫn mặc định
    default_json = project_root / "data_label" / "1.json"
    default_csv = project_root / "data_label" / "1.csv"
    
    # Cho phép truyền tham số từ command line
    if len(sys.argv) >= 2:
        json_file = Path(sys.argv[1])
    else:
        json_file = default_json
    
    if len(sys.argv) >= 3:
        csv_file = Path(sys.argv[2])
    else:
        # Tự động tạo tên file CSV dựa trên tên file JSON
        csv_file = json_file.with_suffix('.csv')
    
    # Kiểm tra file đầu vào
    if not json_file.exists():
        print(f"❌ Lỗi: Không tìm thấy file {json_file}")
        print(f"\nCách sử dụng:")
        print(f"  python {Path(__file__).name} [đường_dẫn_json] [đường_dẫn_csv]")
        print(f"\nVí dụ:")
        print(f"  python {Path(__file__).name}")
        print(f"  python {Path(__file__).name} data_label/1.json")
        print(f"  python {Path(__file__).name} data_label/1.json output/result.csv")
        sys.exit(1)
    
    # Chuyển đổi
    try:
        json_to_csv(json_file, csv_file)
    except json.JSONDecodeError as e:
        print(f"❌ Lỗi: File JSON không hợp lệ - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

