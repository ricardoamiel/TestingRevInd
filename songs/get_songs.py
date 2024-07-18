import pandas as pd
import time 
import subprocess
import os
import glob

songs = pd.read_csv('BD2/spotify_songs_1000.csv')

def get_song_spotify(track_id, requests):
    url = f'https://open.spotify.com/track/{track_id}'
    try_request = 0
    while try_request < requests:
        command = ['spotdl', 'download', url , '--output', f'{"songs/get_songs"}/{track_id}']
        try:
            download_process = subprocess.run(command, check=True)
            if download_process.returncode == 0:
                return True
        except subprocess.CalledProcessError:
            # Si falla, esperar 1 segundo y volver a intentar
            time.sleep(1)
            try_request += 1
    print(f'Error en {track_id}.')
    return False

for track_id in songs['track_id']:
    song_directory = os.path.join("songs/get_songs", track_id)

    # Check if the song has already been downloaded
    downloaded_songs = glob.glob(os.path.join(song_directory, '*.mp3'))
    if not downloaded_songs:
        # Attempt to download the song
        if not get_song_spotify(track_id, 3):
            print(f'Throw download {track_id}.')
            exit(1)
    else:
        print(f'{track_id} ya existe.')
