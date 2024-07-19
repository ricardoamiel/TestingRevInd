from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import psycopg2
import time
import TableCreation
import ProyectoBD2enPython as PBD
import p3_funcs as p3
import pandas as pd
import os
from werkzeug.utils import secure_filename
import rtree
import numpy as np

# AuxFuncs
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp3'}

def accepted(file):
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return ''
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join('/uplads', filename)
        file.save(filepath)
    return filepath

# Inputs
db_name = input("database[postgres]: ")  or 'postgres'
db_user = input('user[postgres]: ') or 'postgres'
db_password = input("password: ")

# Crear tabla en PostgreSQL
temp = ''

while temp != 'y' and temp != 'n':
    temp = input("¿Desea crear la tabla en PostgreSQL? [y/n]: ")
    
if temp == 'y':
    TableCreation.create_table(db_user, db_password, db_name)


# Inicializar la aplicación Flask
app = Flask(__name__)
CORS(app)

# Cargar el índice invertido y calcular normas
index = PBD.index
norms = PBD.calculate_norms(index)
docs = PBD.documentos_sin_procesar
track_info = PBD.track_info

# Conectar a PostgreSQL
conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host="localhost",
    port="5432"
)

my_table = 'db2.spotify_songs'

@app.route('/')
def home():
    return render_template('index.html')

# muestra el contenido de un top k documento
@app.route('/document', methods=['GET'])
def get_document():
    doc_id = request.args.get('doc_id', type=int)
    return {
        'lyrics': docs[doc_id],
        'track_name': track_info[doc_id]['track_name'],
        'track_artist': track_info[doc_id]['track_artist']
    }

# llama los top k documentos con sus scores
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    k = request.args.get('k', type=int)
    language = request.args.get('language')
    start_time = time.time()
    results = PBD.cosine_similarity(query, index, norms, k, language)
    duracion = time.time() - start_time
    response = { # puede haber error 
        'results': [{'doc_id': doc_id, 'score': score} for doc_id, score in results],
        'time': duracion
    }
    return jsonify(response)

# llama los top k documentos con sus scores desde PostgreSQL
@app.route('/search_postgresql', methods=['GET'])
def search_postgresql():
    query = request.args.get('query')
    k = request.args.get('k', type=int)
    language = request.args.get('language')
    
    ### convertir query separado por espacios en query separado por &
    ### ejemplo query = 'Feel Love' => query = 'Feel & Love'
    query = ' & '.join(query.split())

    if language == 'en':
        ts_query = f"to_tsquery('english', '{query}')"
    else:
        ts_query = f"to_tsquery('spanish', '{query}')"
        
    
    # transformar language == en => english o es => spanish
    if language == 'en':
        language = 'english'
    else:
        language = 'spanish'
    
    sql = f"""
        SELECT track_name, track_artist, track_album_name, listo_index,
               ts_rank(to_tsvector('{language}', listo_index), {ts_query}) AS rank
        FROM {my_table}
        WHERE to_tsvector('{language}', listo_index) @@ {ts_query}
        ORDER BY rank DESC
        LIMIT {k};
    """

    start_time = time.time()
    with conn.cursor() as cur:
        cur.execute(sql)
        results = cur.fetchall()
    duracion = time.time() - start_time

    response = {
        'results': [{'track_name': row[0], 'track_artist': row[1], 'track_album_name': row[2], 'lyrics': row[3], 'score': row[4]} for row in results],
        'time': duracion
    }
    return jsonify(response)

@app.route('/knn_pq', methods=['PUT'])
def knn_pq():
    # Check if the request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    filepath = accepted(file)
    if filepath == '':
        return jsonify({'error': 'No selected file'}), 400
    else:
        # Procesar la consulta
        datatrain = pd.read_csv('songs/features.csv')
        datatrain_ = datatrain.iloc[:,1:].values
    
        query = p3.features_extraction(filepath)
        k = request.args.get('k', type=int)
    
        start_time = time.time()
        result = p3.knnSearch(datatrain_, query, k)
        end_time = time.time() - start_time
        
        for i in range(len(result)):
            result[i] = datatrain.iloc[result[i],0]
        
        jj = []
        for i in result:
            jj.append({'id': i[0], 'score': i[1]})
        
        response = {
            'results': jj,
            'time': end_time
        }

@app.route('/knn_rtree', methods=['PUT'])
def knn_rtree():
    # Check if the request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    filepath = accepted(file)
    if filepath == '':
        return jsonify({'error': 'No selected file'}), 400
    else:
        # Procesar la consulta
        datatrain = pd.read_csv('songs/features.csv')
        datatrain_ = datatrain.iloc[:,1:].values
    
        query = p3.features_extraction(filepath)
        k = request.args.get('k', type=int)

        indexes, scores, time_ = p3.knn_rtree(datatrain_, query, k, 32)
        
        response = {
            'results': [{'id': indexes[i], 'score': scores[i]} for i in range(indexes)],
            'time': time_
        }
        
        return jsonify(response)
    
@app.route('/high_d', methods=['PUT'])
def high_d():
    # Check if the request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    filepath = accepted(file)
    if filepath == '':
        return jsonify({'error': 'No selected file'}), 400
    else:
        # Procesar la consulta
        datatrain = pd.read_csv('songs/features.csv')
        datatrain_ = datatrain.iloc[:,1:].values
    
        query = p3.features_extraction(filepath)
        k = request.args.get('k', type=int)
        
        indexes, scores, time_ = p3.knn_faiss(datatrain_, query, k)
        
        response = {
            'results': [{'id': indexes[i], 'score': scores[i]} for i in range(indexes)],
            'time': time_
        }
        
        return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
