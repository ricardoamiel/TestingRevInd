import os
import math
import heapq
from collections import defaultdict, deque
import re
import nltk
import numpy as np
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import pandas as pd
import time
nltk.download('punkt')

with open('BD2/stoplist.txt', 'r') as file:
    stoplist = file.read().splitlines()
stoplist += ['.', ',', ';', ':', '!', '?', '¿', '¡', '(', ')', '[', ']', '{', '}', '"', "'", '``', "''","111âº","111º","«","»","ª","º","ºc","ð","π","_","è","à"]

# Cargar Stopwords en español e inglés
stopwords_es = set(stopwords.words('spanish'))
stopwords_en = set(stopwords.words('english'))

# Cargar Stemmer en español e inglés
stemmer_es = SnowballStemmer("spanish")
stemmer_en = SnowballStemmer("english")

def remove_non_english_spanish(text):
    # This regular expression pattern matches any word that contains characters not in the English or Spanish alphabets
    pattern = r'[^\x00-\x7FÀ-ÿ]'
    # Use the re.sub() function to replace those words with an empty string
    text = re.sub(pattern, '', text)
    return text

def preprocesamiento(text, language):
    # Seleccionar stopwords y stemmer según el idioma
    if language == 'es':
        stemmer = stemmer_es
        stoplist_local = stopwords_es
    elif language == 'en':
        stemmer = stemmer_en
        stoplist_local = stopwords_en
    
    # Combinar stopwords con la stoplist adicional
    stoplist_local.update(stoplist)
    
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
    text = [word for word in text if word not in stoplist_local]
    # Filtrar números
    text = [word for word in text if not word.isdigit()]
    # Stemming
    text = [stemmer.stem(word) for word in text]
    # Eliminar tokens vacíos
    text = [word for word in text if word]
    # Remover palabras no pertenecientes al idioma
    text = [remove_non_english_spanish(word) for word in text]
    # Unir tokens en un solo string
    text = ' '.join(text)
    return text


# Construcción del Índice Invertido usando SPIMI
def spimi_invert(token_stream, block_size):
    output_file = open(f"block_{spimi_invert.block_count}.txt", "w", encoding='utf-8')
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

def parse_docs(documents, languages):
    token_stream = deque()
    for doc_id, text in documents.items():
        language = languages[doc_id]
        tokens = preprocesamiento(text, language).split()
        for token in tokens:
            token_stream.append((token, doc_id))
    return token_stream

'''
estrategia 2 pointers
def merge_blocks(block_files, total_docs):
    term_dict = defaultdict(dict)
    doc_freq = defaultdict(int)

    for block_file in block_files:
        with open(block_file, "r", encoding='utf-8') as f:
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
    with open("final_index.txt", "w", encoding='utf-8') as f:
        for term, postings in sorted_terms:
            if doc_freq[term] == 0: # si no aparece en ningun documento, idf = 0
                idf = 0
            idf = math.log10((total_docs / doc_freq[term]))
            postings_str = " ".join([f"{doc_id}:{round((1 + math.log10(tf)) * idf,2)}" for doc_id, tf in postings.items()])
            f.write(f"{term} {postings_str}\n")
            
    print("Índice invertido construido con éxito")'''

# Estrategia de mezcla de bloques con heap y 2 punteros
def merge_blocks(block_files, total_docs):
    term_dict = defaultdict(dict)
    doc_freq = defaultdict(int)

    heap = []
    file_pointers = []

    # Inicializar los punteros de archivo
    for i, block_file in enumerate(block_files):
        f = open(block_file, "r", encoding='utf-8')
        file_pointers.append(f)
        line = f.readline()
        if line:
            term, postings = line.strip().split(' ', 1)
            heapq.heappush(heap, (term, postings, i))  # Almacena el índice en lugar del objeto de archivo

    while heap:
        term, postings, file_index = heapq.heappop(heap)
        f = file_pointers[file_index]  # Usa el índice para recuperar el objeto de archivo
        if term not in term_dict:
            term_dict[term] = defaultdict(int)
        postings_list = postings.split()
        for posting in postings_list:
            doc_id, tf = posting.split(':')
            doc_id = int(doc_id)
            tf = int(tf)
            term_dict[term][doc_id] += tf
            doc_freq[term] += 1

        next_line = f.readline()
        if next_line:
            next_term, next_postings = next_line.strip().split(' ', 1)
            heapq.heappush(heap, (next_term, next_postings, file_index))

    # Cerrar todos los archivos
    for f in file_pointers:
        f.close()

    sorted_terms = term_dict.items()
    with open("final_index.txt", "w", encoding='utf-8') as f:
        for term, postings in sorted_terms:
            if doc_freq[term] == 0: # si no aparece en ningun documento, idf = 0
                idf = 0
            else:
                idf = math.log10(1 + (total_docs / len(term_dict[term])))
            postings_str = " ".join([f"{doc_id}:{round((1 + math.log10(tf)) * idf, 2)}" for doc_id, tf in postings.items()])
            f.write(f"{term} {postings_str}\n")

    print("Índice invertido construido con éxito")



def build_index(documents, languages, block_size):
    total_docs = len(documents)
    token_stream = parse_docs(documents, languages)
    block_files = []
    while token_stream:
        block_file = spimi_invert(token_stream, block_size)
        block_files.append(block_file)
    merge_blocks(block_files, total_docs)

musics = pd.read_csv('BD2/spotify_songs.csv')

# filtrar solo músicas en español o ingles
musics = musics[(musics['language'] == 'es') | (musics['language'] == 'en')]
#resetear indices
musics = musics.reset_index(drop=True)

# unir en una sola columna el nombre de la canción, el nombre del artista, el nombre del album y las letras de la canción
musics['lyrics'] = musics['track_name'] + ' ' + musics['track_artist'] + ' ' + musics['track_album_name'] + ' ' + musics['lyrics']

# crear diccionario de canciones
documentos_sin_procesar = {}
track_info = {}
for i in range(len(musics)):
    documentos_sin_procesar[i] = musics['lyrics'][i]
    track_info[i] = {'track_name': musics['track_name'][i], 'track_artist': musics['track_artist'][i]}

languages = musics['language']

build_index(documentos_sin_procesar, languages, 8192) # 4096

# Cargar el índice invertido
index = defaultdict(dict)
with open("final_index.txt", "r", encoding="utf-8") as f:
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

def cosine_similarity(query, index, norms, k, language): # search
    scores = defaultdict(float)
    query_tokens = preprocesamiento(query, language).split()
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
        print(f"Song {doc_id}: {docs[doc_id]}, Score: {score}")

Query1 = "Sunflower Post Malone and Swae Lee"
Query2 = "Ricky Martin y sus conciertos"
result = cosine_similarity(Query1, index, norms, 2,'en')
result2 = cosine_similarity(Query2, index, norms, 2,'es')
print(result)
retrieval_documents(result, documentos_sin_procesar)
print("*"*50)
retrieval_documents(result2, documentos_sin_procesar)
print("*"*50)
print(preprocesamiento("Latina (feat. Maluma) Reykon Latina (feat. Maluma)",'es').split())

