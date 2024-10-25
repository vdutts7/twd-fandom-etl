import streamlit as st
import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import unicodedata

# Load environment variables
load_dotenv()

# Initialize Pinecone with the correct API key and environment
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=pinecone_api_key)

index_name = "twd-fandom6"

# Check if the index exists and use it
if index_name not in pc.list_indexes().names():
    st.error(f"Index '{index_name}' not found. Please make sure the index exists in your Pinecone account.")
else:
    index = pc.Index(index_name)

# Load the pre-trained model used for upserting
model = SentenceTransformer('all-MiniLM-L6-v2')  # Same model as in your upsert script

# Function to generate embeddings for queries
def generate_embedding(query):
    return model.encode(query).tolist()  # Convert to list for Pinecone compatibility

# Function to ensure ASCII vector IDs (optional, useful for character IDs but not needed for queries)
def to_ascii(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

def search_characters(query, top_k=5):
    # Generate the embedding for the query using the same model as the one used for upserting
    query_vector = generate_embedding(query)
    
    # Query Pinecone index
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )
    return results['matches']

st.title("The Walking Dead Character Search")

query = st.text_input("Enter your search query:")

if query:
    results = search_characters(query)
    
    for result in results:
        st.subheader(result['metadata'].get('Name', 'Unknown'))
        st.write(f"Similarity Score: {result['score']:.2f}")
        
        overview = result['metadata'].get('Overview[]', 'No overview available.')
        st.write(overview[:200] + "..." if len(overview) > 200 else overview)
        
        with st.expander("More Details"):
            st.write("Pre-Apocalypse:")
            st.write(result['metadata'].get('Pre-Apocalypse[]', 'No information available.'))
            
            st.write("Post-Apocalypse:")
            st.write(result['metadata'].get('Post-Apocalypse[]', 'No information available.'))
            
            st.write("Killed Victims:")
            st.write(result['metadata'].get('Killed Victims[]', 'No information available.'))
            
            st.write("Trivia:")
            st.write(result['metadata'].get('Trivia[]', 'No trivia available.'))
        
        st.write("---")

st.sidebar.title("About")
st.sidebar.info("This app allows you to search for characters from The Walking Dead TV series. Enter a query to find characters with similar attributes or storylines.")
