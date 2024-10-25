import os
import json
import unicodedata
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Pinecone with API key from environment variable
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=pinecone_api_key)

# Create or connect to an index
index_name = "twd-fandom6"
pc.create_index(
    name=index_name,
    dimension=384,  # Example dimension, adjust as needed
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)

# Load a pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to encode character data
def encode_character_data(character_data):
    text_data = " ".join([character_data.get(field, '') for field in ['Overview[]', 'Pre-Apocalypse[]', 'Post-Apocalypse[]', 'Death[]', 'Killed Victims[]', 'Appearances[]', 'Trivia[]']])
    vector = model.encode(text_data)
    
    # Truncate metadata to fit within the 40KB limit
    truncated_metadata = {}
    total_size = 0
    for key, value in character_data.items():
        item_size = len(key.encode('utf-8')) + len(str(value).encode('utf-8'))
        if total_size + item_size > 40000:  # Leave some buffer
            break
        truncated_metadata[key] = value
        total_size += item_size
    
    return vector, truncated_metadata

# Function to ensure ASCII vector IDs
def to_ascii(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

# Directory containing JSON files
json_directory = 'data/character_jsons'

# Connect to the index
index = pc.Index(index_name)

# Iterate over each JSON file
for filename in os.listdir(json_directory):
    if filename.endswith('.json'):
        file_path = os.path.join(json_directory, filename)
        
        # Load the JSON data
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Upsert each character's data
        for character in data:
            vector, metadata = encode_character_data(character)
            character_id = to_ascii(character.get('Name', filename))
            index.upsert([(character_id, vector.tolist(), metadata)])

