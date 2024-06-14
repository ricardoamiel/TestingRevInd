from flask import Flask, request, jsonify, render_template
import ProyectoBD2enPython as PBD
import time

# Inicializar la aplicación Flask
app = Flask(__name__)

# Cargar el índice invertido y calcular normas
index = PBD.index
norms = PBD.calculate_norms(index)
docs = PBD.documentos_sin_procesar

@app.route('/')
def home():
    return render_template('index.html')

# muestra el contenido de un top k documento
@app.route('/document', methods=['GET'])
def get_document():
    doc_id = request.args.get('doc_id', type=int)
    return docs[doc_id]

# llama los top k documentos con sus scores
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    #k = int(request.args.get('k'))
    k = request.args.get('k', type=int)
    start_time = time.time()
    results = PBD.cosine_similarity(query, index, norms, k)
    duracion = time.time() - start_time
    response = {
        'results': [{'doc_id': doc_id, 'document': docs[doc_id], 'score': score} for doc_id, score in results],
        'time': duracion
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)