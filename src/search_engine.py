import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
import pickle
from src.text_processor import ClearText
from src.data_loader import LoadDataset

def LoadIndex(filepath):
    """
    Učitava naš sačuvan indeks (.pkl fajl) nazad u memoriju.
    Vraća uređenu torku (tuple) sa 4 rečnika.
    """
    with open(filepath, 'rb') as file:
        data = pickle.load(file)
    
    return data["positional_index"], data["idf_dict"], data["doc_lengths"], data["champion_lists"]


def VectorSearch(query_tokens, index_data, use_champions=False):
    
    pos_index, idf_dict, doc_lengths, champ_lists = index_data
    
    query_tf = {}
    for term in query_tokens:
        query_tf[term] = query_tf.get(term, 0) + 1
        
    scores = {}       
    query_norm_sq = 0.0 
    
    for term, q_tf in query_tf.items():
        if term not in idf_dict:
            continue 
 
        idf = idf_dict[term]
        q_weight = q_tf * idf
        query_norm_sq += q_weight ** 2
        
        if use_champions:
            docs_to_check = champ_lists.get(term, []) 
        else:
            docs_to_check = pos_index.get(term, {}).keys() 
            
        for doc_id in docs_to_check:
            d_tf = len(pos_index[term][doc_id])
            d_weight = d_tf * idf
            scores[doc_id] = scores.get(doc_id, 0.0) + (q_weight * d_weight)
            
    query_norm = math.sqrt(query_norm_sq)
    if query_norm == 0:
        return [] 
        
    results = []
    for doc_id, dot_product in scores.items():
        d_norm = doc_lengths[doc_id]
        if d_norm > 0:
            cos_sim = dot_product / (query_norm * d_norm)
            results.append((doc_id, cos_sim))
            
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def PhraseSearch(query_tokens, index_data):
    
    pos_index = index_data[0] 
    
    for term in query_tokens:
        if term not in pos_index:
            return []
            
    candidate_docs = set(pos_index[query_tokens[0]].keys())
    for term in query_tokens[1:]:
        candidate_docs.intersection_update(pos_index[term].keys())
        
    results = []
    
    for doc_id in candidate_docs:
        first_term_positions = pos_index[query_tokens[0]][doc_id]
        
        match_found = False
        for start_pos in first_term_positions:
            is_match = True
            
            for i in range(1, len(query_tokens)):
                next_term = query_tokens[i]
                expected_pos = start_pos + i
                
                if expected_pos not in pos_index[next_term][doc_id]:
                    is_match = False
                    break
                    
            if is_match:
                match_found = True
                break
            
        if match_found:
            results.append((doc_id, 1.0))
            
    return results


def ExecuteQuery(query, index_data, use_stemmer=True, use_champions=False):
    
    query = query.strip()
    is_phrase = False
    
    if query.startswith('"') and query.endswith('"'):
        is_phrase = True
        
    query_tokens = ClearText(query, use_stemmer=use_stemmer)
    
    if not query_tokens:
        return []
        
    if is_phrase:
        return PhraseSearch(query_tokens, index_data)
    else:
        return VectorSearch(query_tokens, index_data, use_champions=use_champions)


if __name__ == "__main__":
    INDEX_PATH = "data/index.pkl"
    JSON_PATH = "data/toy_dataset.json"
    
    print("Učitavam indeks sa diska...")
    index_data = LoadIndex(INDEX_PATH)
    
    print("Učitavam tekstove filmova radi lepšeg prikaza...")
    documents = LoadDataset(JSON_PATH, is_json=True)
    
    upit1 = "bartender saloon beer"
    print(f"\n--- PRETRAGA SLOBODNOG TEKSTA: {upit1} ---")
    rezultati1 = ExecuteQuery(upit1, index_data, use_stemmer=True, use_champions=False)
    
    for doc_id, skor in rezultati1:
        naslov = documents[doc_id]["title"]
        print(f"[{skor:.4f}] {naslov}")

    upit2 = '"bartender is working"'
    print(f"\n--- PRETRAGA TAČNE FRAZE: {upit2} ---")
    rezultati2 = ExecuteQuery(upit2, index_data, use_stemmer=True)
    
    for doc_id, skor in rezultati2:
        naslov = documents[doc_id]["title"]
        print(f"[{skor:.4f}] {naslov}")