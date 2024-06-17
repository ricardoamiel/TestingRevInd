# Búsqueda y Recuperación de la Información 
#### Integrantes: Ricardo Acuña, Gonzalo Perea, Isabella Romero y Rodrigo Lauz

## Introducción
### Objetivo del proyecto
Este proyecto fue desarrollado con el fin de facilitar la búsqueda de canciones a través de palabras específicas, como por ejemplo las top 10 canciones más relacionadas al amor o tristeza. Esto simpilifica y devuelve los resultados más acorde a lo que buscamos en un tiempo mínimo.

### Descripción del dominio de datos y la importancia de aplicar indexación
La base de datos contiene más de 17 mil registros de canciones con especificaciones como: nombre, artista, letra de la canción, popularidad, nombre del album, fecha de lanzamiento, género, instrumentos, etc. De las cuales, estamos usando principalmente las columnas del artista, nombre y letra de la canción para poder ingresar un conjunto de palabras y que devuelva las top k canciones que se relacionan más a las palabras ingresadas.
Es importante utilizar índices, ya que minimiza el tiempo de búsqueda de similitud en cantidades masivas de registros como en este caso. En lugar de iterar uno por uno, se genera una lista de palabras clave que estan relacionadas con cierto puntaje a cada canción. Luego este proceso será explicado más a fondo.

## Backend: Índice Invertido
### Construcción del índice invertido en memoria secundaria
Para construir un índice invertido en memoria secundaria, hemos utilizado una lógica basada en el tamaño de los bloques. Asumiendo un tamaño de bloque de 4096 bytes y considerando que para cada término guardamos su doc_id y su valor de tf-idf, estamos almacenando 8 bytes por registro (4 bytes para doc_id y 4 bytes para tf-idf). Esto permite almacenar hasta 4096 registros por bloque, con un total de 32,768 bytes por bloque. Si limitamos la construcción del índice invertido a usar 1MB de RAM, podemos calcular el número de índices invertidos locales como \( \frac{1024 \times 1024}{4096 \times 8} \), lo que da aproximadamente 32 índices invertidos locales. Sin embargo, en la práctica, los registros pueden ocupar más espacio. Por ejemplo, si cada término aparece en 4 documentos y almacenamos 4 valores de tf-idf por término, el tamaño por registro sería 32 bytes (4 doc_ids y 4 tf-idf). Si limitamos la RAM a 4MB, el cálculo sería \( \frac{4 \times 1024 \times 1024}{4096 \times 32} \), lo que también da aproximadamente 32 índices invertidos locales. Esto implica que un término puede aparecer en más de un índice invertido si alcanza el límite de tamaño del bloque.

### Ejecución óptima de consultas aplicando Similitud de Coseno


### Construcción del índice invertido en PostgreSQL
En PostgreSQL, la técnica para aplicar el índice invertido se denomina GIN (Generalized Inverted Index). GIN está diseñado para trabajar con valores compuestos, permitiendo la combinación de múltiples celdas en un solo índice. 
En este caso, los elementos del índice son archivos y las consultas son palabras o términos que queremos buscar en estos archivos específicos. El índice GIN almacena pares de clave (key) y postings lists, donde cada una es un conjunto de identificadores de filas (row IDs) correspondientes a los documentos en los que aparece la clave.

La estructura interna del índice GIN en PostgreSQL es un B-tree para almacenar claves (keys) y sus posting lists, lo que permite búsquedas eficientes en documentos textuales.
<img width="1040" alt="Screen Shot 2024-06-17 at 2 40 37 PM" src="https://github.com/ricardoamiel/TestingRevInd/assets/102993411/bad1dd0a-4751-4c00-9a66-12d6c9e2813c">
Cada clave se almacena solo una vez, haciendo el índice compacto. Los índices GIN multicolumna combinan valores de diferentes columnas en un solo B-tree. Esta estructura soporta consultas complejas y permite el desarrollo de tipos de datos personalizados, mejorando la eficiencia y rapidez de las búsquedas de texto completo.

Cuando se realiza una consulta que contiene múltiples términos (usando AND), PostgreSQL busca los documentos que contienen todos los términos especificados. Esto se hace combinando las listas de postings de cada término.

## Frontend
Screenshots de la GUI

## Experimentación
Tablas y gráficos de los resultados experimentales
Análisis y discusión

Debe incluir imágenes o diagramas para una mejor comprensión.
