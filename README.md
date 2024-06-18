# Búsqueda y Recuperación de la Información 
#### Integrantes: Ricardo Acuña, Gonzalo Perea, Isabella Romero, Rodrigo Lauz y Josué Velo

## Introducción
### Objetivo del proyecto
Este proyecto fue desarrollado con el fin de facilitar la búsqueda de canciones a través de palabras específicas, como por ejemplo las top 10 canciones más relacionadas al amor o tristeza. Esto simpilifica y devuelve los resultados más acorde a lo que buscamos en un tiempo mínimo.

### Descripción del dominio de datos y la importancia de aplicar indexación
La base de datos contiene más de 17 mil registros de canciones con especificaciones como: nombre, artista, letra de la canción, popularidad, nombre del album, fecha de lanzamiento, género, instrumentos, etc. De las cuales, estamos usando principalmente las columnas del artista, nombre y letra de la canción para poder ingresar un conjunto de palabras y que devuelva las top k canciones que se relacionan más a las palabras ingresadas.
Es importante utilizar índices, ya que minimiza el tiempo de búsqueda de similitud en cantidades masivas de registros como en este caso. En lugar de iterar uno por uno, se genera una lista de palabras clave que estan relacionadas con cierto puntaje a cada canción. Luego este proceso será explicado más a fondo.

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
    with open("final_index.txt", "w", encoding='utf-8') as f:
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
  with open("final_index.txt", "w", encoding='utf-8') as f:
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

## Frontend
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

El experimento fue corrido en datagrip, simplemente se carga el csv en una tabla con el mismo nombre (spotify_songs) y se corre el código de experimento.

Primero juntamos en una sola columna el nombre de la canción, el artista, el álbum y la letra de esta misma, nos servirá para poder mostrar la tabla proporcionada por postgres en el frontend. Además de ello, se crean los índices respectivos, con ello listo, podemos correr el experimento

```sql
-- merge columnas nombre cancion, nombre artista, nombre album, y letra cancion
ALTER TABLE spotify_songs
ADD COLUMN listo_index text;
UPDATE spotify_songs
SET listo_index = CONCAT_WS(' ', track_name, track_artist, track_album_name, lyrics);

-- Crear un índice GIN en la columna listo_index
CREATE INDEX idx_listo_index_spanish_gin
    ON spotify_songs USING gin(to_tsvector('spanish', listo_index))
    WHERE language = 'es';

-- Crear un índice GIN en la columna listo_index
CREATE INDEX idx_listo_index_english_gin
    ON spotify_songs USING gin(to_tsvector('english', listo_index))
    WHERE language = 'en';
```

#### Ejecución del código

Debemos tener en cuenta el `schema` y la `contraseña` de nuestra cuenta de postgreSQL, con la tabla y los índices creados, solo ejecutando `app.py` podrás escribir consultas en lenguaje natural en nuestra GUI, y ver las diferencias entre nuestro índice invertido y el índice GiN de PostgreSQL.

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
