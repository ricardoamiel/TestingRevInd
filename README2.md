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

## Análisis y discusión
#### Tiempo de Ejecución

1. **HighD (knn_faiss)**:
   - **Mejor Tiempo de Ejecución**: `HighD (knn_faiss)` muestra el menor tiempo de ejecución en todos los tamaños de datos. En el caso de 16k, el tiempo de ejecución es 0.004762 segundos, que es significativamente más bajo que los otros algoritmos.
   
2. **RTree KNN**:
   - **Segundo Mejor Tiempo de Ejecución**: `RTree KNN` también ofrece buenos tiempos de ejecución, aunque mayores que `HighD (knn_faiss)`. Para 16k, el tiempo es 0.023975 segundos.
   
3. **Range KNN**:
   - **Tiempos de Ejecución Altos**: `Range KNN` muestra tiempos de ejecución mucho mayores que `RTree KNN` y `HighD (knn_faiss)`, creciendo de manera exponencial con el tamaño del conjunto de datos. Por ejemplo, para 16k, el tiempo es 49.965 segundos.
   
4. **Range KNN Priority Queue**:
   - **El Peor Tiempo de Ejecución**: `Range KNN Priority Queue` tiene los tiempos de ejecución más altos, con un crecimiento exponencial aún más pronunciado a medida que aumenta el tamaño del conjunto de datos.

#### Escalabilidad

1. **HighD (knn_faiss)**:
   - **Mejor Escalabilidad**: `HighD (knn_faiss)` muestra una escalabilidad superior, con tiempos de ejecución que aumentan de manera más controlada en comparación con los otros algoritmos. Es capaz de manejar grandes volúmenes de datos con un impacto mínimo en el tiempo de ejecución.
   
2. **RTree KNN**:
   - **Buena Escalabilidad**: `RTree KNN` tiene una escalabilidad relativamente buena, con tiempos de ejecución que crecen de manera más controlada que `Range KNN` y `Range KNN Priority Queue`. Sin embargo, no es tan eficiente como `HighD (knn_faiss)` en conjuntos de datos grandes.
   
3. **Range KNN**:
   - **Escalabilidad Limitada**: `Range KNN` muestra una escalabilidad deficiente, con tiempos de ejecución que crecen exponencialmente a medida que aumenta el tamaño del conjunto de datos, lo que lo hace menos adecuado para grandes volúmenes de datos.
   
4. **Range KNN Priority Queue**:
   - **Escalabilidad Muy Limitada**: `Range KNN Priority Queue` tiene la peor escalabilidad, con un incremento muy alto en los tiempos de ejecución a medida que aumenta el tamaño del conjunto de datos.

#### Flexibilidad

1. **Range KNN Priority Queue**:
   - **Más Flexible en Parámetros**: Permite ajustar el tamaño de la cola de prioridad, lo que puede ser útil para optimizar ciertos casos de uso. Sin embargo, su flexibilidad viene a costa de un alto tiempo de ejecución.
   
2. **Range KNN**:
   - **Moderada Flexibilidad**: Ofrece flexibilidad a través de ajustes del radio, pero el impacto en el tiempo de ejecución no es suficiente para superar a los métodos más eficientes. Aún así, permite cierta adaptación a diferentes configuraciones de parámetros.
   
3. **RTree KNN**:
   - **Menos Flexible**: Menos flexible en comparación con `Range KNN`, pero ofrece una buena combinación de eficiencia y facilidad de uso. Es más adecuado para aplicaciones con requisitos de tiempo de ejecución más estrictos.
   
4. **HighD (knn_faiss)**:
   - **Menos Necesidad de Flexibilidad**: Aunque no proporciona tanta flexibilidad en términos de ajustes de parámetros, la eficiencia de `HighD (knn_faiss)` reduce la necesidad de ajustes, ya que maneja grandes volúmenes de datos de manera eficaz con tiempos de ejecución mínimos.

### Conclusión

- **HighD (knn_faiss)** es el algoritmo más eficiente y escalable, con el mejor rendimiento en términos de tiempo de ejecución y capacidad para manejar grandes volúmenes de datos.
- **RTree KNN** ofrece un buen equilibrio entre tiempo de ejecución y escalabilidad, aunque no alcanza la eficiencia de `HighD (knn_faiss)`.
- **Range KNN** y **Range KNN Priority Queue** tienen tiempos de ejecución significativamente mayores y muestran una escalabilidad deficiente, con `Range KNN Priority Queue` siendo el menos eficiente en términos de tiempo de ejecución.
- La flexibilidad de `Range KNN Priority Queue` y `Range KNN` puede ser útil para ciertos ajustes, pero la eficiencia de `HighD (knn_faiss)` y la escalabilidad de `RTree KNN` lo convierten en la mejor opción para aplicaciones que requieren un alto rendimiento.

