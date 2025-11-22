import pandas as pd
import glob
import os

def merge_auction_data():
    """
    Merges all CSV files from state-specific auction result directories
    into a single CSV file.
    """
    # The script is located in the same directory as the result folders.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the directories to search for CSVs
    dir_state_40 = os.path.join(script_dir, "auction_results_state_40")
    dir_state_50 = os.path.join(script_dir, "auction_results_state_50")
    
    print(f"Searching for CSV files in:\n- {dir_state_40}\n- {dir_state_50}")
    
    # Find all CSV files in both directories
    csv_files_40 = glob.glob(os.path.join(dir_state_40, "*.csv"))
    csv_files_50 = glob.glob(os.path.join(dir_state_50, "*.csv"))
    all_csv_files = csv_files_40 + csv_files_50
    
    if not all_csv_files:
        print("No CSV files found to merge.")
        return

    print(f"Found {len(all_csv_files)} CSV files to merge.")
    
    # Read and collect all DataFrames
    df_list = []
    for file in all_csv_files:
        # Exclude error logs if any
        if 'error_log.txt' in os.path.basename(file):
            continue
        try:
            df = pd.read_csv(file)
            df_list.append(df)
        except Exception as e:
            print(f"Could not read file {file}: {e}")

    if not df_list:
        print("No dataframes were created. Check the CSV files for issues.")
        return

    # Concatenate all DataFrames
    print("Concatenating all dataframes...")
    combined_df = pd.concat(df_list, ignore_index=True)
    
    # Define the output file path
    output_file = os.path.join(script_dir, "auction_data_combined.csv")
    
    # Save the combined DataFrame to a new CSV
    print(f"Saving combined data to '{output_file}'...")
    combined_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Successfully merged {len(all_csv_files)} files into '{os.path.basename(output_file)}'.")
    print(f"Total rows in combined file: {len(combined_df)}")

if __name__ == "__main__":
    merge_auction_data()
