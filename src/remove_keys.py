import os
import json

def remove_keys_from_json(directory, keys_to_remove):
    # Iterate over all files in the given directory
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            
            # Open and load the JSON file
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Process each entry in the JSON data
            for entry in data:
                # Remove specified keys if they exist
                for key in keys_to_remove:
                    if key in entry:
                        del entry[key]
            
            # Write the modified data back to the JSON file
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

# Specify the directory and keys to remove
json_directory = 'data/character_jsons'
keys_to_remove = ["Fate", "Contents", "Relationships[]", "Gallery[]"]

# Call the function
remove_keys_from_json(json_directory, keys_to_remove)