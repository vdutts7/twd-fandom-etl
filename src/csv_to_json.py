import os
import pandas as pd
import json

def convert_csv_to_json(csv_file_path, json_file_path):
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path, keep_default_na=False)

        # Convert the DataFrame to a dictionary
        data_dict = df.to_dict(orient='records')

        # Write the dictionary to a JSON file
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data_dict, json_file, ensure_ascii=False, indent=4)

        print(f"Converted {csv_file_path} to {json_file_path}")

    except Exception as e:
        print(f"Error converting {csv_file_path}: {e}")

def convert_all_csv_to_json(csv_directory, json_directory):
    if not os.path.exists(json_directory):
        os.makedirs(json_directory)

    for filename in os.listdir(csv_directory):
        if filename.endswith('.csv'):
            csv_file_path = os.path.join(csv_directory, filename)
            json_file_name = filename.replace('.csv', '.json')
            json_file_path = os.path.join(json_directory, json_file_name)
            convert_csv_to_json(csv_file_path, json_file_path)

# Specify the directories
csv_directory = 'data/character_data'
json_directory = 'data/character_jsons'
convert_all_csv_to_json(csv_directory, json_directory)

