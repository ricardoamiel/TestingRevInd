import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, text, inspect
from sqlalchemy.schema import CreateSchema
import os
def create_table(user, password, database):

    csv_file_path = os.getcwd() + "\BD2\spotify_songs_pj.csv"

    df = pd.read_csv(csv_file_path)
    # Conectar a la base de datos
    engine = create_engine(f'postgresql://{user}:{password}@localhost:5432/{database}')
    conn = engine.connect()

    # Crear esquema si no existe

    inspector = inspect(engine)
    schemas = inspector.get_schema_names()
    if 'db2' not in schemas:
        conn.execute(text("create schema db2;"))
        conn.commit()

    # Crear tabla

    metadata = MetaData()

    spotify_songs = Table(
        'spotify_songs', metadata,
        Column('track_name', String),
        Column('track_artist', String),
        Column('track_album_name', String),
        Column('lyrics', String),
        Column('language', String),
        Column('track_ID', Integer, primary_key=True),
        schema='db2'
        )

    metadata.create_all(engine)

    # Insertar datos en la tabla
    df.to_sql('spotify_songs', engine, if_exists='replace', schema='db2', index=False)

    conn.execute(text("ALTER TABLE db2.spotify_songs ADD COLUMN listo_index text;"))
    conn.execute(text("UPDATE db2.spotify_songs SET listo_index = CONCAT_WS(' ', track_name, track_artist, track_album_name, lyrics);"))

    # Creacion de indices

    conn.execute(text("CREATE INDEX idx_listo_index_spanish_gin ON db2.spotify_songs USING gin(to_tsvector('spanish', listo_index)) WHERE language = 'es';"))
    conn.execute(text("CREATE INDEX idx_listo_index_english_gin ON db2.spotify_songs USING gin(to_tsvector('english', listo_index))WHERE language = 'en';"))

    conn.commit()