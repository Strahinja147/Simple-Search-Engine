import csv
import json
from itertools import islice

def CreateToyDataset(csv_path, json_path):
    with open(csv_path, "r", newline='', encoding="utf-8") as csvFile:
        reader = csv.DictReader(csvFile)
        toy_data = {
            str(i + 1): {"title": row["Title"], "plot": row["Plot"]} 
            for i, row in enumerate(islice(reader, 10))
        }

    with open(json_path, "w", encoding="utf-8") as jsonFile:
        json.dump(toy_data, jsonFile, indent=4)
        

def LoadDataset(filepath, is_json=True):

    with open(filepath, "r", encoding="utf-8") as file:
         
        if is_json:
            data = json.load(file)
        else:
            reader = csv.DictReader(file)
            data = {
                str(i + 1): {"title": row["Title"], "plot": row["Plot"]} 
                for i, row in enumerate(reader)
            }
    return data

if __name__ == "__main__":
    
    CSV_PATH = "data/wiki_movie_plots_deduped.csv"
    JSON_PATH = "data/toy_dataset.json"
    
    print("Pravim 'toy_dataset.json'...")
    CreateToyDataset(CSV_PATH, JSON_PATH)
    print("Mali dataset je uspešno kreiran!")
    
    print("Testiram učitavanje malog dataseta...")
    test_data = LoadDataset(JSON_PATH, is_json=True)
    print(f"Učitano je {len(test_data)} filmova.")
    
    print("Prvi film:", test_data["1"])