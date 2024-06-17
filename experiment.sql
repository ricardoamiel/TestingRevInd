-- SCRIPT DE DATAGRIP (PSQL)

-- merge columnas nombre cancion, nombre artista, nombre album, y letra cancion
ALTER TABLE spotify_songs
ADD COLUMN listo_index text;
UPDATE spotify_songs
SET listo_index = CONCAT_WS(' ', track_name, track_artist, track_album_name, lyrics);

-- Crear un índice GIN en la columna listo_index
CREATE INDEX idx_listo_index_spanish_gin
    ON spotify_songs USING gin(to_tsvector('spanish', listo_index))
    WHERE language = 'es';

-- Crear un índice GIN en la columna listo_index
CREATE INDEX idx_listo_index_english_gin
    ON spotify_songs USING gin(to_tsvector('english', listo_index))
    WHERE language = 'en';

-- i want to duplicate my database but only with 1000 records
CREATE TABLE spotify_songs_1000 AS
SELECT *
FROM spotify_songs
LIMIT 1000;


explain analyse SELECT track_name, track_artist, track_album_name, listo_index,
       ts_rank(to_tsvector('english', listo_index), to_tsquery('english', 'Feel & Love')) AS rank
FROM spotify_songs
WHERE to_tsvector('english', listo_index) @@ to_tsquery('english', 'Feel & Love')
ORDER BY rank DESC
LIMIT 5;

-- Crear un índice GIN en la columna listo_index para la tabla spotify_songs_1000
CREATE INDEX idx_listo_index_english_gin_1000
    ON spotify_songs_1000 USING gin(to_tsvector('english', listo_index));

-- Crear un índice GIN en la columna listo_index para la tabla spotify_songs_1000
CREATE INDEX idx_listo_index_spanish_gin_1000
    ON spotify_songs_1000 USING gin(to_tsvector('spanish', listo_index));

-- hacer un explain analyse de la query anterior
explain analyse SELECT track_name, track_artist, track_album_name, listo_index,
       ts_rank(to_tsvector('english', listo_index), to_tsquery('english', 'Feel & Love')) AS rank
FROM spotify_songs_1000
WHERE to_tsvector('english', listo_index) @@ to_tsquery('english', 'Feel & Love')
ORDER BY rank DESC
LIMIT 5;

CREATE TABLE spotify_songs_2000 AS
SELECT *
FROM spotify_songs
LIMIT 2000;

-- Crear un índice GIN en la columna listo_index para la tabla spotify_songs_1000
CREATE INDEX idx_listo_index_english_gin_2000
    ON spotify_songs_2000 USING gin(to_tsvector('english', listo_index));

-- Crear un índice GIN en la columna listo_index para la tabla spotify_songs_1000
CREATE INDEX idx_listo_index_spanish_gin_2000
    ON spotify_songs_2000 USING gin(to_tsvector('spanish', listo_index));

-- hacer un explain analyse de la query anterior
explain analyse SELECT track_name, track_artist, track_album_name, listo_index,
                       ts_rank(to_tsvector('english', listo_index), to_tsquery('english', 'Feel & Love')) AS rank
                FROM spotify_songs_2000
                WHERE to_tsvector('english', listo_index) @@ to_tsquery('english', 'Feel & Love')
                ORDER BY rank DESC
                LIMIT 5;

CREATE TABLE spotify_songs_4000 AS
SELECT *
FROM spotify_songs
LIMIT 4000;

-- Crear un índice GIN en la columna listo_index para la tabla spotify_songs_1000
CREATE INDEX idx_listo_index_english_gin_4000
    ON spotify_songs_4000 USING gin(to_tsvector('english', listo_index));

-- Crear un índice GIN en la columna listo_index para la tabla spotify_songs_1000
CREATE INDEX idx_listo_index_spanish_gin_4000
    ON spotify_songs_4000 USING gin(to_tsvector('spanish', listo_index));

-- hacer un explain analyse de la query anterior
explain analyse SELECT track_name, track_artist, track_album_name, listo_index,
                       ts_rank(to_tsvector('english', listo_index), to_tsquery('english', 'Feel & Love')) AS rank
                FROM spotify_songs_4000
                WHERE to_tsvector('english', listo_index) @@ to_tsquery('english', 'Feel & Love')
                ORDER BY rank DESC
                LIMIT 5;

CREATE TABLE spotify_songs_8000 AS
SELECT *
FROM spotify_songs
LIMIT 8000;

-- Crear un índice GIN en la columna listo_index para la tabla spotify_songs_1000
CREATE INDEX idx_listo_index_english_gin_8000
    ON spotify_songs_8000 USING gin(to_tsvector('english', listo_index));

-- Crear un índice GIN en la columna listo_index para la tabla spotify_songs_1000
CREATE INDEX idx_listo_index_spanish_gin_8000
    ON spotify_songs_8000 USING gin(to_tsvector('spanish', listo_index));

-- hacer un explain analyse de la query anterior
explain analyse SELECT track_name, track_artist, track_album_name, listo_index,
                       ts_rank(to_tsvector('english', listo_index), to_tsquery('english', 'Feel & Love')) AS rank
                FROM spotify_songs_8000
                WHERE to_tsvector('english', listo_index) @@ to_tsquery('english', 'Feel & Love')
                ORDER BY rank DESC
                LIMIT 5;

CREATE TABLE spotify_songs_16000 AS
SELECT *
FROM spotify_songs
LIMIT 16000;

-- Crear un índice GIN en la columna listo_index para la tabla spotify_songs_1000
CREATE INDEX idx_listo_index_english_gin_16000
    ON spotify_songs_16000 USING gin(to_tsvector('english', listo_index));

-- Crear un índice GIN en la columna listo_index para la tabla spotify_songs_1000
CREATE INDEX idx_listo_index_spanish_gin_16000
    ON spotify_songs_16000 USING gin(to_tsvector('spanish', listo_index));

-- hacer un explain analyse de la query anterior
explain analyse SELECT track_name, track_artist, track_album_name, listo_index,
                       ts_rank(to_tsvector('english', listo_index), to_tsquery('english', 'Feel & Love')) AS rank
                FROM spotify_songs_16000
                WHERE to_tsvector('english', listo_index) @@ to_tsquery('english', 'Feel & Love')
                ORDER BY rank DESC
                LIMIT 5;

explain analyse SELECT track_name, track_artist, track_album_name, listo_index,
                       ts_rank(to_tsvector('english', listo_index), to_tsquery('english', 'Feel & Love')) AS rank
                FROM spotify_songs
                WHERE to_tsvector('english', listo_index) @@ to_tsquery('english', 'Feel & Love')
                ORDER BY rank DESC
                LIMIT 5;

