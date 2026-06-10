import os
import sys
import re  

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import time
from src.data_loader import LoadDataset
from src.search_engine import LoadIndex, ExecuteQuery
from src.text_processor import ClearText  

st.set_page_config(page_title="Simple Search Engine", page_icon="🔍", layout="wide")

st.markdown(
    """
    <style>
    /* Podešavanje širine levog panela */
    [data-testid="stSidebar"] {
        min-width: 300px;
        max-width: 300px;
    }
    /* Proširenje desnog panela (glavnog dela sa pretragom i rezultatima) na 1100px */
    [data-testid="stAppViewBlockContainer"] {
        max-width: 1100px;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


INDEX_STEMMED_PATH = "data/index_stemmed.pkl"
INDEX_RAW_PATH = "data/index_raw.pkl"
DATA_PATH = "data/wiki_movie_plots_deduped.csv"

def generate_snippet(plot_text, query, use_stemmer=True, context=100):
   
    query_processed = set(ClearText(query, use_stemmer=use_stemmer))
    if not query_processed:
        return plot_text[:300] + "..."

    text_lower = plot_text.lower()
    first_idx = -1
    raw_words = set(query.replace('"', '').lower().split())
    search_terms = raw_words.union(query_processed)
    
    for term in search_terms:
        idx = text_lower.find(term)
        if idx != -1 and (first_idx == -1 or idx < first_idx):
            first_idx = idx
            
    if first_idx == -1:
        first_idx = 0
        
    start = max(0, first_idx - context)
    end = min(len(plot_text), first_idx + context + 80)
    snippet = plot_text[start:end]
    
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(plot_text) else ""
    
    highlight_style = 'background-color: #ffe873; color: #000000; font-weight: bold; padding: 0 2px; border-radius: 3px;'
    parts = re.split(r'([a-zA-Z0-9_]+)', snippet)
    
    for i, part in enumerate(parts):
        if part.isalnum():
            
            part_processed = ClearText(part, use_stemmer=use_stemmer)
            
            if part_processed and part_processed[0] in query_processed:
                parts[i] = f'<mark style="{highlight_style}">{part}</mark>'
                
    highlighted_snippet = "".join(parts)
    return prefix + highlighted_snippet + suffix


@st.cache_resource
def load_all_data():
    index_data_stemmed = LoadIndex(INDEX_STEMMED_PATH)
    index_data_raw = LoadIndex(INDEX_RAW_PATH)
    documents = LoadDataset(DATA_PATH, is_json=False)
    return index_data_stemmed, index_data_raw, documents

index_data_stemmed, index_data_raw, documents = load_all_data()

st.sidebar.title("⚙️ Settings")
st.sidebar.markdown("Manage search algorithms and parameters:")

use_champions = st.sidebar.checkbox(
    "Enable Champion Lists", 
    value=False, 
    help="Discards low-weight documents and searches only the Top-K best for a significant speedup."
)

use_stemmer = st.sidebar.checkbox(
    "Use Porter Stemmer", 
    value=True, 
    help="Reduces words to their root (e.g., 'running' -> 'run')."
)

st.title("🔍 Mini Movie Search Engine")
st.markdown("*Enter keywords or search exact phrases using quotes.*")

query = st.text_input("What are you looking for?", "")

if st.button("Search") or query:
    if query.strip() == "":
        st.warning("Please enter a search term.")
    else:
        
        active_index_data = index_data_stemmed if use_stemmer else index_data_raw
        
        start_time = time.time()
        
        results = ExecuteQuery(query, active_index_data, use_stemmer=use_stemmer, use_champions=use_champions)
        
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000 
        
        st.success(f"Found **{len(results)}** results in **{elapsed_time:.2f} ms**")
        
        if len(results) == 0:
            st.info("No matches found for your query. Try different words.")
        else:
            st.markdown("### Top Results:")
            for rank, (doc_id, score) in enumerate(results[:10], 1):
                doc = documents[doc_id]
                title = doc["title"]
                
                snippet = generate_snippet(doc["plot"], query, use_stemmer=use_stemmer)
                
                with st.container():
                    st.markdown(f"#### {rank}. {title} (Score: {score:.4f})")
                    st.markdown(f"*{snippet}*", unsafe_allow_html=True)
                    st.divider()