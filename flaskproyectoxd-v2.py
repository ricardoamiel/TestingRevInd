from flask import Flask, request, jsonify
from collections import defaultdict, deque
import ProyectoBD2enPython as PBD
import math
app = Flask(__name__)

def cosine_similarity(query_vector, doc_vector, doc_norm):
    dot_product = sum(query_vector[token] * doc_vector[token] for token in query_vector if token in doc_vector)
    query_norm = math.sqrt(sum(weight ** 2 for weight in query_vector.values()))
    return dot_product / (query_norm * doc_norm)

def search(query, index, norms, k):
    query_tokens = PBD.preprocesamiento(query).split()
    query_tf = defaultdict(int)
    for token in query_tokens:
        query_tf[token] += 1
    query_vector = {token: 1 + math.log10(tf) for token, tf in query_tf.items() if token in index}
    
    scores = defaultdict(float)
    for token, weight in query_vector.items():
        if token in index:
            for doc_id, tfidf in index[token].items():
                scores[doc_id] += weight * tfidf
    
    for doc_id in scores:
        scores[doc_id] /= norms[doc_id]
    
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]

@app.route('/search', methods=['GET'])
def search_endpoint():
    query = request.args.get('query')
    k = int(request.args.get('k'))
    results = search(query, index, norms, k)
    return jsonify([{'doc_id': doc_id, 'score': score} for doc_id, score in results])

if __name__ == '__main__':
    app.run(debug=True)
