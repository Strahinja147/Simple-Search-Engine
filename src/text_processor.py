import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download('stopwords')
ENG_STOP_WORDS = set(stopwords.words('english'))
stemmer = PorterStemmer()

def ClearText(text, use_stemmer=True):
    words = re.sub(r'[^\w\s]', "", text.lower()).split()
    if use_stemmer:
        filteredText = [stemmer.stem(w) for w in words if w not in ENG_STOP_WORDS]
    else:
        filteredText = [w for w in words if w not in ENG_STOP_WORDS]
     
    return filteredText

text = input("Unesi tekst: ")
print(ClearText(text))