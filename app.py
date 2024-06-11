from flask import Flask, request, jsonify, render_template
import ProyectoBD2enPython as PBD

# Inicializar la aplicación Flask
app = Flask(__name__)

# Cargar el índice invertido y calcular normas
index = PBD.index
norms = PBD.calculate_norms(index)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    k = int(request.args.get('k'))
    results = PBD.cosine_similarity(query, index, norms, k)
    return jsonify([{'doc_id': doc_id, 'score': score} for doc_id, score in results])

@app.route('/document', methods=['GET'])
def get_document():
    doc_id = int(request.args.get('doc_id'))
    return PBD.librillos_sin_procesar[doc_id]

if __name__ == '__main__':
    app.run(debug=True)