import os
import math
import heapq
from collections import defaultdict, deque
import re
import nltk
import numpy as np
from nltk.stem.snowball import SnowballStemmer
nltk.download('punkt')

stemmer = SnowballStemmer("spanish")

with open('BD2/stoplist.txt', 'r') as file:
    stoplist = file.read().splitlines()
stoplist += ['.', ',', ';', ':', '!', '?', '¿', '¡', '(', ')', '[', ']', '{', '}', '"', "'", '``', "''","111âº"]  
  
# Preprocesamiento: Tokenización, Stopword Removal, Stemming
def preprocesamiento(text):
    #normalizar
    text = re.sub(r'[.,;:!?¿¡()\[\]{}"\'-]', '', text)
    #tokenizar
    text = nltk.word_tokenize(text)
    #normalizar parte 2
    text = [word.lower() for word in text]
    #filtrar stopwords
    text = [word for word in text if word not in stoplist]
    #stemming
    text = [stemmer.stem(word) for word in text]
    text = ' '.join(text)
    return text

# Construcción del Índice Invertido usando SPIMI
def spimi_invert(token_stream, block_size):
    output_file = open(f"block_{spimi_invert.block_count}.txt", "w")
    spimi_invert.block_count += 1
    
    dictionary = defaultdict(dict)
    
    while token_stream:
        token, doc_id = token_stream.popleft()
        if doc_id not in dictionary[token]:
            dictionary[token][doc_id] = 0
        dictionary[token][doc_id] += 1
        
        if len(dictionary) > block_size:
            break
    
    sorted_terms = sorted(dictionary.items())
    for term, postings in sorted_terms:
        postings_str = " ".join([f"{doc_id}:{tf}" for doc_id, tf in postings.items()])
        output_file.write(f"{term} {postings_str}\n")
    output_file.close()

    return output_file.name

spimi_invert.block_count = 0

def parse_docs(documents):
    token_stream = deque()
    for doc_id, text in documents.items():
        tokens = preprocesamiento(text).split()
        for token in tokens:
            token_stream.append((token, doc_id))
    return token_stream

def merge_blocks(block_files, total_docs):
    term_dict = defaultdict(dict)
    doc_freq = defaultdict(int)

    for block_file in block_files:
        with open(block_file, "r") as f:
            for line in f:
                term, postings = line.strip().split(' ', 1)
                postings_list = postings.split()
                for posting in postings_list:
                    doc_id, tf = posting.split(':')
                    doc_id = int(doc_id)
                    tf = int(tf)
                    if doc_id not in term_dict[term]:
                        term_dict[term][doc_id] = 0
                    term_dict[term][doc_id] += tf
                    doc_freq[term] += 1

    sorted_terms = sorted(term_dict.items())
    with open("final_index.txt", "w") as f:
        for term, postings in sorted_terms:
            idf = math.log10(total_docs / len(term_dict[term]))
            postings_str = " ".join([f"{doc_id}:{round((1 + math.log10(tf)) * idf,2)}" for doc_id, tf in postings.items()])
            f.write(f"{term} {postings_str}\n")
            
    print("Índice invertido construido con éxito")

def build_index(documents, block_size):
    total_docs = len(documents)
    token_stream = parse_docs(documents)
    block_files = []
    while token_stream:
        block_file = spimi_invert(token_stream, block_size)
        block_files.append(block_file)
    merge_blocks(block_files, total_docs)

# Ejemplo de uso
documents = {
    1: "El rápido zorro marrón salta sobre el perro perezoso",
    2: "Un zorro es un animal astuto",
    3: "El perro es el mejor amigo del hombre",
    4: "El perro y el zorro son amigos",
    5: "El hombre y el zorro son enemigos",
    6: "El gato es enemigo del perro",
    7: "El gato y el zorro son amigos",
    8: "El gato es astuto",
    9: "El gato es rápido",
    10: "El perro es fiel"
}

for doc_id, text in documents.items():
    documents[doc_id] = preprocesamiento(text)

textos = ["libro1.txt","libro2.txt","libro3.txt","libro4.txt","libro5.txt","libro6.txt"]
textos_procesados = []
indice = {} # para que sirve esto?  # para saber cuantas veces aparece una palabra en cada texto
librillos ={}
i = 1
for file_name in textos:
  file = open('BD2/docs/'+file_name)
  texto = file.read().rstrip()
  texto = preprocesamiento(texto)
  textos_procesados.append(texto)
  librillos[i] = texto
  i += 1

for doc_id, text in librillos.items():
    librillos[doc_id] = preprocesamiento(text)

#build_index(documents, 7)
build_index(librillos, 500)



# Cargar el índice invertido
index = defaultdict(dict)
with open("final_index.txt", "r") as f:
    for line in f:
        term, postings = line.strip().split(' ', 1)
        postings_list = postings.split()
        for posting in postings_list:
            doc_id, tfidf = posting.split(':')
            doc_id = int(doc_id)
            tfidf = float(tfidf)
            if doc_id not in index[term]:
                index[term][doc_id] = 0
            index[term][doc_id] += tfidf
            
# Calcular la norma de los documentos y guardarlo en un diccionario
def calculate_norms(index):
    norms = defaultdict(float)
    for term, postings in index.items():
        for doc_id, tfidf in postings.items():
            norms[doc_id] += tfidf ** 2
    for doc_id in norms:
        norms[doc_id] = math.sqrt(norms[doc_id])
    return norms

norms = calculate_norms(index)