"""
Script consensus voting với chế độ interactive cho người quản lý
"""
import csv
import sys
import io
from pathlib import Path
from collections import Counter, defaultdict

# Fix console encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# User weights for voting
USER_WEIGHTS = {
    'nhhoangthong': 1.5,
    'dangdoai3': 1.4,
    'ah3cu102': 1.3,
    'quangvinh02200': 1.2,
}

DEFAULT_WEIGHT = 1.0  # Default weight for users not in the list

# Mapping số -> label
NUMBER_TO_LABEL = {
    '0': 'Neutral',
    '1': 'Positive', 
    '2': 'Negative',
    '': ''  # Enter để skip/giữ nguyên
}

LABEL_TO_NUMBER = {v: k for k, v in NUMBER_TO_LABEL.items() if k != ''}

CANONICAL_LABELS = {
    'neutral': 'Neutral',
    'neu': 'Neutral',
    '0': 'Neutral',
    'positive': 'Positive',
    'pos': 'Positive',
    '1': 'Positive',
    'negative': 'Negative',
    'neg': 'Negative',
    '2': 'Negative',
    '': '',
}


def normalize_label_value(value):
    if value is None:
        return ''
    return CANONICAL_LABELS.get(value.strip().lower(), '')

def get_user_weight(annotator):
    """Get weight for an annotator, extract username from email format"""
    # Extract username from email format (e.g., 'nhhoangthong@example.com' -> 'nhhoangthong')
    username = annotator.split('@')[0].lower().strip()
    return USER_WEIGHTS.get(username, DEFAULT_WEIGHT)

def weighted_vote(values, annotations):
    """
    Calculate weighted voting result based on user scores
    
    Args:
        values: List of label values
        annotations: List of annotation dictionaries with 'annotator' field
    
    Returns:
        Tuple (winning_value, total_weight, weight_details)
    """
    if not values or not annotations:
        return "", 0.0, {}
    
    # Calculate weighted scores for each unique value
    weighted_scores = defaultdict(float)
    value_annotators = defaultdict(list)  # Track which annotators voted for each value
    
    for value, annotation in zip(values, annotations):
        weight = get_user_weight(annotation['annotator'])
        weighted_scores[value] += weight
        value_annotators[value].append({
            'annotator': annotation['annotator'].split('@')[0],
            'weight': weight
        })
    
    # Find the value with highest weighted score
    if not weighted_scores:
        return "", 0.0, {}
    
    winning_value = max(weighted_scores.items(), key=lambda x: x[1])[0]
    winning_weight = weighted_scores[winning_value]
    
    # Prepare detailed breakdown
    weight_details = {
        'scores': dict(weighted_scores),
        'annotators': dict(value_annotators),
        'total_weight': sum(weighted_scores.values())
    }
    
    return winning_value, winning_weight, weight_details

def get_highest_weighted_vote(values, annotations):
    """
    Get the vote from the annotator with highest weight
    
    Args:
        values: List of label values
        annotations: List of annotation dictionaries
    
    Returns:
        Value from the highest-weighted annotator
    """
    if not values or not annotations:
        return ""
    
    # Find annotator with highest weight
    max_weight = -1
    max_vote = ""
    
    for value, annotation in zip(values, annotations):
        weight = get_user_weight(annotation['annotator'])
        if weight > max_weight:
            max_weight = weight
            max_vote = value
    
    return max_vote





def get_user_weight(annotator):
    """Get weight for an annotator, extract username from email format"""
    # Extract username from email format (e.g., 'nhhoangthong@example.com' -> 'nhhoangthong')
    username = annotator.split('@')[0].lower().strip()
    return USER_WEIGHTS.get(username, DEFAULT_WEIGHT)

def weighted_vote(values, annotations):
    """
    Calculate weighted voting result based on user scores
    
    Args:
        values: List of label values
        annotations: List of annotation dictionaries with 'annotator' field
    
    Returns:
        Tuple (winning_value, total_weight, weight_details)
    """
    if not values or not annotations:
        return "", 0.0, {}
    
    # Calculate weighted scores for each unique value
    weighted_scores = defaultdict(float)
    value_annotators = defaultdict(list)  # Track which annotators voted for each value
    
    for value, annotation in zip(values, annotations):
        weight = get_user_weight(annotation['annotator'])
        weighted_scores[value] += weight
        value_annotators[value].append({
            'annotator': annotation['annotator'].split('@')[0],
            'weight': weight
        })
    
    # Find the value with highest weighted score
    if not weighted_scores:
        return "", 0.0, {}
    
    winning_value = max(weighted_scores.items(), key=lambda x: x[1])[0]
    winning_weight = weighted_scores[winning_value]
    
    # Prepare detailed breakdown
    weight_details = {
        'scores': dict(weighted_scores),
        'annotators': dict(value_annotators),
        'total_weight': sum(weighted_scores.values())
    }
    
    return winning_value, winning_weight, weight_details

def display_annotations(text, label, annotations, votes, weighted_result=None):
    """Hiển thị thông tin annotations cho người quản lý"""
    print(f"\n{'='*70}")
    print(f"📝 Text: {text[:100]}{'...' if len(text) > 100 else ''}")
    print(f"🏷️  Label: {label}")
    print(f"\n👥 Votes từ annotators:")
    
    for i, ann in enumerate(annotations, 1):
        annotator = ann['annotator'].split('@')[0]  # Lấy tên trước @
        value = normalize_label_value(ann[label])
        display_value = value if value else "(Rỗng)"
        weight = get_user_weight(ann['annotator'])
        print(f"   {i}. {annotator:20} → {display_value:15} (weight: {weight:.1f})")
    
    # Thống kê votes
    counter = Counter(votes)
    print(f"\n📊 Tổng kết (Simple count):")
    for value, count in counter.most_common():
        display_value = value if value else "(Rỗng)"
        percentage = count / len(votes) * 100
        print(f"   {display_value:15} : {count}/{len(votes)} ({percentage:.0f}%)")
    
    
    # Hiển thị weighted scores nếu có
    if weighted_result:
        winning_value, winning_weight, weight_details = weighted_result
        print(f"\n⚖️  Weighted Scores:")
        for value, score in sorted(weight_details['scores'].items(), key=lambda x: x[1], reverse=True):
            display_value = value if value else "(Rỗng)"
            percentage = score / weight_details['total_weight'] * 100
            print(f"   {display_value:15} : {score:.1f}/{weight_details['total_weight']:.1f} ({percentage:.0f}%)")
        print(f"\n🏆 Winner (Weighted): {winning_value if winning_value else '(Rỗng)'} (score: {winning_weight:.1f})")
    
    # Xác định agreement level
    max_votes = counter.most_common(1)[0][1]
    if max_votes == len(votes):
        agreement = "✅ PERFECT (All Agree)"
    elif max_votes >= len(votes) // 2 + 1:
        agreement = "⚠️  MAJORITY (2/3 Agree)"
    else:
        agreement = "❌ NO AGREEMENT (All Different)"
    
    print(f"\n🎯 Độ đồng thuận: {agreement}")

def get_manager_decision(current_value):
    """Lấy quyết định từ người quản lý"""
    print(f"\n{'─'*70}")
    print(f"👨‍💼 Quyết định của bạn:")
    print(f"   0 = Neutral")
    print(f"   1 = Positive")
    print(f"   2 = Negative")
    print(f"   r = (Rỗng)")
    print(f"   Enter = Giữ nguyên ({current_value if current_value else '(Rỗng)'})")
    print(f"   s = Skip (bỏ qua, xử lý sau)")
    
    while True:
        choice = input("\n➤ Chọn (0/1/2/r/Enter/s): ").strip().lower()
        
        if choice == 's':
            return 'SKIP'
        elif choice == 'r':
            return ''
        elif choice == '':
            return current_value
        elif choice in NUMBER_TO_LABEL:
            return NUMBER_TO_LABEL[choice]
        else:
            print("❌ Không hợp lệ! Vui lòng nhập 0, 1, 2, r, Enter hoặc s")

def majority_vote_with_review(values, annotations, text, label, 
                              min_agreement=2, auto_mode=False, use_weighted=True):
    """
    Voting với option review thủ công và weighted voting
    
    Args:
        values: List các giá trị
        annotations: List annotations gốc
        text: Text content
        label: Label name
        min_agreement: Số vote tối thiểu
        auto_mode: Nếu True, tự động dùng weighted voting, không hỏi
        use_weighted: Nếu True, sử dụng weighted voting system
    
    Returns:
        Tuple (value, confidence, needs_review, reviewed_by_manager)
    """
    if not values:
        return "", 1.0, False, False
    
    counter = Counter(values)
    most_common_value, most_common_count = counter.most_common(1)[0]
    total_votes = len(values)
    confidence = most_common_count / total_votes
    
    # Calculate weighted vote
    weighted_winner, weighted_score, weight_details = weighted_vote(values, annotations)
    
    # Nếu đủ agreement (simple majority), không cần review
    if most_common_count >= min_agreement:
        # Check if weighted winner agrees with simple majority
        if use_weighted and weighted_winner != most_common_value:
            # Có conflict giữa simple majority và weighted vote
            needs_review = True
            if auto_mode:
                # Auto mode: chọn theo người có điểm cao nhất
                highest_vote = get_highest_weighted_vote(values, annotations)
                return highest_vote, confidence, True, False
            else:
                # Interactive mode: tự động chọn theo người có điểm cao nhất
                highest_vote = get_highest_weighted_vote(values, annotations)
                return highest_vote, confidence, True, False
        else:
            # No conflict, use simple majority
            return most_common_value, confidence, False, False
    
    # Không đủ agreement, cần review
    needs_review = True
    
    if auto_mode:
        # Auto mode: chọn theo người có điểm cao nhất
        if use_weighted:
            # Lấy vote của người có weight cao nhất
            highest_vote = get_highest_weighted_vote(values, annotations)
            return highest_vote, confidence, True, False
        else:
            # Fallback to priority
            priority_order = ['Negative', 'Neutral', 'Positive', '']
            for priority_val in priority_order:
                if priority_val in values:
                    return priority_val, confidence, True, False
    else:
        # Interactive mode: nếu dùng weighted, tự động chọn luôn
        if use_weighted:
            # Tự động chọn vote của người có điểm cao nhất, không hỏi
            highest_vote = get_highest_weighted_vote(values, annotations)
            return highest_vote, confidence, True, False
        else:
            # Chỉ hỏi khi không dùng weighted
            display_annotations(text, label, annotations, values)
            
            priority_order = ['Negative', 'Neutral', 'Positive', '']
            suggested = next((v for v in priority_order if v in values), '')
            
            print(f"\n💡 Gợi ý (priority): {suggested if suggested else '(Rỗng)'}")
            
            manager_decision = get_manager_decision(suggested)
            
            if manager_decision == 'SKIP':
                return suggested, confidence, True, False
            else:
                return manager_decision, confidence, True, True

def consensus_with_manager_review(input_file, output_file=None, 
                                 min_agreement=2, interactive=True,
                                 review_only_no_agreement=True, use_weighted=True):
    """
    Tạo consensus với review của người quản lý và weighted voting
    
    Args:
        input_file: File CSV input
        output_file: File CSV output
        min_agreement: Số vote tối thiểu (2 = cần 2/3 đồng ý)
        interactive: True = hỏi người quản lý, False = auto weighted voting
        review_only_no_agreement: True = chỉ review khi hoàn toàn không đồng thuận
        use_weighted: True = sử dụng weighted voting system
    """
    print(f"\n{'='*70}")
    print(f"🎯 CONSENSUS VOTING VỚI MANAGER REVIEW")
    print(f"{'='*70}")
    print(f"📁 File: {input_file}")
    print(f"🎚️  Min agreement: {min_agreement}/{3}")
    print(f"👤 Interactive mode: {'Yes' if interactive else 'No (Auto)'}")
    print(f"⚖️  Weighted voting: {'Yes' if use_weighted else 'No'}")
    print(f"📋 Review only no-agreement: {'Yes' if review_only_no_agreement else 'No'}")
    
    if use_weighted:
        print(f"\n👥 User Weights:")
        for user, weight in sorted(USER_WEIGHTS.items(), key=lambda x: x[1], reverse=True):
            print(f"   {user:20} : {weight:.1f}")
        print(f"   {'(others)':20} : {DEFAULT_WEIGHT:.1f}")
    
    if interactive:
        print(f"\n⚠️  Chế độ interactive: Bạn sẽ được hỏi khi có disagreement")
        input("\n➤ Nhấn Enter để bắt đầu...")
    
    # Đọc dữ liệu
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    label_columns = [
        'Battery',
        'Camera',
        'Performance',
        'Display',
        'Design',
        'Software',
        'Packaging',
        'Price',
        'Warranty',
        'Shop_Service',
        'Shipping',
        'General',
        'Others',
    ]
    
    # Nhóm theo ID
    annotations_by_id = defaultdict(list)
    for row in rows:
        annotations_by_id[row['id']].append(row)
    
    print(f"\n📊 Tổng annotations: {len(rows)}")
    print(f"📝 Số texts unique: {len(annotations_by_id)}")
    
    # Tạo consensus
    consensus_data = []
    stats = {
        'total_items': 0,
        'total_labels': 0,
        'needs_review': 0,
        'reviewed_by_manager': 0,
        'perfect': 0,
        'majority': 0,
        'no_agreement': 0,
    }
    
    item_count = 0
    total_items = len(annotations_by_id)
    
    for item_id, annotations in sorted(annotations_by_id.items()):
        item_count += 1
        stats['total_items'] += 1
        text = annotations[0]['data']
        
        print(f"\n\n{'='*70}")
        print(f"📍 Progress: {item_count}/{total_items} texts")
        print(f"🆔 ID: {item_id}")
        
        consensus_row = {
            'data': text,
            'id': item_id,
            'num_annotators': len(annotations),
            'manager_reviewed_labels': []
        }
        
        for label in label_columns:
            stats['total_labels'] += 1
            values = [normalize_label_value(ann[label]) for ann in annotations]
            
            # Kiểm tra có cần review không
            counter = Counter(values)
            max_votes = counter.most_common(1)[0][1]
            
            # Quyết định có review không
            if review_only_no_agreement:
                # Chỉ review khi hoàn toàn không đồng thuận (1/1/1)
                should_review = (max_votes < 2)  # Không có giá trị nào ≥ 2 votes
            else:
                # Review khi không đủ min_agreement
                should_review = (max_votes < min_agreement)
            
            if should_review:
                result, confidence, needs_review, reviewed = majority_vote_with_review(
                    values, annotations, text, label, 
                    min_agreement, auto_mode=not interactive, use_weighted=use_weighted
                )
                
                if needs_review:
                    stats['needs_review'] += 1
                if reviewed:
                    stats['reviewed_by_manager'] += 1
                    consensus_row['manager_reviewed_labels'].append(label)
            else:
                # Không cần review, lấy majority
                result = counter.most_common(1)[0][0]
                confidence = max_votes / len(values)
                
                if max_votes == len(values):
                    stats['perfect'] += 1
                else:
                    stats['majority'] += 1
            
            consensus_row[label] = result
        
        consensus_row['manager_reviewed_labels'] = ','.join(consensus_row['manager_reviewed_labels'])
        consensus_data.append(consensus_row)
    
    # Tạo output file
    if output_file is None:
        input_path = Path(input_file)
        mode = "interactive" if interactive else "auto"
        output_file = input_path.parent / f"{input_path.stem}_consensus_{mode}.csv"
    
    # Ghi file
    print(f"\n\n{'='*70}")
    print(f"💾 Đang ghi file: {output_file}")
    
    fieldnames = ['data'] + label_columns + ['id', 'num_annotators', 'manager_reviewed_labels']
    
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(consensus_data)
    
    # Báo cáo
    print(f"\n{'='*70}")
    print(f"📊 THỐNG KÊ KẾT QUẢ")
    print(f"{'='*70}")
    print(f"Tổng texts:                {stats['total_items']}")
    print(f"Tổng labels:               {stats['total_labels']}")
    print(f"Labels perfect agreement:  {stats['perfect']} ({stats['perfect']/stats['total_labels']*100:.1f}%)")
    print(f"Labels majority agreement: {stats['majority']} ({stats['majority']/stats['total_labels']*100:.1f}%)")
    print(f"Labels cần review:         {stats['needs_review']} ({stats['needs_review']/stats['total_labels']*100:.1f}%)")
    print(f"Labels đã review bởi QA:   {stats['reviewed_by_manager']} ({stats['reviewed_by_manager']/stats['total_labels']*100:.1f}%)")
    
    print(f"\n✅ Hoàn thành!")
    print(f"📁 File output: {output_file}")

def main():
    if len(sys.argv) < 2:
        print("❌ Cần chỉ định file input")
        print(f"\nCách sử dụng:")
        print(f"  python {Path(__file__).name} <input> [output] [options]")
        print(f"\nOptions:")
        print(f"  --auto              : Chế độ tự động (không hỏi, dùng weighted voting)")
        print(f"  --min-agreement N   : Số vote tối thiểu (1-3, mặc định 2)")
        print(f"  --review-all        : Review tất cả cases không đủ agreement")
        print(f"  --no-weighted       : Tắt weighted voting, dùng simple majority")
        print(f"\nVí dụ:")
        print(f"  # Interactive mode với weighted voting")
        print(f"  python {Path(__file__).name} data_label/2.csv")
        print(f"\n  # Auto mode với weighted voting")
        print(f"  python {Path(__file__).name} data_label/2.csv output.csv --auto")
        print(f"\n  # Review tất cả cases không có 2/3 agreement")
        print(f"  python {Path(__file__).name} data_label/2.csv --review-all")
        print(f"\n  # Không dùng weighted voting")
        print(f"  python {Path(__file__).name} data_label/2.csv --no-weighted")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    
    # Parse arguments
    output_file = None
    interactive = True
    min_agreement = 2
    review_only_no_agreement = True
    use_weighted = True
    
    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == '--auto':
            interactive = False
        elif arg == '--min-agreement' and i + 1 < len(sys.argv):
            min_agreement = int(sys.argv[i + 1])
        elif arg == '--review-all':
            review_only_no_agreement = False
        elif arg == '--no-weighted':
            use_weighted = False
        elif not arg.startswith('--') and output_file is None:
            output_file = Path(arg)
    
    if not input_file.exists():
        print(f"❌ Không tìm thấy file {input_file}")
        sys.exit(1)
    
    try:
        consensus_with_manager_review(
            input_file, output_file, min_agreement, 
            interactive, review_only_no_agreement, use_weighted
        )
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Đã hủy bởi người dùng")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

