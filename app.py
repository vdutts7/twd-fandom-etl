import streamlit as st
import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import unicodedata
from openai import OpenAI

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

def search_characters(query, trait=None, top_k=5):
    query_vector = generate_embedding(query)
    
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )
    
    if trait:
        filtered_results = [r for r in results['matches'] if trait.lower() in r['metadata'].get('Overview[]', '').lower()]
        return filtered_results[:top_k]
    return results['matches']

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_ai_response(query, search_results):
    # Prepare the prompt with search results
    prompt = f"Query: {query}\n\nSearch Results:\n"
    for result in search_results[:3]:  # Use top 3 results
        prompt += f"- {result['metadata'].get('Name', 'Unknown')}: {result['metadata'].get('Overview[]', 'No overview available.')[:200]}...\n"
    
    prompt += "\nBased on the query and search results, provide a concise and informative response:"

    # Generate response using OpenAI API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant knowledgeable about The Walking Dead TV series."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    
    return response.choices[0].message.content.strip()

# Set page config
st.set_page_config(page_title="The Walking Dead Character Search", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for dark maroon background
st.markdown("""
    <style>
    .stApp {
        background-color: #4A0E0E;
        color: #FFFFFF;
    }
    .stButton>button {
        background-color: #800000;
        color: #FFFFFF;
    }
    .stTextInput>div>div>input {
        background-color: #2B0000;
        color: #FFFFFF;
    }
    .stTextArea>div>div>textarea {
        background-color: #2B0000;
        color: #FFFFFF;
    }
    .stSelectbox>div>div>select {
        background-color: #2B0000;
        color: #FFFFFF;
    }
    .sidebar .sidebar-content {
        background-color: #1A0000;
    }
    header {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #FFD700;'>The Walking Dead Character Database</h1>", unsafe_allow_html=True)

query = st.text_input("Enter your search query:", key="query_input")
trait = st.text_input("Enter a character trait or role (optional):", key="trait_input")

if query:
    results = search_characters(query, trait)
    
    # Generate AI response
    ai_response = generate_ai_response(query, results)
    st.markdown("<h2 style='color: #FFD700;'>AI Response:</h2>", unsafe_allow_html=True)
    st.write(ai_response)
    
    st.markdown("<h2 style='color: #FFD700;'>Search Results:</h2>", unsafe_allow_html=True)
    for result in results:
        st.markdown(f"<h3 style='color: #FFD700;'>{result['metadata'].get('Name', 'Unknown')}</h3>", unsafe_allow_html=True)
        st.write(f"Similarity Score: {result['score']:.2f}")
        
        overview = result['metadata'].get('Overview[]', 'No overview available.')
        st.write(overview[:200] + "..." if len(overview) > 200 else overview)
        
        with st.expander("More Details"):
            st.markdown("<h4 style='color: #FFD700;'>Pre-Apocalypse:</h4>", unsafe_allow_html=True)
            st.write(result['metadata'].get('Pre-Apocalypse[]', 'No information available.'))
            
            st.markdown("<h4 style='color: #FFD700;'>Post-Apocalypse:</h4>", unsafe_allow_html=True)
            st.write(result['metadata'].get('Post-Apocalypse[]', 'No information available.'))
            
            st.markdown("<h4 style='color: #FFD700;'>Killed Victims:</h4>", unsafe_allow_html=True)
            st.write(result['metadata'].get('Killed Victims[]', 'No information available.'))
            
            st.markdown("<h4 style='color: #FFD700;'>Trivia:</h4>", unsafe_allow_html=True)
            st.write(result['metadata'].get('Trivia[]', 'No trivia available.'))
        
        st.markdown("---")

st.sidebar.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color: #1A0000;
    }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("About")
st.sidebar.info("This app allows you to search for characters from The Walking Dead TV series. Enter a query to find characters with similar attributes or storylines.")
