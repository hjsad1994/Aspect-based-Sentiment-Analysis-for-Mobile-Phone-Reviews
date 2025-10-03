import pandas as pd
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('merge_phase_csv.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def merge_csv_files():
    try:
        base_dir = Path('D:/AI_Tranning')
        data_result_dir = base_dir / 'data_result'
        
        input_files = [
            data_result_dir / 'Phase1-SubPhase1.csv',
            data_result_dir / 'Phase1-SubPhase2.csv',
            data_result_dir / 'Phase1-SubPhase3.csv'
        ]
        
        output_file = data_result_dir / 'Phase1-Merged.csv'
        
        # Check if all input files exist
        for file in input_files:
            if not file.exists():
                logging.error(f"Input file not found: {file}")
                return
        
        # Create backup if output file exists
        if output_file.exists():
            backup_file = data_result_dir / f'Phase1-Merged_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            logging.info(f"Output file exists. Creating backup: {backup_file}")
            output_file.rename(backup_file)
        
        # Read and merge CSV files
        dataframes = []
        for file in input_files:
            logging.info(f"Reading: {file.name}")
            df = pd.read_csv(file, encoding='utf-8')
            logging.info(f"  - Rows: {len(df)}, Columns: {len(df.columns)}")
            dataframes.append(df)
        
        # Concatenate all dataframes
        logging.info("Merging data...")
        merged_df = pd.concat(dataframes, ignore_index=True)
        
        # Save merged data
        logging.info(f"Saving merged data to: {output_file}")
        merged_df.to_csv(output_file, index=False, encoding='utf-8')
        
        # Report statistics
        logging.info("=" * 60)
        logging.info("MERGE COMPLETE")
        logging.info("=" * 60)
        logging.info(f"Total records: {len(merged_df)}")
        logging.info(f"Total columns: {len(merged_df.columns)}")
        logging.info(f"Columns: {', '.join(merged_df.columns)}")
        logging.info(f"Output file: {output_file}")
        
        # Show record count per source
        total = 0
        for i, df in enumerate(dataframes, 1):
            logging.info(f"Records from Phase1-SubPhase{i}: {len(df)}")
            total += len(df)
        logging.info(f"Total records (verification): {total}")
        
    except Exception as e:
        logging.error(f"Error during merge: {e}", exc_info=True)

if __name__ == "__main__":
    merge_csv_files()
