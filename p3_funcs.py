import librosa
import os
import numpy as np
import heapq
import time
import concurrent.futures
import rtree
import faiss

# Funciones de extraccion de caracteristicas
def features_extraction(file_path, dimensions):
    #load the audio file
    x, sample_rate = librosa.load(file_path, res_type='kaiser_fast')
    #extract features from the audio file
    mfcc = np.mean(librosa.feature.mfcc(y=x, sr=sample_rate, n_mfcc=dimensions),axis=1) # axis = 1
    
    return mfcc

# Funciones de KNN Range priority queue
def euclidean_distances(query, data):
    return np.sqrt(((data - query) ** 2).sum(axis=1))

def KNNPriorityQueue(query, K, chars):
    data = np.loadtxt(chars, delimiter=',')
    
    if len(data) < K:
        raise ValueError("El número de datos es menor que K")
    
    distances = euclidean_distances(query, data)
    pq = []
    
    # Insertamos los primeros K elementos de la base de datos en la cola de prioridad
    for i in range(K):
        heapq.heappush(pq, (-distances[i], i))  # Distancia negativa para simular una cola de prioridad máxima

    for i in range(K, len(data)):
        # Si la distancia entre el objeto de consulta y el objeto i es menor que la mayor distancia en la cola de prioridad
        if -pq[0][0] > distances[i]: # Eliminamos el objeto en la cola de prioridad con mayor distancia
            heapq.heappop(pq)
            heapq.heappush(pq, (-distances[i], i))
            
    return [(data[i], -distance) for distance, i in sorted(pq, reverse=True)]

def knnSearch(collection, query, k):
    heap = [] # heap vacio
    ED = lambda P, Q: np.sqrt((P-Q)**2)

    for i in range(len(collection)):
        dist = np.sqrt((ED(collection[i], query) ** 2).sum()) # porque es una serie de pandas y no un array de numpy
        # Use negative distance because heapq is a min heap
        if len(heap) < k:
            heapq.heappush(heap, (-dist, i)) # si no se ha llenado el heap, se inserta
        else:
            heapq.heappushpop(heap, (-dist, i)) # si ya se lleno el heap, se inserta y se elimina el menor

    # Return indices and distances, reversing the order so that the closest is first
    indices_and_distances = [(i, -d) for d, i in sorted(heap, reverse=True)]
    return indices_and_distances
 
# Funciones para KNN Range radio
def genDistancias(data, N):
    ED = lambda P, Q: np.sqrt(sum((P-Q)**2))
    v = np.zeros(N)
    for i in range(N):
        ind = np.random.choice(data.shape[0], size=2, replace=False)
        P = data[ind[0], :]
        Q = data[ind[1], :]
        #v[i] = distance.euclidean(P, Q)
        v[i] = np.sqrt((ED(P, Q) ** 2).sum())
    return v

def rangeSearch(collection, query, r, query_index):
    ED = lambda P, Q: np.sqrt(sum((P-Q)**2))
    result = []
    heap = []
    for i in range(len(collection)):
        dist = np.sqrt((ED(collection[i], query) ** 2).sum())
        if (dist < r).all():  # Check if all elements in the Series are less than r
            result.append(i)
            #sort by distance to r
            heapq.heappush(heap, (dist, i))
    sorted_result = [index for _, index in heapq.nsmallest(len(heap), heap)]
    return sorted_result # result

# Funciones para KNN Rtree
def knn_rtree(collection, query, k, dimensions):
    # Create a new RTree index
    prop = rtree.index.Property()
    prop.dimension = dimensions   # dimension del vector caracteristico
    #prop.buffering_capacity = 8    # Cantidad maxima de MBRs en un nodo 
    ind = rtree.index.Index(properties = prop)

    # insertar los puntos                
    for i in range(collection.shape[0]):
        ind.insert(i, collection[i].tolist() + collection[i].tolist())     

    start_time = time.time()
    ind.nearest(query, num_results=k) # cambiar a k+1 porque se cuenta a si mismo
    end_time = time.time() - start_time

    # Obtener los k vecinos más cercanos (k+1 para excluir el punto de consulta si está presente)
    k_nearest = list(ind.nearest(query.tolist() + query.tolist(), num_results=k))
    ind.close()

    # Calcular distancias y ordenar
    distances = []
    for idx in k_nearest:
        dist = np.linalg.norm(collection[idx] - query)
        distances.append((dist, idx))
            
    distances.sort(key=lambda x: x[0])  # Ordenar por distancia
    
    # Extraer índices ordenados
    sorted_indices = [idx for _, idx in distances]
    
    return sorted_indices, distances, end_time


# Funciones para HighD
def knn_faiss(data, query, k):
    d = len(data[0])  # Dimensionality of the feature vectors
    start_time = time.time()  # Inicio del temporizador
    index = faiss.IndexFlatL2(d)  # L2 distance
    index.add(np.array(data, dtype='float32'))  # Add data to the index
    D, I = index.search(np.array([query], dtype='float32'), k)  # Perform the search k+1 para no contar la query
    end_time = time.time()  # Fin del temporizador
    total_time = end_time - start_time  # Acumular el tiempo de ejecución
    return I[0], D[0], total_time