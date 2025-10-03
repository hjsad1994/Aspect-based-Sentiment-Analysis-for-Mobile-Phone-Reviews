"""
Script nâng cao để tính độ đồng thuận Fleiss' Kappa cho dữ liệu annotation
Phiên bản này có:
- Thống kê chi tiết cho từng cột
- Phân tích items có agreement thấp
- Xử lý dữ liệu thiếu
- Xuất báo cáo ra file
"""
import csv
import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from datetime import datetime

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
        tuple: (kappa_value, P_bar, P_e) - Kappa, observed agreement, expected agreement
    """
    n, k = ratings_matrix.shape  # n = số items, k = số categories
    N = ratings_matrix.sum(axis=1)[0]  # Tổng số raters (giả định giống nhau cho tất cả items)
    
    # Tính p_j (proportion of all assignments which were to the j-th category)
    p_j = ratings_matrix.sum(axis=0) / (n * N)
    
    # Tính P_e (expected agreement by chance)
    P_e = (p_j ** 2).sum()
    
    # Tính P_bar (observed agreement)
    P_i = (ratings_matrix ** 2).sum(axis=1) - N
    P_i = P_i / (N * (N - 1))
    P_bar = P_i.mean()
    
    # Tính Fleiss' Kappa
    if P_e == 1:
        kappa = 1.0 if P_bar == 1.0 else 0.0
    else:
        kappa = (P_bar - P_e) / (1 - P_e)
    
    return kappa, P_bar, P_e

def calculate_item_agreement(counts):
    """
    Tính độ agreement cho một item cụ thể
    
    Args:
        counts: List số lượng votes cho mỗi category
    
    Returns:
        float: Tỷ lệ agreement (0-1)
    """
    N = sum(counts)
    if N <= 1:
        return 1.0
    
    # Tính P_i cho item này
    P_i = (sum(c**2 for c in counts) - N) / (N * (N - 1))
    return P_i

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

def calculate_agreement_advanced(csv_file, output_report=None):
    """
    Tính Fleiss' Kappa cho tất cả label columns với thống kê chi tiết
    
    Args:
        csv_file: Đường dẫn file CSV
        output_report: Đường dẫn file báo cáo (optional)
    """
    print(f"{'='*80}")
    print(f"FLEISS' KAPPA AGREEMENT ANALYSIS")
    print(f"{'='*80}")
    print(f"File: {csv_file}\n")
    
    # Đọc dữ liệu
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Các cột label cần tính
    label_columns = [
        'Battery', 'Camera', 'Performance', 'Display', 'Design', 
        'Software', 'Packaging', 'Price', 'Warranty', 'Shop_Service', 
        'Shipping', 'General', 'Others'
    ]
    
    # Nhóm annotations theo ID
    annotations_by_id = defaultdict(list)
    for row in rows:
        item_id = row['id']
        annotations_by_id[item_id].append(row)
    
    print(f"Tổng số items (texts) được đánh giá: {len(annotations_by_id)}")
    print(f"Tổng số annotations: {len(rows)}")
    
    # Thống kê số annotators
    annotators = set(row.get('annotator', 'unknown') for row in rows)
    print(f"Số annotators: {len(annotators)}")
    
    # Phân bố số raters per item
    raters_per_item = [len(anns) for anns in annotations_by_id.values()]
    print(f"Số raters mỗi item: min={min(raters_per_item)}, max={max(raters_per_item)}, trung bình={np.mean(raters_per_item):.1f}")
    
    # Tính Fleiss' Kappa cho từng label
    results = {}
    detailed_stats = {}
    low_agreement_items = {}  # Items có agreement thấp
    
    categories = ['Negative', 'Neutral', 'Positive', '']
    category_to_idx = {cat: idx for idx, cat in enumerate(categories)}
    
    for label in label_columns:
        print(f"\n{'='*80}")
        print(f"LABEL: {label}")
        print(f"{'='*80}")
        
        # Tạo ma trận ratings
        ratings_matrix = []
        valid_items = 0
        items_with_data = 0
        item_agreements = []
        item_details = []
        
        for item_id, annotations in sorted(annotations_by_id.items()):
            # Đếm số lượng mỗi category
            counts = [0] * len(categories)
            has_annotation = False
            
            for ann in annotations:
                value = ann[label].strip()
                if value in category_to_idx:
                    counts[category_to_idx[value]] += 1
                    if value != '':
                        has_annotation = True
            
            total_raters = sum(counts)
            
            # Đếm items có ít nhất 1 annotation không rỗng
            if has_annotation:
                items_with_data += 1
            
            # Chỉ tính những items có ít nhất 2 raters
            if total_raters >= 2:
                ratings_matrix.append(counts)
                valid_items += 1
                
                # Tính agreement cho item này
                item_agreement = calculate_item_agreement(counts)
                item_agreements.append(item_agreement)
                
                # Lưu chi tiết
                item_details.append({
                    'id': item_id,
                    'text': annotations[0]['data'][:80] + '...' if len(annotations[0]['data']) > 80 else annotations[0]['data'],
                    'counts': counts,
                    'agreement': item_agreement,
                    'annotations': [ann[label].strip() for ann in annotations]
                })
        
        if len(ratings_matrix) == 0:
            print(f"⚠️  Không có đủ dữ liệu để tính Fleiss' Kappa")
            print(f"   Items có annotation: {items_with_data}")
            results[label] = None
            continue
        
        ratings_matrix = np.array(ratings_matrix)
        
        # Tính Fleiss' Kappa
        kappa, P_bar, P_e = fleiss_kappa(ratings_matrix)
        results[label] = kappa
        
        # Thống kê
        total_annotations = ratings_matrix.sum()
        category_counts = ratings_matrix.sum(axis=0)
        
        print(f"\n📊 Thống kê:")
        print(f"  Items có annotation không rỗng:  {items_with_data}/{len(annotations_by_id)} ({items_with_data/len(annotations_by_id)*100:.1f}%)")
        print(f"  Items có ≥2 raters:               {valid_items}")
        print(f"  Tổng số annotations:              {int(total_annotations)}")
        
        print(f"\n📈 Phân bố categories:")
        for cat, count in zip(categories, category_counts):
            cat_name = cat if cat else "(Rỗng)"
            percentage = (count / total_annotations * 100) if total_annotations > 0 else 0
            bar_length = int(percentage / 2)
            bar = '█' * bar_length
            print(f"  {cat_name:12} : {int(count):4} ({percentage:5.1f}%) {bar}")
        
        print(f"\n🎯 Fleiss' Kappa: {kappa:.4f}")
        print(f"   Observed agreement (P̄):  {P_bar:.4f}")
        print(f"   Expected agreement (Pₑ): {P_e:.4f}")
        print(f"   Đánh giá: {interpret_kappa(kappa)}")
        
        # Phân tích agreement distribution
        if item_agreements:
            print(f"\n📉 Phân bố agreement cho từng item:")
            print(f"   Min:  {min(item_agreements):.4f}")
            print(f"   Max:  {max(item_agreements):.4f}")
            print(f"   Mean: {np.mean(item_agreements):.4f}")
            print(f"   Std:  {np.std(item_agreements):.4f}")
            
            # Tìm items có agreement thấp (dưới 0.5)
            low_agreement = [item for item in item_details if item['agreement'] < 0.5]
            if low_agreement:
                print(f"\n⚠️  Items có agreement thấp (<0.5): {len(low_agreement)}")
                low_agreement_items[label] = sorted(low_agreement, key=lambda x: x['agreement'])[:5]
        
        # Lưu thống kê chi tiết
        detailed_stats[label] = {
            'kappa': kappa,
            'P_bar': P_bar,
            'P_e': P_e,
            'valid_items': valid_items,
            'items_with_data': items_with_data,
            'total_items': len(annotations_by_id),
            'category_counts': {cat: int(count) for cat, count in zip(categories, category_counts)},
            'item_agreements': item_agreements
        }
    
    # Tổng kết
    print(f"\n\n{'='*80}")
    print(f"TỔNG KẾT FLEISS' KAPPA")
    print(f"{'='*80}")
    print(f"{'Label':15} {'Kappa':>8} {'P̄':>8} {'Pₑ':>8} {'Items':>7} {'Đánh giá'}")
    print(f"{'-'*80}")
    
    valid_kappas = []
    for label in label_columns:
        if results.get(label) is not None:
            kappa = results[label]
            stats = detailed_stats[label]
            valid_kappas.append(kappa)
            print(f"{label:15} {kappa:8.4f} {stats['P_bar']:8.4f} {stats['P_e']:8.4f} {stats['valid_items']:7} {interpret_kappa(kappa)}")
        else:
            print(f"{label:15} {'N/A':>8} {'N/A':>8} {'N/A':>8} {'N/A':>7} Không đủ dữ liệu")
    
    # Tính trung bình
    if valid_kappas:
        print(f"{'-'*80}")
        avg_kappa = np.mean(valid_kappas)
        median_kappa = np.median(valid_kappas)
        print(f"{'Trung bình':15} {avg_kappa:8.4f} {' '*17} {len(valid_kappas):7} {interpret_kappa(avg_kappa)}")
        print(f"{'Trung vị':15} {median_kappa:8.4f}")
        print(f"{'Độ lệch chuẩn':15} {np.std(valid_kappas):8.4f}")
    
    # Hiển thị items có agreement thấp
    if low_agreement_items:
        print(f"\n\n{'='*80}")
        print(f"ITEMS CÓ AGREEMENT THẤP (Top 5 mỗi label)")
        print(f"{'='*80}")
        
        for label, items in low_agreement_items.items():
            if items:
                print(f"\n📋 {label}:")
                for item in items[:5]:
                    print(f"\n  ID: {item['id']} (Agreement: {item['agreement']:.3f})")
                    print(f"  Text: {item['text']}")
                    print(f"  Votes: {', '.join(item['annotations'])}")
                    print(f"  Distribution: Neg={item['counts'][0]}, Neu={item['counts'][1]}, Pos={item['counts'][2]}, Empty={item['counts'][3]}")
    
    # Ghi báo cáo ra file
    if output_report:
        write_report(output_report, results, detailed_stats, low_agreement_items, 
                    len(annotations_by_id), len(rows), len(annotators))
        print(f"\n📄 Báo cáo chi tiết đã được lưu: {output_report}")
    
    return results, detailed_stats

def write_report(output_file, results, detailed_stats, low_agreement_items, 
                total_items, total_annotations, num_annotators):
    """Ghi báo cáo chi tiết ra file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("FLEISS' KAPPA AGREEMENT ANALYSIS - DETAILED REPORT\n")
        f.write("="*80 + "\n")
        f.write(f"Ngày tạo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"\nTổng số items: {total_items}\n")
        f.write(f"Tổng số annotations: {total_annotations}\n")
        f.write(f"Số annotators: {num_annotators}\n")
        
        f.write(f"\n{'='*80}\n")
        f.write("KẾT QUẢ FLEISS' KAPPA\n")
        f.write(f"{'='*80}\n")
        f.write(f"{'Label':15} {'Kappa':>8} {'P_bar':>8} {'P_e':>8} {'Valid Items':>12} {'Items w/ Data':>15} {'Coverage':>10}\n")
        f.write(f"{'-'*80}\n")
        
        valid_kappas = []
        for label, kappa in results.items():
            if kappa is not None:
                stats = detailed_stats[label]
                valid_kappas.append(kappa)
                coverage = stats['items_with_data'] / stats['total_items'] * 100
                f.write(f"{label:15} {kappa:8.4f} {stats['P_bar']:8.4f} {stats['P_e']:8.4f} "
                       f"{stats['valid_items']:12} {stats['items_with_data']:15} {coverage:9.1f}%\n")
        
        if valid_kappas:
            f.write(f"{'-'*80}\n")
            f.write(f"{'Trung bình':15} {np.mean(valid_kappas):8.4f}\n")
            f.write(f"{'Trung vị':15} {np.median(valid_kappas):8.4f}\n")
            f.write(f"{'Độ lệch chuẩn':15} {np.std(valid_kappas):8.4f}\n")
        
        # Category distribution
        f.write(f"\n{'='*80}\n")
        f.write("PHÂN BỐ CATEGORIES\n")
        f.write(f"{'='*80}\n")
        
        for label, stats in detailed_stats.items():
            if results[label] is not None:
                f.write(f"\n{label}:\n")
                total = sum(stats['category_counts'].values())
                for cat, count in stats['category_counts'].items():
                    cat_name = cat if cat else "(Rỗng)"
                    pct = count / total * 100 if total > 0 else 0
                    f.write(f"  {cat_name:12} : {count:4} ({pct:5.1f}%)\n")
        
        # Low agreement items
        if low_agreement_items:
            f.write(f"\n{'='*80}\n")
            f.write("ITEMS CÓ AGREEMENT THẤP\n")
            f.write(f"{'='*80}\n")
            
            for label, items in low_agreement_items.items():
                if items:
                    f.write(f"\n{label}:\n")
                    for item in items:
                        f.write(f"\n  ID: {item['id']} (Agreement: {item['agreement']:.3f})\n")
                        f.write(f"  Text: {item['text']}\n")
                        f.write(f"  Votes: {', '.join(item['annotations'])}\n")
                        f.write(f"  Distribution: Neg={item['counts'][0]}, Neu={item['counts'][1]}, "
                               f"Pos={item['counts'][2]}, Empty={item['counts'][3]}\n")

def main():
    """Hàm chính"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # Đường dẫn mặc định
    default_csv = project_root / "data_label" / "2.csv"
    
    # Cho phép truyền tham số từ command line
    if len(sys.argv) >= 2:
        csv_file = Path(sys.argv[1])
    else:
        csv_file = default_csv
    
    # Output report
    if len(sys.argv) >= 3:
        output_report = Path(sys.argv[2])
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_report = csv_file.parent / f"fleiss_kappa_report_{timestamp}.txt"
    
    # Kiểm tra file
    if not csv_file.exists():
        print(f"❌ Lỗi: Không tìm thấy file {csv_file}")
        print(f"\nCách sử dụng:")
        print(f"  python {Path(__file__).name} [đường_dẫn_csv] [output_report]")
        print(f"\nVí dụ:")
        print(f"  python {Path(__file__).name}")
        print(f"  python {Path(__file__).name} data_label/2.csv")
        print(f"  python {Path(__file__).name} data_label/2.csv report.txt")
        sys.exit(1)
    
    # Tính Fleiss' Kappa
    try:
        calculate_agreement_advanced(csv_file, output_report)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
