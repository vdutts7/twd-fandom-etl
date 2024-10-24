import os
import json

def update_json_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            
            # Open and load the JSON file
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Update the first key-value pair in each JSON object
            for entry in data:
                if entry:
                    first_key = next(iter(entry))
                    entry["Name"] = first_key
                    entry[first_key] = first_key
            
            # Save the updated JSON back to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

# Specify the directory containing the JSON files
json_directory = 'data/character_jsons'
update_json_files(json_directory)