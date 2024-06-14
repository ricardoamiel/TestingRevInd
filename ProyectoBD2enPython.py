import os
import math
import heapq
from collections import defaultdict, deque
import re
import nltk
import numpy as np
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
import pandas as pd
import time
nltk.download('punkt')

# Preprocesamiento: Tokenización, Stopword Removal, Stemming
stemmer = SnowballStemmer("spanish")

with open('BD2/stoplist.txt', 'r') as file:
    stoplist = file.read().splitlines()
stoplist += ['.', ',', ';', ':', '!', '?', '¿', '¡', '(', ')', '[', ']', '{', '}', '"', "'", '``', "''","111âº","111º","«","»"]

def preprocesamiento(text):
    if text is None:
        return ""
    # Reemplazar siglas con puntos por la misma sigla sin puntos
    text = re.sub(r'\b(\w\.)+\b', lambda match: match.group(0).replace('.', ''), text)
    # Separar números de las palabras
    text = re.sub(r'(\d+)', r' \1 ', text)
    # Tokenizar, tratando la puntuación como tokens separados
    tokenizer = RegexpTokenizer(r'\w+|\$[\d\.]+|\S+')
    text = tokenizer.tokenize(text)
    # Normalizar: convertir a minúsculas
    text = [word.lower() for word in text]
    # Eliminar signos de puntuación
    text = [re.sub(r'[^\w\s]', '', word) for word in text]
    # Filtrar stopwords
    text = [word for word in text if word not in stoplist]
    # Filtrar números
    text = [word for word in text if not word.isdigit()]
    # Stemming
    text = [stemmer.stem(word) for word in text]
    # Unir los tokens en una cadena y eliminar espacios extra
    text = ' '.join(text).replace('  ', ' ') ####################
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
            if doc_freq[term] == 0: # si no aparece en ningun documento, idf = 0
                idf = 0
            idf = math.log10(1 + (total_docs / len(term_dict[term])))
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
  
#pasar libros sin procesar a un diccionario
librillos_sin_procesar ={}
i = 1
for file_name in textos:
  file = open('BD2/docs/'+file_name, encoding='utf-8')
  texto = file.read().rstrip()
  librillos_sin_procesar[i] = texto
  i += 1

for doc_id, text in librillos.items():
    librillos[doc_id] = preprocesamiento(text)

dataton = pd.read_csv('BD2/df_total.csv')
#solo guardar 100 documentos
dataton = dataton.head(25)

# crear diccionario de documentos
documentos_sin_procesar = {}
for i in range(len(dataton)):
    documentos_sin_procesar[i] = dataton['news'][i]
    
documentos_procesados = {}
for doc_id, text in documentos_sin_procesar.items():
    documentos_procesados[doc_id] = preprocesamiento(text)

#build_index(documents, 7)
#build_index(librillos, 500)
build_index(documentos_sin_procesar, 800)



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

def cosine_similarity(query, index, norms, k): # search
    scores = defaultdict(float)
    query_tokens = preprocesamiento(query).split()
    query_tf = defaultdict(int)
    for token in query_tokens:
        query_tf[token] += 1
    query_vector = {token: 1 + math.log10(tf) for token, tf in query_tf.items() if token in index}
    
    query_norm = math.sqrt(sum((1 + math.log10(tf))**2 for tf in query_tf.values() if tf > 0))
    
    for token, weight in query_vector.items():
        if token in index:
            for doc_id, tfidf in index[token].items():
                scores[doc_id] += weight * tfidf
    
    for doc_id in scores:
        scores[doc_id] /= query_norm * norms[doc_id]
    result = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
    return result

def retrieval_documents(result, docs):
    for doc_id, score in result:
        print(f"Documento {doc_id}: {docs[doc_id]}, Score: {score}")

#result = cosine_similarity("debido a la codicia desperto frodo sam ithilien", index, norms, 2)
#print(result)
#retrieval_documents(result, librillos_sin_procesar)


Query1 = "El pais de China y su cooperacion"
result = cosine_similarity(Query1, index, norms, 3)
print(f'{result}')
retrieval_documents(result, documentos_sin_procesar)

def retrieval_documents(result, docs):
    for doc_id, score in result:
        print(f"Documento {doc_id}: {docs[doc_id]}, Score: {score}")

#result = cosine_similarity("debido a la codicia desperto frodo sam ithilien", index, norms, 2)
#print(result)
#retrieval_documents(result, librillos_sin_procesar)

#print(cosine_similarity("por la muerte de gandalf",index,norms,2))

Query1 = "El pais de China y su cooperacion"
result = cosine_similarity(Query1, index, norms, 3)
print(result)
retrieval_documents(result, documentos_sin_procesar)

#print(cosine_similarity("criptomon",index,norms,2))
print(preprocesamiento("criptomonedas y aconsejar").split())