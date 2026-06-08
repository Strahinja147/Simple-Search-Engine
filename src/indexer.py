import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
import pickle
from src.text_processor import ClearText
from src.data_loader import LoadDataset

def BuildPositionalIndex(documents, use_stemmer=True):
    positional_index = {}
    for doc_id, doc_info in documents.items():
        plot_text = doc_info["plot"]
        tokens = ClearText(plot_text, use_stemmer=use_stemmer)
        
        for pos, term in enumerate(tokens):
            if term not in positional_index:
                positional_index[term] = {}
            if doc_id not in positional_index[term]:
                positional_index[term][doc_id] = []
            positional_index[term][doc_id].append(pos)
    return positional_index

def CalculateTfidfMetadata(documents, positional_index):
    idf_dict = {}
    doc_lengths = {}
    N = len(documents) 
    
    for doc_id in documents.keys():
        doc_lengths[doc_id] = 0.0
        
    for term, postings in positional_index.items():
        df = len(postings)
        idf = math.log(N / df)
        idf_dict[term] = idf
        
        for doc_id, positions in postings.items():
            tf = len(positions)      
            tf_idf = tf * idf        
            doc_lengths[doc_id] += (tf_idf ** 2)
            
    for doc_id in doc_lengths.keys():
        doc_lengths[doc_id] = math.sqrt(doc_lengths[doc_id])
    return idf_dict, doc_lengths

def CreateChampionLists(positional_index, k=50):
    champion_lists = {}
    for term, postings in positional_index.items():
        doc_tf_pairs = [(doc_id, len(positions)) for doc_id, positions in postings.items()]
        doc_tf_pairs.sort(key=lambda x: x[1], reverse=True)
        
        top_k_pairs = doc_tf_pairs[:k]
        champion_lists[term] = [doc_id for doc_id, tf in top_k_pairs]
    return champion_lists

def SaveIndex(filepath, index_data):
    with open(filepath, 'wb') as file:
        pickle.dump(index_data, file)
    print(f"   -> Indeks je uspešno sačuvan na putanji: {filepath}")

def GenerateAndSaveIndex(documents, use_stemmer, filepath):
    """Omotač funkcija za kompletno pravljenje i čuvanje jednog indeksa."""
    print(f"\n--- PRAVIM INDEKS (Stemer uključen: {use_stemmer}) ---")
    positional_index = BuildPositionalIndex(documents, use_stemmer=use_stemmer)
    print(f"   -> Pozicioni indeks napravljen. Jedinstvenih reči: {len(positional_index)}")
    
    idf_dict, doc_lengths = CalculateTfidfMetadata(documents, positional_index)
    champion_lists = CreateChampionLists(positional_index, k=50)
    
    final_index_data = {
        "positional_index": positional_index,
        "idf_dict": idf_dict,
        "doc_lengths": doc_lengths,
        "champion_lists": champion_lists
    }
    SaveIndex(filepath, final_index_data)

if __name__ == "__main__":
    DATA_PATH = "data/wiki_movie_plots_deduped.csv"
    INDEX_STEMMED_PATH = "data/index_stemmed.pkl"
    INDEX_RAW_PATH = "data/index_raw.pkl"
    
    print("1. Učitavam veliki dataset...")
    documents = LoadDataset(DATA_PATH, is_json=False)
    print(f"Uspešno učitano {len(documents)} filmova.")
    
    GenerateAndSaveIndex(documents, use_stemmer=True, filepath=INDEX_STEMMED_PATH)
    
    GenerateAndSaveIndex(documents, use_stemmer=False, filepath=INDEX_RAW_PATH)
    
    print("\nSVE JE GOTOVO! Oba indeksa su generisana i sačuvana.")