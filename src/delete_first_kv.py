import os
import json

def remove_first_kv_pair(directory):
    # Iterate over all files in the given directory
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            
            # Open and load the JSON file
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Process each entry in the JSON data
            for entry in data:
                # Remove the first key-value pair
                if entry:
                    first_key = next(iter(entry))
                    del entry[first_key]
            
            # Save the modified data back to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

# Example usage
directory_path = 'data/character_jsons'
remove_first_kv_pair(directory_path)