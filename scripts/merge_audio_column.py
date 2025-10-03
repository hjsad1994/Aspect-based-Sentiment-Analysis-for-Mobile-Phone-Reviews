"""
Script to merge Audio column from audio-col.csv into Phase1-Merged_consensus_interactive.csv
with thorough validation and data integrity checks
"""
import csv
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Setup logging
log_file = Path('merge_audio_column.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def read_csv_file(file_path):
    """Read CSV file and return rows as list of dictionaries"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            logging.info(f"✓ Read {len(rows)} rows from {file_path.name}")
            return rows, reader.fieldnames
    except FileNotFoundError:
        logging.error(f"✗ File not found: {file_path}")
        raise
    except Exception as e:
        logging.error(f"✗ Error reading {file_path}: {e}")
        raise

def normalize_text(text):
    """Normalize text for comparison"""
    if text is None:
        return ""
    return text.strip()

def build_audio_lookup(audio_rows):
    """
    Build lookup dictionary from audio-col.csv
    Key: normalized data text
    Value: Audio column value
    
    Handles multiple annotations for same text by checking agreement
    """
    audio_lookup = {}
    duplicates = defaultdict(list)
    
    for row in audio_rows:
        data_text = normalize_text(row['data'])
        audio_value = row.get('Audio', '').strip()
        
        if data_text in audio_lookup:
            # Track duplicates
            duplicates[data_text].append({
                'audio': audio_value,
                'annotator': row.get('annotator', 'unknown'),
                'agreement': row.get('agreement', 'N/A')
            })
        else:
            audio_lookup[data_text] = audio_value
            duplicates[data_text].append({
                'audio': audio_value,
                'annotator': row.get('annotator', 'unknown'),
                'agreement': row.get('agreement', 'N/A')
            })
    
    return audio_lookup, duplicates

def validate_and_merge(main_file, audio_file, output_file):
    """
    Main function to validate and merge Audio column
    """
    logging.info("=" * 80)
    logging.info("AUDIO COLUMN MERGE - VALIDATION & PROCESSING")
    logging.info("=" * 80)
    
    # Validate file existence
    if not main_file.exists():
        logging.error(f"✗ Main file not found: {main_file}")
        return False
    
    if not audio_file.exists():
        logging.error(f"✗ Audio file not found: {audio_file}")
        return False
    
    logging.info(f"\n📁 Main file: {main_file.name}")
    logging.info(f"📁 Audio file: {audio_file.name}")
    
    # Read both files
    try:
        main_rows, main_fieldnames = read_csv_file(main_file)
        audio_rows, audio_fieldnames = read_csv_file(audio_file)
    except Exception as e:
        logging.error(f"✗ Failed to read input files: {e}")
        return False
    
    # Validate required columns
    if 'data' not in main_fieldnames:
        logging.error("✗ 'data' column not found in main file")
        return False
    
    if 'data' not in audio_fieldnames or 'Audio' not in audio_fieldnames:
        logging.error("✗ Required columns ('data', 'Audio') not found in audio file")
        return False
    
    logging.info(f"\n✓ Main file columns: {len(main_fieldnames)}")
    logging.info(f"✓ Audio file columns: {len(audio_fieldnames)}")
    
    # Build audio lookup
    logging.info("\n" + "=" * 80)
    logging.info("BUILDING AUDIO LOOKUP")
    logging.info("=" * 80)
    audio_lookup, duplicates = build_audio_lookup(audio_rows)
    logging.info(f"✓ Built lookup for {len(audio_lookup)} unique text entries")
    
    # Check for duplicates with different Audio values
    conflicts = []
    for data_text, entries in duplicates.items():
        if len(entries) > 1:
            audio_values = set(e['audio'] for e in entries)
            if len(audio_values) > 1:
                conflicts.append({
                    'text': data_text[:50] + '...' if len(data_text) > 50 else data_text,
                    'entries': entries
                })
    
    if conflicts:
        logging.warning(f"\n⚠️  Found {len(conflicts)} texts with conflicting Audio values:")
        for conflict in conflicts[:5]:  # Show first 5
            logging.warning(f"  Text: {conflict['text']}")
            for entry in conflict['entries']:
                logging.warning(f"    - {entry['annotator']}: '{entry['audio']}' (agreement: {entry['agreement']})")
        if len(conflicts) > 5:
            logging.warning(f"  ... and {len(conflicts) - 5} more conflicts")
    
    # Merge process
    logging.info("\n" + "=" * 80)
    logging.info("MERGING AUDIO COLUMN")
    logging.info("=" * 80)
    
    merged_rows = []
    stats = {
        'total': len(main_rows),
        'matched': 0,
        'not_matched': 0,
        'empty_audio': 0,
        'has_audio': 0
    }
    
    unmatched_texts = []
    
    for i, main_row in enumerate(main_rows, 1):
        data_text = normalize_text(main_row['data'])
        
        # Create merged row (copy all fields from main)
        merged_row = main_row.copy()
        
        # Check if we have Audio data for this text
        if data_text in audio_lookup:
            audio_value = audio_lookup[data_text]
            merged_row['Audio'] = audio_value
            stats['matched'] += 1
            
            if audio_value:
                stats['has_audio'] += 1
            else:
                stats['empty_audio'] += 1
        else:
            # No match found in audio file
            merged_row['Audio'] = ''
            stats['not_matched'] += 1
            unmatched_texts.append({
                'row': i,
                'text': data_text[:80] + '...' if len(data_text) > 80 else data_text
            })
        
        merged_rows.append(merged_row)
        
        # Progress logging
        if i % 100 == 0:
            logging.info(f"  Processed {i}/{stats['total']} rows...")
    
    # Report unmatched entries
    if unmatched_texts:
        logging.warning(f"\n⚠️  {len(unmatched_texts)} rows not matched in audio file:")
        for entry in unmatched_texts[:10]:  # Show first 10
            logging.warning(f"  Row {entry['row']}: {entry['text']}")
        if len(unmatched_texts) > 10:
            logging.warning(f"  ... and {len(unmatched_texts) - 10} more unmatched")
    
    # Prepare output fieldnames (insert Audio after Others)
    output_fieldnames = list(main_fieldnames)
    
    # Check if Audio column already exists
    if 'Audio' in output_fieldnames:
        logging.info("\n✓ Audio column already exists in main file, will be overwritten")
    else:
        # Insert Audio column after 'Others' if it exists, otherwise at the end
        if 'Others' in output_fieldnames:
            others_index = output_fieldnames.index('Others')
            output_fieldnames.insert(others_index + 1, 'Audio')
            logging.info("\n✓ Audio column will be inserted after 'Others'")
        else:
            output_fieldnames.append('Audio')
            logging.info("\n✓ Audio column will be appended at the end")
    
    # Write merged file
    logging.info("\n" + "=" * 80)
    logging.info("WRITING OUTPUT FILE")
    logging.info("=" * 80)
    
    try:
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=output_fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(merged_rows)
        
        logging.info(f"✓ Successfully wrote {len(merged_rows)} rows to {output_file.name}")
    except Exception as e:
        logging.error(f"✗ Error writing output file: {e}")
        return False
    
    # Final statistics
    logging.info("\n" + "=" * 80)
    logging.info("MERGE STATISTICS")
    logging.info("=" * 80)
    logging.info(f"Total rows processed:           {stats['total']}")
    logging.info(f"Rows matched with audio file:   {stats['matched']} ({stats['matched']/stats['total']*100:.1f}%)")
    logging.info(f"  - With Audio data:            {stats['has_audio']}")
    logging.info(f"  - With empty Audio:           {stats['empty_audio']}")
    logging.info(f"Rows NOT matched:               {stats['not_matched']} ({stats['not_matched']/stats['total']*100:.1f}%)")
    
    if stats['not_matched'] > 0:
        logging.warning(f"\n⚠️  WARNING: {stats['not_matched']} rows have no matching Audio data!")
        logging.warning(f"   These rows will have empty Audio column in the output.")
    
    logging.info("\n" + "=" * 80)
    logging.info("MERGE COMPLETE")
    logging.info("=" * 80)
    logging.info(f"📁 Output file: {output_file}")
    logging.info(f"📋 Log file: {log_file}")
    
    return True

def main():
    # File paths
    base_dir = Path('D:/AI_Tranning/data_result')
    
    main_file = base_dir / 'Phase1-Merged_consensus_interactive.csv'
    audio_file = base_dir / 'audio-col.csv'
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = base_dir / f'Phase1-Merged_with_Audio_{timestamp}.csv'
    
    # Validate and merge
    success = validate_and_merge(main_file, audio_file, output_file)
    
    if success:
        print(f"\nSUCCESS!")
        print(f"Merged file created: {output_file}")
        print(f"Check log for details: {log_file}")
    else:
        print(f"\nFAILED!")
        print(f"Check log for errors: {log_file}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
