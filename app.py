from flask import Flask, request, jsonify, render_template
import psycopg2
import time
import TableCreation

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

import ProyectoBD2enPython as PBD

# Inicializar la aplicación Flask
app = Flask(__name__)

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

if __name__ == '__main__':
    app.run()
