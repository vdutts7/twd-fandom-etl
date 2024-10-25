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
    sources = []
    for i, result in enumerate(search_results[:3], 1):  # Use top 3 results
        name = result['metadata'].get('Name', 'Unknown')
        overview = result['metadata'].get('Overview[]', 'No overview available.')[:200]
        prompt += f"[{i}] {name}: {overview}...\n"
        sources.append({"name": name, "content": overview})
    
    prompt += "\nBased on the query and search results, provide a concise and informative response. Cite sources using [1], [2], [3] as appropriate:"

    # Generate response using OpenAI API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant knowledgeable about The Walking Dead TV series. Always cite your sources using [1], [2], [3] when providing information."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
    )
    
    return response.choices[0].message.content.strip(), sources

# Set page config
st.set_page_config(page_title="The Walking Dead Character Search", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for Perplexity-like styling
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    .stTextInput > div > div > input {
        background-color: #1E1E1E;
        color: #FFFFFF;
        border: 1px solid #333333;
    }
    .stButton > button {
        background-color: #1E1E1E;
        color: #FFFFFF;
        border: 1px solid #333333;
    }
    .stMarkdown {
        color: #CCCCCC;
    }
    .source-bubble {
        display: inline-block;
        background-color: #333333;
        color: #FFFFFF;
        border-radius: 20px;
        padding: 5px 10px;
        margin: 5px;
        font-size: 14px;
    }
    .source-bubble:hover {
        background-color: #444444;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

# Main layout
col1, col2 = st.columns([2, 3])

with col1:
    st.markdown("<h1 style='color: #FFFFFF;'>The Walking Dead Character Search</h1>", unsafe_allow_html=True)
    query = st.text_input("Enter your search query:", key="query_input")
    trait = st.text_input("Enter a character trait or role (optional):", key="trait_input")
    
    if st.button("Search"):
        if query:
            results = search_characters(query, trait)
            
            # Generate AI response
            ai_response, sources = generate_ai_response(query, results)
            
            # Display sources as bubbles
            st.markdown("<h3 style='color: #FFFFFF;'>Sources:</h3>", unsafe_allow_html=True)
            source_html = "<div>"
            for i, source in enumerate(sources, 1):
                source_html += f"<span class='source-bubble' data-result-id='{i-1}' title='{source['content']}'>[{i}] {source['name']}</span>"
            source_html += "</div>"
            st.markdown(source_html, unsafe_allow_html=True)
            
            # Add JavaScript for handling source bubble clicks
            st.markdown("""
            <script>
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.addedNodes.length) {
                        mutation.addedNodes.forEach((node) => {
                            if (node.nodeType === 1 && node.matches('.source-bubble')) {
                                node.addEventListener('click', () => {
                                    const resultId = node.getAttribute('data-result-id');
                                    const expander = document.querySelector(`[data-testid="expander"][aria-controls="result_${resultId}-content"]`);
                                    if (expander) {
                                        expander.click();
                                    }
                                });
                            }
                        });
                    }
                });
            });
            observer.observe(document.body, { childList: true, subtree: true });
            </script>
            """, unsafe_allow_html=True)
            
            # Display AI response
            st.markdown("<h3 style='color: #FFFFFF;'>Answer:</h3>", unsafe_allow_html=True)
            st.write(ai_response)

with col2:
    if query:
        st.markdown("<h2 style='color: #FFFFFF;'>Search Results:</h2>", unsafe_allow_html=True)
        for i, result in enumerate(results):
            with st.expander(f"{result['metadata'].get('Name', 'Unknown')} (Score: {result['score']:.2f})"):
                st.markdown("<h4 style='color: #FFFFFF;'>Overview:</h4>", unsafe_allow_html=True)
                overview = result['metadata'].get('Overview[]', 'No overview available.')
                st.write(overview[:200] + "..." if len(overview) > 200 else overview)
                
                st.markdown("<h4 style='color: #FFFFFF;'>Pre-Apocalypse:</h4>", unsafe_allow_html=True)
                st.write(result['metadata'].get('Pre-Apocalypse[]', 'No information available.'))
                
                st.markdown("<h4 style='color: #FFFFFF;'>Post-Apocalypse:</h4>", unsafe_allow_html=True)
                st.write(result['metadata'].get('Post-Apocalypse[]', 'No information available.'))
                
                st.markdown("<h4 style='color: #FFFFFF;'>Killed Victims:</h4>", unsafe_allow_html=True)
                st.write(result['metadata'].get('Killed Victims[]', 'No information available.'))
                
                st.markdown("<h4 style='color: #FFFFFF;'>Trivia:</h4>", unsafe_allow_html=True)
                st.write(result['metadata'].get('Trivia[]', 'No trivia available.'))

# Sidebar
st.sidebar.markdown("<h2 style='color: #FFFFFF;'>About</h2>", unsafe_allow_html=True)
st.sidebar.info("This app allows you to search for characters from The Walking Dead TV series. Enter a query to find characters with similar attributes or storylines.")
st.sidebar.markdown("<h3 style='color: #FFFFFF;'>How to use:</h3>", unsafe_allow_html=True)
st.sidebar.markdown("1. Enter your search query in the main text box.")
st.sidebar.markdown("2. Optionally, enter a character trait or role to refine your search.")
st.sidebar.markdown("3. Click the 'Search' button to get results.")
st.sidebar.markdown("4. View the AI-generated response and explore detailed character information.")
