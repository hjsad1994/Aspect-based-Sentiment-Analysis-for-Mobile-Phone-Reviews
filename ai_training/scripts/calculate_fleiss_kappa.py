"""
Script để tính độ đồng thuận Fleiss' Kappa cho dữ liệu annotation
"""
import csv
import sys
import io
from pathlib import Path
from collections import defaultdict
import numpy as np

# Fix console encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def fleiss_kappa(ratings_matrix):
    """
    Tính Fleiss' Kappa
    
    Args:
        ratings_matrix: Ma trận n x k, trong đó:
                       n = số items (texts được đánh giá)
                       k = số categories (Negative, Positive, Neutral, etc.)
                       Mỗi cell chứa số lượng raters chọn category đó cho item đó
    
    Returns:
        float: Giá trị Fleiss' Kappa (từ -1 đến 1)
    """
    n, k = ratings_matrix.shape  # n = số items, k = số categories
    N = ratings_matrix.sum(axis=1)[0]  # Tổng số raters (giả định giống nhau cho tất cả items)
    
    # Tính P_i (proportion of all assignments which were to the j-th category)
    p_j = ratings_matrix.sum(axis=0) / (n * N)
    
    # Tính P_e (expected agreement by chance)
    P_e = (p_j ** 2).sum()
    
    # Tính P_bar (observed agreement)
    P_i = (ratings_matrix ** 2).sum(axis=1) - N
    P_i = P_i / (N * (N - 1))
    P_bar = P_i.mean()
    
    # Tính Fleiss' Kappa
    if P_e == 1:
        return 1.0 if P_bar == 1.0 else 0.0
    
    kappa = (P_bar - P_e) / (1 - P_e)
    return kappa

def calculate_agreement(csv_file):
    """
    Tính Fleiss' Kappa cho từng label column trong file CSV
    
    Args:
        csv_file: Đường dẫn file CSV
    """
    print(f"Đang đọc file: {csv_file}\n")
    
    # Đọc dữ liệu
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Các cột label cần tính
    label_columns = ['Camera', 'Design', 'Others', 'Battery', 'Pricing', 
                    'Shipping', 'Warranty', 'Packaging', 'Performance']
    
    # Nhóm annotations theo ID
    annotations_by_id = defaultdict(list)
    for row in rows:
        item_id = row['id']
        annotations_by_id[item_id].append(row)
    
    print(f"Tổng số items (texts) được đánh giá: {len(annotations_by_id)}")
    print(f"Tổng số annotations: {len(rows)}\n")
    
    # Tính Fleiss' Kappa cho từng label
    results = {}
    
    for label in label_columns:
        print(f"{'='*60}")
        print(f"Label: {label}")
        print(f"{'='*60}")
        
        # Tạo ma trận ratings
        # Categories: Negative, Neutral, Positive, Empty
        categories = ['Negative', 'Neutral', 'Positive', '']
        category_to_idx = {cat: idx for idx, cat in enumerate(categories)}
        
        # Ma trận n x k (n items, k categories)
        ratings_matrix = []
        valid_items = 0
        
        for item_id, annotations in sorted(annotations_by_id.items()):
            # Đếm số lượng mỗi category
            counts = [0] * len(categories)
            for ann in annotations:
                value = ann[label].strip()
                if value in category_to_idx:
                    counts[category_to_idx[value]] += 1
            
            # Chỉ tính những items có ít nhất 2 raters
            if sum(counts) >= 2:
                ratings_matrix.append(counts)
                valid_items += 1
        
        if len(ratings_matrix) == 0:
            print(f"⚠ Không có đủ dữ liệu để tính Fleiss' Kappa cho {label}\n")
            continue
        
        ratings_matrix = np.array(ratings_matrix)
        
        # Tính Fleiss' Kappa
        kappa = fleiss_kappa(ratings_matrix)
        results[label] = kappa
        
        # Thống kê
        total_annotations = ratings_matrix.sum()
        category_counts = ratings_matrix.sum(axis=0)
        
        print(f"Số items có ít nhất 2 raters: {valid_items}")
        print(f"Tổng số annotations: {int(total_annotations)}")
        print(f"\nPhân bố categories:")
        for cat, count in zip(categories, category_counts):
            cat_name = cat if cat else "(Rỗng)"
            percentage = (count / total_annotations * 100) if total_annotations > 0 else 0
            print(f"  {cat_name:12} : {int(count):4} ({percentage:5.1f}%)")
        
        print(f"\n✓ Fleiss' Kappa: {kappa:.4f}")
        print(f"  Đánh giá: {interpret_kappa(kappa)}\n")
    
    # Tổng kết
    print(f"\n{'='*60}")
    print(f"TỔNG KẾT")
    print(f"{'='*60}")
    for label, kappa in results.items():
        print(f"{label:12} : {kappa:7.4f}  ({interpret_kappa(kappa)})")
    
    # Tính trung bình
    if results:
        avg_kappa = np.mean(list(results.values()))
        print(f"\n{'Trung bình':12} : {avg_kappa:7.4f}  ({interpret_kappa(avg_kappa)})")

def interpret_kappa(kappa):
    """
    Diễn giải giá trị Fleiss' Kappa theo thang đo Landis & Koch (1977)
    """
    if kappa < 0:
        return "Poor (Kém)"
    elif kappa < 0.20:
        return "Slight (Nhẹ)"
    elif kappa < 0.40:
        return "Fair (Trung bình)"
    elif kappa < 0.60:
        return "Moderate (Khá)"
    elif kappa < 0.80:
        return "Substantial (Tốt)"
    else:
        return "Almost Perfect (Gần như hoàn hảo)"

def main():
    """Hàm chính"""
    # Xác định đường dẫn
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # Đường dẫn mặc định
    default_csv = project_root / "data_label" / "2.csv"
    
    # Cho phép truyền tham số từ command line
    if len(sys.argv) >= 2:
        csv_file = Path(sys.argv[1])
    else:
        csv_file = default_csv
    
    # Kiểm tra file
    if not csv_file.exists():
        print(f"❌ Lỗi: Không tìm thấy file {csv_file}")
        print(f"\nCách sử dụng:")
        print(f"  python {Path(__file__).name} [đường_dẫn_csv]")
        print(f"\nVí dụ:")
        print(f"  python {Path(__file__).name}")
        print(f"  python {Path(__file__).name} data_label/2.csv")
        sys.exit(1)
    
    # Tính Fleiss' Kappa
    try:
        calculate_agreement(csv_file)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

