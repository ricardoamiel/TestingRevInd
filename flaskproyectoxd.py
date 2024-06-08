from flask import Flask, request, jsonify
from collections import defaultdict, deque
import ProyectoBD2enPython as PBD
app = Flask(__name__)

# Cargar el índice invertido
index = defaultdict(list)
with open("final_index.txt", "r") as f:
    for line in f:
        term, postings = line.strip().split(' ', 1)
        postings_list = list(map(int, postings.split()))
        index[term] = postings_list

def search(query, index, k):
    query_tokens = PBD.preprocesamiento(query).split()
    scores = defaultdict(float)
    for token in query_tokens:
        if token in index:
            for doc_id in index[token]:
                scores[doc_id] += 1
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]

@app.route('/search', methods=['GET'])
def search_endpoint():
    query = request.args.get('query')
    k = int(request.args.get('k'))
    results = search(query, index, k)
    return jsonify([{'doc_id': doc_id, 'score': score} for doc_id, score in results])

if __name__ == '__main__':
    app.run(debug=True)
