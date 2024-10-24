import os
import pandas as pd

def clean_csv_file(file_path):
    try:
        # Read the CSV file
        df = pd.read_csv(file_path, keep_default_na=False)

        # Clean each cell by removing extra newlines
        for column in df.columns:
            df[column] = df[column].apply(lambda x: ' '.join(str(x).split()))

        # Save the cleaned CSV back to the file
        df.to_csv(file_path, index=False)
        print(f"Cleaned {file_path}")

    except Exception as e:
        print(f"Error cleaning {file_path}: {e}")

def clean_all_csv_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            clean_csv_file(file_path)

# Specify the directory containing the CSV files
csv_directory = 'data/character_data'
clean_all_csv_files(csv_directory)

