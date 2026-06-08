import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import time
from src.data_loader import LoadDataset
from src.search_engine import LoadIndex, ExecuteQuery

st.set_page_config(page_title="Simple Search Engine", page_icon="🔍", layout="centered")

INDEX_STEMMED_PATH = "data/index_stemmed.pkl"
INDEX_RAW_PATH = "data/index_raw.pkl"
DATA_PATH = "data/wiki_movie_plots_deduped.csv"

@st.cache_resource
def ucitaj_sve_podatke():
    
    index_data_stemmed = LoadIndex(INDEX_STEMMED_PATH)
    index_data_raw = LoadIndex(INDEX_RAW_PATH)
    documents = LoadDataset(DATA_PATH, is_json=False)
    return index_data_stemmed, index_data_raw, documents

index_data_stemmed, index_data_raw, documents = ucitaj_sve_podatke()

st.sidebar.title("⚙️ Podešavanja")
st.sidebar.markdown("Upravljaj pretragom i algoritmima:")

use_champions = st.sidebar.checkbox(
    "Uključi Champion liste", 
    value=False, 
    help="Odbacuje dokumente sa malom težinom i pretražuje samo Top-K najbolje za drastično ubrzanje."
)

use_stemmer = st.sidebar.checkbox(
    "Koristi Porter Stemer", 
    value=True, 
    help="Skraćuje reči na njihov koren (npr. 'running' -> 'run')."
)

st.title("🔍 Mini Pretraživač Filmova")
st.markdown("*Unesite ključne reči ili pretražujte tačne fraze pod navodnicima.*")

query = st.text_input("Šta tražite?", "")

if st.button("Pretraži") or query:
    if query.strip() == "":
        st.warning("Molimo vas unesite reč za pretragu.")
    else:
        
        active_index_data = index_data_stemmed if use_stemmer else index_data_raw
        
        start_time = time.time()
        
        rezultati = ExecuteQuery(query, active_index_data, use_stemmer=use_stemmer, use_champions=use_champions)
        
        end_time = time.time()
        proteklo_vreme = (end_time - start_time) * 1000 
        
        st.success(f"Pronađeno **{len(rezultati)}** rezultata za **{proteklo_vreme:.2f} ms**")
        
        if len(rezultati) == 0:
            st.info("Nema poklapanja za vaš upit. Pokušajte sa drugim rečima.")
        else:
            st.markdown("### Top Rezultati:")
            for rank, (doc_id, skor) in enumerate(rezultati[:10], 1):
                doc = documents[doc_id]
                naslov = doc["title"]
                
                iseckan_plot = doc["plot"][:300] + "..." if len(doc["plot"]) > 300 else doc["plot"]
                
                with st.container():
                    st.markdown(f"#### {rank}. {naslov} (Skor: {skor:.4f})")
                    st.write(f"*{iseckan_plot}*")
                    st.divider()