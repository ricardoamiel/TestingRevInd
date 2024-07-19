# Búsqueda y Recuperación de la Información Pt.2
## Construcción del Índice Multidimensional
#### Integrantes: Ricardo Acuña, Gonzalo Perea, Isabella Romero, Rodrigo Lauz y Josué Velo

## Introducción
### Objetivo del proyecto
El objetivo de este proyecto es desarrollar una herramienta efectiva que facilite la búsqueda y el reconocimiento de canciones a través de sus características principales. Inspirado en aplicaciones como Shazam, este proyecto se centra en la extracción de vectores característicos de cada canción en una base de datos, lo que permite realizar búsquedas eficientes y precisas basadas en distintas características y similitudes entre canciones. Esta herramienta está diseñada para mejorar la experiencia del usuario en la identificación y descubrimiento de música, proporcionando resultados rápidos y relevantes que se ajusten a sus preferencias y necesidades musicales.

### Descripción del dominio de datos y la importancia de aplicar indexación
Nuestra base de datos contiene aproximadamente 25,000 canciones de distintos géneros y estilos, procesadas para extraer vectores característicos que capturan sus atributos esenciales. La indexación multidimensional es crucial para realizar búsquedas rápidas y precisas, permitiendo identificar canciones similares de manera eficiente. Esto asegura que, incluso con una base de datos extensa, las búsquedas sean ágiles y relevantes, optimizando el uso de recursos del sistema y mejorando la experiencia del usuario en la identificación y descubrimiento de música.

## Backend: Índice Multidimensional
### Técnica de indexación de las librerías utilizadas

#### Faiss
**Faiss (Facebook AI Similarity Search)** es una biblioteca desarrollada por Facebook AI Research para realizar búsquedas de similitud y clustering en grandes conjuntos de datos de vectores. Utiliza una serie de técnicas de indexación, entre ellas:

- Índice de Archivo Invertido (IVF): Esta técnica acelera la búsqueda de similitudes dividiendo el conjunto de datos en múltiples clústeres o celdas. Cada celda corresponde a un clúster de vectores, y durante la consulta, solo se busca en un subconjunto de estas celdas, reduciendo así el número de comparaciones necesarias.

- Índice Multi-invertido: Es una extensión del índice de archivo invertido para búsquedas en espacios de alta dimensión. Utiliza una estructura de índice multinivel, particionando los datos a lo largo de varios niveles o dimensiones. Esto permite realizar búsquedas más granulares y eficientes en conjuntos de datos complejos y de alta dimensión.

- Cuantización de Productos (PQ - Product Quantization): Reduce la dimensión de los vectores descomponiéndolos en subvectores y cuantificándolos por separado. Esto mejora la rapidez de búsqueda y reduce el uso de memoria.

- Índice Distribuido: Faiss soporta índices distribuidos mediante una biblioteca RPC simple, que permite acceder a índices desde varias máquinas ("esclavos"). Cada esclavo contiene una parte del conjunto de datos (fragmento). Durante la búsqueda, el master emite la consulta a todos los esclavos, que procesan la consulta y envían los resultados de vuelta al maestro, que combina estos resultados en la salida final. Cabe destacar que el código de servidor y RPC proporcionado con Faiss es para fines de demostración y no incluye ciertas protecciones de seguridad, por lo que no está destinado a ejecutarse en redes no confiables o en entornos de producción.

### Como se realiza el KNN Search y el Range Search
- Búsqueda KNN con Cola de Prioridad: Se implementa un algoritmo K-Nearest Neighbors (KNN) que utiliza una cola de prioridad para encontrar los k vecinos más cercanos a un punto de consulta. Tras importar las librerías necesarias y cargar un archivo CSV en un DataFrame, se calcula la distancia euclidiana entre los puntos. La función mantiene los k vecinos más cercanos en la cola de prioridad y devuelve sus índices y distancias. Se evalúa el rendimiento del algoritmo con diferentes puntos de consulta y valores de k, midiendo el tiempo promedio de ejecución.
  
- Búsqueda de Rango: Se implementa una búsqueda de vecinos dentro de un rango específico usando características de canciones. Se importan las librerías necesarias, se carga un archivo CSV y se calculan distancias entre pares de canciones aleatorias. Se crea un histograma de distancias y se determinan radios de búsqueda mediante percentiles. La función rangeSearch busca canciones dentro de un radio alrededor de un punto de consulta. Se prueba la búsqueda para diferentes radios y se mide el tiempo promedio de ejecución.

### Análisis de la maldición de la dimensionalidad y como mitigarlo
- La maldición de la dimensionalidad afecta la eficacia de los algoritmos KNN al aumentar la dificultad de distinguir entre vecinos cercanos en espacios de alta dimensión. FAISS mitiga este problema mediante técnicas de indexación eficiente, como Product Quantization y HNSW, que optimizan la búsqueda en grandes conjuntos de datos de alta dimensión. En el proyecto, se utiliza un índice faiss.IndexFlatL2 para calcular distancias y realizar búsquedas, mostrando una reducción significativa en el tiempo de ejecución promedio al comparar con métodos no optimizados.

## Frontend
### Diseño de la GUI
#### Mini-manual de usuario
#### Screenshots de la GUI
### Análisis comparativo visual con otras implementaciones

## Experimentación
### Tabla de Resultados de los Algoritmo (KNN) 
| Tamaño de Datos | Range KNN Priority Queue | RTree KNN     | HighD (knn_faiss)|
|-----------------|--------------------------|---------------|-------------|
| 1k              | 3.280                    | 0.000416      | 0.000396    |
| 2k              | 6.102                    | 0.001113      | 0.000778    |
| 4k              | 12.977                   | 0.005534      | 0.001001    |
| 8k              | 25.527                   | 0.001432      | 0.002268    |
| 16k             | 49.965                   | 0.023975      | 0.004762    |

### Gráfica de Resultados de los Algoritmos (KNN) 
<img width="1040" alt="Screen Shot 2024-06-17 at 2 40 37 PM" src="https://github.com/ricardoamiel/TestingRevInd/blob/main/imgs/Algoritmos.png">

### Tabla de Resultados del Algoritmo Range KNN
| Tamaño de Datos | Radio 1 | Tiempo 1 | Radio 2 | Tiempo 2 | Radio 3 | Tiempo 3 |
|-----------------|---------|----------|---------|----------|---------|----------|
| 1k              | 58.15   | 0.1739   | 72.75   | 0.1724   | 86.82   | 0.1743   |
| 2k              | 60.40   | 0.3452   | 76.06   | 0.3395   | 91.70   | 0.3536   |
| 4k              | 63.43   | 0.6835   | 79.89   | 0.6995   | 96.14   | 0.6690   |
| 8k              | 63.87   | 1.3710   | 79.53   | 1.3429   | 94.80   | 1.3910   |
| 16k             | 62.46   | 2.6490   | 77.87   | 2.6441   | 92.01   | 2.6570   |

### Gráfica 
<img width="1040" alt="Screen Shot 2024-06-17 at 2 40 37 PM" src="https://github.com/ricardoamiel/TestingRevInd/blob/main/imgs/Range_KNN.png">

### Análisis y discusión
#### Resultados Generales de los Algoritmos KNN

Las tablas de resultados muestran el desempeño de tres algoritmos KNN (`Range KNN Priority Queue`, `RTree KNN`, y `HighD (knn_faiss)`) en función del tamaño de datos. Los tiempos de ejecución, medidos en segundos, proporcionan una visión clara de la eficiencia de cada algoritmo a medida que se incrementa el tamaño del conjunto de datos.

**1. Range KNN Priority Queue:**

- **Crecimiento del Tiempo de Ejecución:** Este algoritmo muestra un crecimiento exponencial en el tiempo de ejecución a medida que aumenta el tamaño de los datos. Para datos de tamaño 1k, el tiempo de ejecución es 3.280 segundos, mientras que para 16k, aumenta a 49.965 segundos. Esto indica que el algoritmo `Range KNN Priority Queue` es menos eficiente para conjuntos de datos grandes debido a la complejidad del proceso de búsqueda y el manejo de prioridades en la cola.
  
- **Escalabilidad:** La escalabilidad del `Range KNN Priority Queue` es limitada. A medida que el tamaño de los datos aumenta, el tiempo de ejecución crece significativamente, lo que sugiere que el algoritmo podría no ser la mejor opción para aplicaciones con grandes volúmenes de datos.

**2. RTree KNN:**

- **Tiempo de Ejecución Consistente:** A diferencia del `Range KNN Priority Queue`, el `RTree KNN` muestra tiempos de ejecución relativamente constantes, con un aumento leve al pasar de 1k a 16k datos. El tiempo para 1k es 0.000416 segundos, mientras que para 16k es 0.023975 segundos. Este comportamiento sugiere que el algoritmo `RTree KNN` maneja de manera más eficiente el incremento en el tamaño de los datos.
  
- **Eficiencia:** `RTree KNN` es considerablemente más eficiente que `Range KNN Priority Queue` en todos los tamaños de datos. Su rendimiento más estable con tamaños grandes de datos lo convierte en una opción más adecuada para aplicaciones con grandes conjuntos de datos.

**3. HighD (knn_faiss):**

- **Desempeño Superior:** El algoritmo `HighD (knn_faiss)` también muestra tiempos de ejecución significativamente menores en comparación con `Range KNN Priority Queue`, aunque algo mayores que `RTree KNN`. El tiempo para 1k es 0.000396 segundos y para 16k es 0.004762 segundos. Este algoritmo combina eficiencia con una buena capacidad para manejar conjuntos de datos grandes.
  
- **Escalabilidad:** `HighD (knn_faiss)` tiene una buena escalabilidad y rendimiento relativamente constante, lo que sugiere que es una opción sólida para aplicaciones que requieren tanto eficiencia como capacidad para manejar grandes volúmenes de datos.

#### Resultados del Algoritmo Range KNN

La segunda tabla muestra los tiempos de ejecución del algoritmo `Range KNN` para diferentes radios. La tendencia general indica que el tiempo de ejecución aumenta con el tamaño del conjunto de datos, y varía ligeramente con el cambio en el radio.

- **Impacto del Radio:** Para cada tamaño de datos, los tiempos de ejecución muestran variaciones menores entre los diferentes radios, pero en general, tiempos más largos se observan con radios más grandes. Esto sugiere que, a medida que el radio aumenta, el algoritmo `Range KNN` debe procesar más datos para cada consulta, lo que incrementa el tiempo total de ejecución.

- **Tamaño de Datos:** La tendencia de los tiempos de ejecución es coherente con el aumento del tamaño de los datos. Con tamaños más grandes, incluso pequeños cambios en el radio tienen un impacto más notable en el tiempo de ejecución debido al mayor volumen de datos que se deben considerar en las consultas.

### Conclusión

- **`Range KNN Priority Queue`** es menos eficiente a medida que aumenta el tamaño de los datos y muestra una escalabilidad deficiente. No es recomendable para conjuntos de datos grandes.

- **`RTree KNN`** ofrece un rendimiento más constante y es mucho más eficiente que `Range KNN Priority Queue`. Es una opción viable para grandes conjuntos de datos.

- **`HighD (knn_faiss)`** combina eficiencia y buen manejo de grandes conjuntos de datos, siendo una opción robusta para aplicaciones que requieren manejo de grandes volúmenes de datos con buenos tiempos de respuesta.

- **El impacto del radio** en el tiempo de ejecución de `Range KNN` es notable, pero en general, el tamaño del conjunto de datos tiene un impacto mayor en el tiempo de ejecución que el cambio en el radio. Ajustar el radio puede ayudar a optimizar el rendimiento en casos específicos, pero el tamaño del conjunto de datos sigue siendo un factor clave en el rendimiento general.
