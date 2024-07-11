import numpy as np
import heapq

#genere documentos con vectores de prueba
#       pruebita.txt tiene 4d
#       vectores.txt tiene 128d

def euclidean_distances(query, data):
    return np.sqrt(((data - query) ** 2).sum(axis=1))

def KNNPriorityQueue(query, K):
    data = np.loadtxt('pruebita.txt', delimiter=',')
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
            
    return [data[i] for _, i in sorted(pq, reverse=True)]

query = np.array([0.4576, 0.034567, 0.1234, 0.9876])

K = 5
result = KNNPriorityQueue(query, K)
print(result)

def rangeSearch(query, radius):
    data = np.loadtxt('pruebita.txt', delimiter=',')
    distances = euclidean_distances(query, data)
    result = []
    for i in range(len(data)):
        if distances[i] < radius:
            result.append(data[i])
    return result

radius = 0.15
result2 = rangeSearch(query, radius)
print(result2)