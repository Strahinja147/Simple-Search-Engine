import math
import pickle

from text_processor import ClearText
from data_loader import LoadDataset

"""
{
    "babi": {
        "1": [3]  # Reč "babi" (baby) je u filmu "1" na poziciji 3 (indeks kreće od 0)
    },
    "stop": {
        "1": [4], # Reč "stop" je u filmu "1" na poziciji 4
        "10": [35] # i u filmu "10" na poziciji 35
    }
}

"""

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
    print(f"Indeks je uspešno sačuvan na putanji: {filepath}")

if __name__ == "__main__":
    JSON_PATH = "data/toy_dataset.json"
    INDEX_OUTPUT_PATH = "data/index.pkl"
    
    print("1. Učitavam test podatke...")
    documents = LoadDataset(JSON_PATH, is_json=True)
    
    print("2. Pravim pozicioni indeks...")
    positional_index = BuildPositionalIndex(documents, use_stemmer=True)
    
    print("3. Računam TF-IDF metapodatke...")
    idf_dict, doc_lengths = CalculateTfidfMetadata(documents, positional_index)
    
    print("4. Pravim Champion liste (K=5)...")
    champion_lists = CreateChampionLists(positional_index, k=5)
    
    print("5. Pakujem i snimam sve na disk...")
    final_index_data = {
        "positional_index": positional_index,
        "idf_dict": idf_dict,
        "doc_lengths": doc_lengths,
        "champion_lists": champion_lists
    }
    SaveIndex(INDEX_OUTPUT_PATH, final_index_data)
    
    print("\n--- TEST REZULTATA ---")
    print(f"Reč 'stop' se nalazi u {len(positional_index.get('stop', []))} filma.")
    print(f"IDF za reč 'stop': {idf_dict.get('stop', 0):.4f}")
    print(f"Šampionska lista za 'stop' (Top 5): {champion_lists.get('stop', [])}")