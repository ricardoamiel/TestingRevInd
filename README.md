# Búsqueda y Recuperación de la Información 
#### Integrantes: Ricardo Acuña, Gonzalo Perea, Isabella Romero, Rodrigo Lauz y Josué Velo

## Introducción
### Objetivo del proyecto
- Este proyecto fue desarrollado con el fin de facilitar la búsqueda de canciones a través de palabras específicas o de audios relacionados a través como por ejemplo las top 10 canciones más relacionadas al amor o tristeza. Esto simpilifica y devuelve los resultados más acorde a lo que buscamos en un tiempo mínimo. 
- Además, decidimos desarrollar una herramienta efectiva que facilite la búsqueda y el reconocimiento de canciones a través de sus características principales. Inspirado en aplicaciones como Shazam, este proyecto se centra en la extracción de vectores característicos de cada canción en una base de datos, lo que permite realizar búsquedas eficientes y precisas basadas en distintas características y similitudes entre canciones. Esta herramienta está diseñada para mejorar la experiencia del usuario en la identificación y descubrimiento de música, proporcionando resultados rápidos y relevantes que se ajusten a sus preferencias y necesidades musicales.

### Descripción del dominio de datos y la importancia de aplicar indexación
La base de datos contiene más de 17 mil registros de canciones con especificaciones como: nombre, artista, letra de la canción, popularidad, nombre del album, fecha de lanzamiento, género, instrumentos, etc. De las cuales, estamos usando principalmente las columnas del artista, nombre y letra de la canción para poder ingresar un conjunto de palabras y que devuelva las top k canciones que se relacionan más a las palabras ingresadas.
Es importante utilizar índices, ya que minimiza el tiempo de búsqueda de similitud en cantidades masivas de registros como en este caso. En lugar de iterar uno por uno, se genera una lista de palabras clave que estan relacionadas con cierto puntaje a cada canción. Luego este proceso será explicado más a fondo.

Por otro lado, nuestra base de datos multimedia contiene aproximadamente 24,000 canciones de distintos géneros y estilos, procesadas para extraer vectores característicos que capturan sus atributos esenciales. 
La indexación multidimensional es crucial para realizar búsquedas rápidas y precisas, permitiendo identificar canciones similares de manera eficiente. Esto asegura que, incluso con una base de datos extensa, las búsquedas sean ágiles y relevantes, optimizando el uso de recursos del sistema y mejorando la experiencia del usuario en la identificación y descubrimiento de música.


## Backend: Índice Invertido
### Construcción del índice invertido en memoria secundaria
Para construir un índice invertido en memoria secundaria, hemos utilizado una lógica basada en el tamaño de los bloques. Asumiendo un tamaño de bloque de 4096 bytes y considerando que para cada término guardamos su `doc_id` y su valor de `tf-idf`, estamos almacenando 8 bytes por registro (4 bytes para `doc_id` y 4 bytes para `tf-idf`). Esto permite almacenar hasta 4096 registros por bloque, con un total de 32,768 bytes por bloque. Si limitamos la construcción del índice invertido a usar 1MB de RAM, podemos calcular el número de índices invertidos locales como $\frac{1024 \times 1024}{4096 \times 8}$, lo que da aproximadamente 32 índices invertidos locales. Sin embargo, en la práctica, los registros pueden ocupar más espacio. Por ejemplo, si cada término aparece en 4 documentos y almacenamos 4 valores de `tf-idf` por término, el tamaño por registro sería 32 bytes (4 `doc_ids` y 4 `tf-idf`). Si limitamos la RAM a 4MB, el cálculo sería $\frac{4 \times 1024 \times 1024}{4096 \times 32}$, lo que también da aproximadamente 32 índices invertidos locales. Esto implica que un término puede aparecer en más de un índice invertido si alcanza el límite de tamaño del bloque.

Se ocuparon las siguientes librerías para el desarrollo del proyeco
```python
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
nltk.download('stopwords')
```

#### Preprocesamiento
Se trabajo con keywords en inglés y español, también se creó una función para remover letras que no pertenezcan al alfabeto de estos idiomas.

```python
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
```

Al final se llamó a todo el proceso: tokenizar, normalizar, stemming. Se guarda como un string
```python
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
```
#### Índice invertido

```python
def build_index(documents, languages, block_size):
    total_docs = len(documents)
    token_stream = parse_docs(documents, languages)
    block_files = []
    while token_stream:
        block_file = spimi_invert(token_stream, block_size)
        block_files.append(block_file)
    merge_blocks(block_files, total_docs)
```

##### Parsear documentos
Todos los records de nuestra bd son preprocesados, se comporta como una cola fifo, garantizando un pop en O(1).

```python
def parse_docs(documents, languages):
    token_stream = deque()
    for doc_id, text in documents.items():
        language = languages[doc_id]
        tokens = preprocesamiento(text, language).split()
        for token in tokens:
            token_stream.append((token, doc_id))
    return token_stream
```
##### Spimi
Se implementa la lógica de `block_size`, cada vez que se rompe esa condición, se crea un nuevo bloque para guardar nuevos 'buckets' para los keywords respectivos y se guarda en memoria secundaria.

```python
def spimi_invert(token_stream, block_size):
    output_file = open(os.getcwd() + "/blocks/" + f"block_{spimi_invert.block_count}.txt", "w", encoding='utf-8')
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
```

##### Merge Blocks
Se basa en una estrategia usando un min heap

```python
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
    with open(os.getcwd() + "/blocks/" + "final_index.txt", "w", encoding='utf-8') as f:
        for term, postings in sorted_terms:
            if doc_freq[term] == 0: # si no aparece en ningun documento, idf = 0
                idf = 0
            else:
                idf = math.log10(1 + (total_docs / len(term_dict[term])))
            postings_str = " ".join([f"{doc_id}:{round((1 + math.log10(tf)) * idf, 2)}" for doc_id, tf in postings.items()])
            f.write(f"{term} {postings_str}\n")

    print("Índice invertido construido con éxito")
```
* **Inicialización de Diccionarios y Heap:**
  ```python
  term_dict = defaultdict(dict)
  doc_freq = defaultdict(int)
  heap = []
  file_pointers = []
  ```

  - `term_dict`: Almacena los términos y sus frecuencias de documentos.
  - `doc_freq`: Almacena la frecuencia de documentos para cada término.
  - `heap`: Utilizado para mantener los términos en orden lexicográfico durante la mezcla.
  - `file_pointers`: Lista de punteros de archivos abiertos para leer bloques de términos.
* **Inicialización de Punteros de Archivo y Heap:**
  ```python
  for i, block_file in enumerate(block_files):
      f = open(block_file, "r", encoding='utf-8')
      file_pointers.append(f)
      line = f.readline()
      if line:
          term, postings = line.strip().split(' ', 1)
          heapq.heappush(heap, (term, postings, i))  # Almacena el índice en lugar del objeto de archivo
  ```

  - Abre cada archivo de bloque y lee la primera línea.
  - Cada línea se descompone en un término (`term`) y sus postings (`postings`).
  - Se añade una tupla al heap que contiene el término, postings y el índice del archivo (`i`).
* **Mezcla de Términos:**
  ```python
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
  ```

  - Extrae el término con menor valor lexicográfico del heap.
  - Actualiza `term_dict` con las postings del término extraído.
  - Lee la siguiente línea del archivo correspondiente y la añade al heap, manteniendo el orden.
* **Cierre de Archivos:**
  ```python
  for f in file_pointers:
      f.close()
  ```

  - Cierra todos los archivos de bloque después de procesarlos.
* **Construcción del Índice Invertido Final:**
  ```python
  sorted_terms = term_dict.items()
  with open(os.getcwd() + "/blocks/" + "final_index.txt", "w", encoding='utf-8') as f:
        for term, postings in sorted_terms:
            if doc_freq[term] == 0: # si no aparece en ningun documento, idf = 0
                idf = 0
            else:
                idf = math.log10(1 + (total_docs / len(term_dict[term])))
            postings_str = " ".join([f"{doc_id}:{round((1 + math.log10(tf)) * idf, 2)}" for doc_id, tf in postings.items()])
            f.write(f"{term} {postings_str}\n")

  ```
  - Los  términos en `term_dict` ya están ordenados gracias al heap lexicográficamente.
  - Calcula el IDF para cada término y construye la cadena de postings.
  - Escribe los términos y postings en el archivo `final_index.txt`.

### Ejecución óptima de consultas aplicando Similitud de Coseno
La similitud de coseno es una medida fundamental para comparar la similitud entre distintos archivos, en este caso, canciones. Se utiliza para calcular qué tan cercanas son dos canciones en términos de contenido, mediante la representación de cada canción como un vector de características basado en términos relevantes ponderados (como TF-IDF). Al aplicar la fórmula del coseno entre estos vectores, se obtiene un valor que indica la proximidad entre las canciones: valores cercanos a 1 denotan alta similitud, mientras que cercanos a 0 indican diferencias significativas. Esto permite realizar recomendaciones de canciones similares y agrupar por temas líricos comunes dentro de la base de datos musical de manera eficiente y precisa.

### Construcción del índice invertido en PostgreSQL
En PostgreSQL, la técnica para aplicar el índice invertido se denomina GIN (Generalized Inverted Index). GIN está diseñado para trabajar con valores compuestos, permitiendo la combinación de múltiples celdas en un solo índice. 
En este caso, los elementos del índice son archivos y las consultas son palabras o términos que queremos buscar en estos archivos específicos. El índice GIN almacena pares de clave (key) y postings lists, donde cada una es un conjunto de identificadores de filas (row IDs) correspondientes a los documentos en los que aparece la clave.

La estructura interna del índice GIN en PostgreSQL es un B-tree para almacenar claves (keys) y sus posting lists, lo que permite búsquedas eficientes en documentos textuales.
<img width="1040" alt="Screen Shot 2024-06-17 at 2 40 37 PM" src="https://github.com/ricardoamiel/TestingRevInd/assets/102993411/bad1dd0a-4751-4c00-9a66-12d6c9e2813c">
Cada clave se almacena solo una vez, haciendo el índice compacto. Los índices GIN multicolumna combinan valores de diferentes columnas en un solo B-tree. Esta estructura soporta consultas complejas y permite el desarrollo de tipos de datos personalizados, mejorando la eficiencia y rapidez de las búsquedas de texto completo.

Cuando se realiza una consulta que contiene múltiples términos (usando AND), PostgreSQL busca los documentos que contienen todos los términos especificados. Esto se hace combinando las listas de postings de cada término.

## Frontend Índice Invertido
Tenemos opción para colocar idioma y el valor de k para hayar los top k más relacionados.
Te devuelve el ID de la canción, nombre, lyrics, artista y score de similitud.
<img width="1440" alt="Screen Shot 2024-06-17 at 3 34 22 PM" src="https://github.com/ricardoamiel/TestingRevInd/assets/102993411/0e7ad3fb-bd60-40a3-b591-f5d5850b2737">
<img width="1439" alt="Screen Shot 2024-06-17 at 3 35 14 PM" src="https://github.com/ricardoamiel/TestingRevInd/assets/102993411/dcb2103d-e8f0-4752-bbd5-fd56f4b5fa7d">

### Índice invertido vs GiN PostgreSQL
Nuestro frontend muestra no solo los datos obtenidos usando nuestro índice invertido, también los del índice GiN en postgresql, además se puede visualizar estos mismos datos en formato json.
![](./imgs/1.jpg)
![](./imgs/2.jpg)
![](./imgs/3.jpg)

#### Conección con PostgreSQL

El experimento fue corrido en datagrip, en un principio la data se cargaba mediante el csv spotify_songs, por temas de reducir tiempo entre cargas, lo automatizamos mediante el script `TableCreation.py`.

Creamos una función `create_table` que recibe el usuario, la contraseña y la base de datos (asumiendo que trabajaremos en localhost y puerto 5432), creamos el schema `db2` y la tabla solo con las columnas que nos dan información (así evitamos cargar información extra y tarda menos en cargar la tabla). Después de ello, podemos insertar los datos mediante el método de `engine`.

Procedemos a crear los índices, este sería el código completo.

```python
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, text, inspect
from sqlalchemy.schema import CreateSchema
import os
def create_table(user, password, database):

    csv_file_path = os.getcwd() + "\BD2\spotify_songs_pj.csv"

    df = pd.read_csv(csv_file_path)
    # Conectar a la base de datos
    engine = create_engine(f'postgresql://{user}:{password}@localhost:5432/{database}')
    conn = engine.connect()

    # Crear esquema si no existe

    inspector = inspect(engine)
    schemas = inspector.get_schema_names()
    if 'db2' not in schemas:
        conn.execute(text("create schema db2;"))
        conn.commit()

    # Crear tabla

    metadata = MetaData()

    spotify_songs = Table(
        'spotify_songs', metadata,
        Column('track_name', String),
        Column('track_artist', String),
        Column('track_album_name', String),
        Column('lyrics', String),
        Column('language', String),
        Column('track_ID', Integer, primary_key=True),
        schema='db2'
        )

    metadata.create_all(engine)

    # Insertar datos en la tabla
    df.to_sql('spotify_songs', engine, if_exists='replace', schema='db2', index=False)

    conn.execute(text("ALTER TABLE db2.spotify_songs ADD COLUMN listo_index text;"))
    conn.execute(text("UPDATE db2.spotify_songs SET listo_index = CONCAT_WS(' ', track_name, track_artist, track_album_name, lyrics);"))

    # Creacion de indices

    conn.execute(text("CREATE INDEX idx_listo_index_spanish_gin ON db2.spotify_songs USING gin(to_tsvector('spanish', listo_index)) WHERE language = 'es';"))
    conn.execute(text("CREATE INDEX idx_listo_index_english_gin ON db2.spotify_songs USING gin(to_tsvector('english', listo_index))WHERE language = 'en';"))

    conn.commit()
```

#### Ejecución del código

Solo ejecutando `app.py` podrás escribir consultas en lenguaje natural en nuestra GUI, y ver las diferencias entre nuestro índice invertido y el índice GiN de PostgreSQL. **Al correr el programa te pedirá tu usuario, la base de datos y la contraseña de cuenta de localhost de postgres, si es la primera vez que corres el programa cuándo te pregunten si deseas crear la tabla acepta (y), las siguientes veces tendrás que colocar (n)**

```python
from flask import Flask, request, jsonify, render_template
import psycopg2
import time
import TableCreation

# Inputs
db_name = input("database[postgres]: ")  or 'postgres'
db_user = input('user[postgres]: ') or 'postgres'
db_password = input("password: ")

# Crear tabla en PostgreSQL
temp = ''

while temp != 'y' and temp != 'n':
    temp = input("¿Desea crear la tabla en PostgreSQL? [y/n]: ")
    
if temp == 'y':
    TableCreation.create_table(db_user, db_password, db_name)

import ProyectoBD2enPython as PBD

# Inicializar la aplicación Flask
app = Flask(__name__)

# Cargar el índice invertido y calcular normas
index = PBD.index
norms = PBD.calculate_norms(index)
docs = PBD.documentos_sin_procesar
track_info = PBD.track_info

# Conectar a PostgreSQL
conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host="localhost",
    port="5432"
)

my_table = 'db2.spotify_songs'

@app.route('/')
def home():
    return render_template('index.html')

# muestra el contenido de un top k documento
@app.route('/document', methods=['GET'])
def get_document():
    doc_id = request.args.get('doc_id', type=int)
    return {
        'lyrics': docs[doc_id],
        'track_name': track_info[doc_id]['track_name'],
        'track_artist': track_info[doc_id]['track_artist']
    }

# llama los top k documentos con sus scores
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    k = request.args.get('k', type=int)
    language = request.args.get('language')
    start_time = time.time()
    results = PBD.cosine_similarity(query, index, norms, k, language)
    duracion = time.time() - start_time
    response = { # puede haber error 
        'results': [{'doc_id': doc_id, 'score': score} for doc_id, score in results],
        'time': duracion
    }
    return jsonify(response)

# llama los top k documentos con sus scores desde PostgreSQL
@app.route('/search_postgresql', methods=['GET'])
def search_postgresql():
    query = request.args.get('query')
    k = request.args.get('k', type=int)
    language = request.args.get('language')
    
    ### convertir query separado por espacios en query separado por &
    ### ejemplo query = 'Feel Love' => query = 'Feel & Love'
    query = ' & '.join(query.split())

    if language == 'en':
        ts_query = f"to_tsquery('english', '{query}')"
    else:
        ts_query = f"to_tsquery('spanish', '{query}')"
        
    
    # transformar language == en => english o es => spanish
    if language == 'en':
        language = 'english'
    else:
        language = 'spanish'
    
    sql = f"""
        SELECT track_name, track_artist, track_album_name, listo_index,
               ts_rank(to_tsvector('{language}', listo_index), {ts_query}) AS rank
        FROM {my_table}
        WHERE to_tsvector('{language}', listo_index) @@ {ts_query}
        ORDER BY rank DESC
        LIMIT {k};
    """

    start_time = time.time()
    with conn.cursor() as cur:
        cur.execute(sql)
        results = cur.fetchall()
    duracion = time.time() - start_time

    response = {
        'results': [{'track_name': row[0], 'track_artist': row[1], 'track_album_name': row[2], 'lyrics': row[3], 'score': row[4]} for row in results],
        'time': duracion
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run()
```

## Experimentación
### Tablas y gráficos de los resultados experimentales
#### Query: "Feel Love"
<img width="1006" alt="Screen Shot 2024-06-17 at 5 28 15 PM" src="https://github.com/ricardoamiel/TestingRevInd/assets/102993411/27ef1366-061b-4d4c-9c99-266b5c204131">

#### Query: "Roar"
<img width="1086" alt="Screen Shot 2024-06-17 at 11 19 39 PM" src="https://github.com/ricardoamiel/TestingRevInd/assets/102993411/b3c89888-c3bb-4ebc-b83d-aa09fb41b0d0">
<https://docs.google.com/spreadsheets/d/1Hz1B3FfuxvhOOhrPeBV6ze1CJF0ue693COQl0Q4s_Cs/edit?usp=sharing>


### Análisis y discusión
Al investigar cómo funciona el índice GIN en PostgreSQL, notamos que este trabaja con el operador AND, realizando una intersección de palabras en las consultas. Por ejemplo, devuelve resultados de canciones que contengan tanto la palabra "feel" como "love", lo que incrementa el tiempo de búsqueda. Por otro lado, nuestro índice invertido utiliza el operador OR, lo que resulta en tiempos de búsqueda mucho menores, ya que realiza una unión y devuelve todas las canciones que contienen la palabra "feel" o "love". En términos de efectividad, ambos índices son útiles; el de PostgreSQL es más efectivo para encontrar coincidencias exactas en una oración o una frase compuesta, mientras que para búsquedas de palabras individuales, ambos métodos son igualmente efectivos.

Las similitudes cosenos implementadas son muy diferentes, y el factor principal de esto es la `metadata`, un motor de búsqueda de canciones como spotify se rige por el nombre del artista o el nombre de la canción, y el peso que tengan los keywords en ello deberían ser por obvias razones mayor que cualquier otro keyword que aparezca en las líricas de una canción, en caso contrario de un motor de búsqueda de papers donde sí se muestra más ese balance entre frecuencia de keywords y rareza de estos (`tf-idf`), es por ello la diferencia notoria en los score entre ambos índices.

El normalizar los vectores en la implementación de nuestro índice, ayuda a equilibrar las frecuencias de las palabras clave y asegurar que los resultados sean más consistentes y rápidos. PostgreSQL podría no estar normalizando en la misma medida, lo que puede generar variaciones significativas en los scores y, consecuentemente, en los tiempos de búsqueda dependiendo de la consulta. El no normalizar (en el caso del índice GIN) podría generar un desbalance entre la frecuencia y la rareza de los keywords, en consecuencia, una gran diferencia en los scores obtenidos dependiendo de la query (obteniendo scores muy altos o scores muy bajos).


## Backend: Índice Multidimensional
### Técnica de indexación de las librerías utilizadas

#### Faiss
**Faiss (Facebook AI Similarity Search)** es una biblioteca desarrollada por Facebook AI Research para realizar búsquedas de similitud y clustering en grandes conjuntos de datos de vectores. Utiliza una serie de técnicas de indexación, entre ellas:

- **Índice de Archivo Invertido (IVF):** Esta técnica acelera la búsqueda de similitudes dividiendo el conjunto de datos en múltiples clústeres o celdas. Cada celda corresponde a un clúster de vectores, y durante la consulta, solo se busca en un subconjunto de estas celdas, reduciendo así el número de comparaciones necesarias.

- **Índice Multi-invertido:** Es una extensión del índice de archivo invertido para búsquedas en espacios de alta dimensión. Utiliza una estructura de índice multinivel, particionando los datos a lo largo de varios niveles o dimensiones. Esto permite realizar búsquedas más granulares y eficientes en conjuntos de datos complejos y de alta dimensión.

- **Cuantización de Productos (PQ - Product Quantization):** Reduce la dimensión de los vectores descomponiéndolos en subvectores y cuantificándolos por separado. Esto mejora la rapidez de búsqueda y reduce el uso de memoria.

- **Índice Distribuido:** Faiss soporta índices distribuidos mediante una biblioteca RPC simple, que permite acceder a índices desde varias máquinas ("esclavos"). Cada esclavo contiene una parte del conjunto de datos (fragmento). Durante la búsqueda, el master emite la consulta a todos los esclavos, que procesan la consulta y envían los resultados de vuelta al maestro, que combina estos resultados en la salida final. Cabe destacar que el código de servidor y RPC proporcionado con Faiss es para fines de demostración y no incluye ciertas protecciones de seguridad, por lo que no está destinado a ejecutarse en redes no confiables o en entornos de producción.

### Como se realiza el KNN Search y el Range Search
- **Búsqueda KNN con Cola de Prioridad:** Se implementa un algoritmo K-Nearest Neighbors (KNN) que utiliza una cola de prioridad para encontrar los k vecinos más cercanos a un punto de consulta. Tras importar las librerías necesarias y cargar un archivo CSV en un DataFrame, se calcula la distancia euclidiana entre los puntos. La función mantiene los k vecinos más cercanos en la cola de prioridad y devuelve sus índices y distancias. Se evalúa el rendimiento del algoritmo con diferentes puntos de consulta y valores de k, midiendo el tiempo promedio de ejecución.
  
- **Búsqueda de Rango:** Se implementa una búsqueda de vecinos dentro de un rango específico usando características de canciones. Se importan las librerías necesarias, se carga un archivo CSV y se calculan distancias entre pares de canciones aleatorias. Se crea un histograma de distancias y se determinan radios de búsqueda mediante percentiles. La función rangeSearch busca canciones dentro de un radio alrededor de un punto de consulta. Se prueba la búsqueda para diferentes radios y se mide el tiempo promedio de ejecución.

### Análisis de la maldición de la dimensionalidad y como mitigarlo
- La maldición de la dimensionalidad afecta la eficacia de los algoritmos KNN al aumentar la dificultad de distinguir entre vecinos cercanos en espacios de alta dimensión. FAISS mitiga este problema mediante técnicas de indexación eficiente, como Product Quantization y HNSW, que optimizan la búsqueda en grandes conjuntos de datos de alta dimensión. En el proyecto, se utiliza un índice faiss.IndexFlatL2 para calcular distancias y realizar búsquedas, mostrando una reducción significativa en el tiempo de ejecución promedio al comparar con métodos no optimizados.

## Frontend
### Diseño de la GUI
#### Mini-manual de usuario
Para instalar y ejecutar el proyecto Frontend, sigue estos pasos:

1. **Cambiar al directorio "Frontend"**

    ```bash
    cd Frontend
    ```
    
2. **Instalar las dependencias del proyecto**

    ```bash
    npm install
    ```

3. **Ejecutar el proyecto**

    ```bash
    npm run dev
    ```
#### Screenshots de la GUI
### Análisis comparativo visual con otras implementaciones
- **Shazam**
<img width="1040" alt="Screen Shot 2024-06-17 at 2 40 37 PM" src="https://github.com/ricardoamiel/TestingRevInd/blob/main/imgs/WhatsApp Image 2024-07-18 at 11.10.31 PM.jpeg">
Esta aplicación, es mundialmente conocida por reconocer sonidos a tu alrededor y hacer match con alguna canción en su base de datos (están casi todas las canciones existentes)

- **Google Audio**
<img width="1040" alt="Screen Shot 2024-06-17 at 2 40 37 PM" src="https://github.com/ricardoamiel/TestingRevInd/blob/main/imgs/WhatsApp Image 2024-07-18 at 11.15.22 PM.jpeg">
<img width="1040" alt="Screen Shot 2024-06-17 at 2 40 37 PM" src="https://github.com/ricardoamiel/TestingRevInd/blob/main/imgs/WhatsApp Image 2024-07-18 at 11.15.37 PM.jpeg">
Esta opción en el navegador de Google se basa prácticamente en reconocer tu voz, en este caso, alguna canción que estes tarareando o cantando y te lleva al buscador de Google que te dará como resultado la canción más parecida o, en el mejor de los casos, a la canción que estás buscando.

## Experimentación
### Tabla de Resultados de los Algoritmo de Búsqueda KNN (que no requieren radio) 
| Tamaño de Datos | KNN Priority Queue | RTree KNN | HighD (knn_faiss) |
|-----------------|--------------------|-----------|------------------|
| 1k              | 3.280              | 0.000416  | 0.000396         |
| 2k              | 6.102              | 0.001113  | 0.000778         |
| 4k              | 12.977             | 0.005534  | 0.001001         |
| 8k              | 25.527             | 0.001432  | 0.002268         |
| 16k             | 49.965             | 0.023975  | 0.004762         |

### Gráfica de Resultados de los Algoritmos (KNN) 
<img width="1040" alt="Screen Shot 2024-06-17 at 2 40 37 PM" src="https://github.com/ricardoamiel/TestingRevInd/blob/main/imgs/Algoritmos.png">

### Tabla de Resultados del los Algoritmo de Búsqueda KNN (que no requieren radio) 
| Tamaño de Datos | Radio 1 | Tiempo 1 | Radio 2 | Tiempo 2 | Radio 3 | Tiempo 3 |
|-----------------|---------|----------|---------|----------|---------|----------|
| 1k              | 58.15   | 0.1739   | 72.75   | 0.1724   | 86.82   | 0.1743   |
| 2k              | 60.40   | 0.3452   | 76.06   | 0.3395   | 91.70   | 0.3536   |
| 4k              | 63.43   | 0.6835   | 79.89   | 0.6995   | 96.14   | 0.6690   |
| 8k              | 63.87   | 1.3710   | 79.53   | 1.3429   | 94.80   | 1.3910   |
| 16k             | 62.46   | 2.6490   | 77.87   | 2.6441   | 92.01   | 2.6570   |


### Gráfica de Resultados del Algoritmo Range KNN
<img width="1040" alt="Screen Shot 2024-06-17 at 2 40 37 PM" src="https://github.com/ricardoamiel/TestingRevInd/blob/main/imgs/Range_KNN.png">


### Tabla de Resultados de los Algoritmos de Búsqueda KNN 
| Tamaño de Datos | KNN Priority Queue | Range KNN | RTree KNN | HighD (knn_faiss)|
|-----------------|--------------------|------------|----------|--------------|
| 1k              | 3.280              | 0.1735     | 0.000416 | 0.000396    |
| 2k              | 6.102              | 0.3461     | 0.001113 | 0.000778    |
| 4k              | 12.977             | 0.6840     | 0.005534 | 0.001001    |
| 8k              | 25.527             | 1.3683     | 0.001432 | 0.002268    |
| 16k             | 49.965             | 2.6500     | 0.023975 | 0.004762    |

### Gráfica de Resultados de los Algoritmos de Búsqueda KNN
<img width="1040" alt="Screen Shot 2024-06-17 at 2 40 37 PM" src="https://github.com/ricardoamiel/TestingRevInd/blob/main/imgs/Tiempos.png?raw=true">

## Análisis y discusión
#### Tiempo de Ejecución

1. **HighD (knn_faiss)**:
   - **Mejor Tiempo de Ejecución**: `HighD (knn_faiss)` muestra el menor tiempo de ejecución en todos los tamaños de datos. Por ejemplo, para 16k datos, el tiempo de ejecución es 0.004762 segundos, superando ampliamente a los otros algoritmos. Esto lo hace ideal para aplicaciones donde el tiempo de respuesta es crítico.

2. **RTree KNN**:
   - **Segundo Mejor Tiempo de Ejecución**: `RTree KNN` también ofrece buenos tiempos de ejecución, aunque mayores que `HighD (knn_faiss)`. Para 16k datos, el tiempo de ejecución es 0.023975 segundos. Aun así, es una opción viable para escenarios que requieren tiempos de respuesta rápidos.

3. **Range KNN**:
   - **Tiempos de Ejecución Moderados**: `Range KNN` tiene tiempos de ejecución significativamente mayores que `HighD (knn_faiss)` y `RTree KNN`, pero sigue siendo más rápido que `Range KNN Priority Queue`. Por ejemplo, para 16k datos, el tiempo de ejecución varía entre 2.6441 y 2.6570 segundos dependiendo del radio, lo cual es mucho más lento que los dos anteriores.

4. **KNN Priority Queue**:
   - **El Peor Tiempo de Ejecución**: `Range KNN Priority Queue` tiene los tiempos de ejecución más altos, con un crecimiento exponencial a medida que aumenta el tamaño del conjunto de datos. Para 16k datos, el tiempo de ejecución es 49.965 segundos, lo que lo hace poco práctico para grandes volúmenes de datos.

#### Escalabilidad

1. **HighD (knn_faiss)**:
   - **Mejor Escalabilidad**: `HighD (knn_faiss)` muestra una escalabilidad superior, con tiempos de ejecución que aumentan de manera muy controlada a medida que crece el tamaño del conjunto de datos. Este algoritmo puede manejar grandes volúmenes de datos con un impacto mínimo en el tiempo de ejecución, haciéndolo adecuado para aplicaciones de alta demanda.

2. **RTree KNN**:
   - **Buena Escalabilidad**: `RTree KNN` también tiene una escalabilidad razonable, con tiempos de ejecución que crecen de manera más controlada que `Range KNN` y `Range KNN Priority Queue`. Aunque no es tan eficiente como `HighD (knn_faiss)`, sigue siendo una opción escalable para conjuntos de datos medianos a grandes.

3. **Range KNN**:
   - **Escalabilidad Moderada**: `Range KNN` muestra una escalabilidad deficiente en comparación con `HighD (knn_faiss)` y `RTree KNN`. Los tiempos de ejecución aumentan significativamente con el tamaño del conjunto de datos, lo que limita su utilidad para grandes volúmenes de datos. Por ejemplo, de 1k a 16k datos, el tiempo de ejecución pasa de 0.1739 a 2.6570 segundos.

4. **KNN Priority Queue**:
   - **Pobre Escalabilidad**: `Range KNN Priority Queue` tiene la peor escalabilidad entre los algoritmos comparados. El incremento en los tiempos de ejecución es exponencial a medida que aumenta el tamaño del conjunto de datos. Para aplicaciones con grandes volúmenes de datos, este algoritmo no es práctico debido a su tiempo de ejecución extremadamente alto.

### Conclusión

- **HighD (knn_faiss)** es claramente el algoritmo más eficiente y escalable, siendo ideal para aplicaciones que requieren tiempos de respuesta rápidos y pueden manejar grandes volúmenes de datos.
- **RTree KNN** es una buena alternativa con tiempos de ejecución razonables y buena escalabilidad, adecuado para aplicaciones que no requieren el rendimiento extremo de `HighD (knn_faiss)`.
- **Range KNN** ofrece tiempos de ejecución moderados y una escalabilidad limitada, siendo menos eficiente que `HighD (knn_faiss)` y `RTree KNN`.
- **Range KNN Priority Queue** es el menos eficiente y escalable, con tiempos de ejecución muy altos y pobre escalabilidad, haciendo que sea poco práctico para la mayoría de aplicaciones con grandes volúmenes de datos.
