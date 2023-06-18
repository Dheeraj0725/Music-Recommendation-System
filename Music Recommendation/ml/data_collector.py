import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import json
import os

client_credentials_manager = SpotifyClientCredentials(client_id='b1a36f257455497d928527ae908dfa06',
                                                      client_secret='4812348d24124b62b94128bc60cfd5ed')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

base_path = r"D:\Downloads\spotify_million_playlist_dataset\data"

file_names = [os.path.join(each) for each in os.listdir(base_path) if each.endswith('.json')]

with open('D:\Downloads\spotify_million_playlist_dataset\data\mpd.slice.0-999.json', 'r') as f:
    json_data = json.load(f)

print(json_data['playlists'])
playlists = json_data['playlists']

with open('test.json', 'w') as f:
    f.write(json.dumps(playlists[0]))

uri = "0UaMYEvWZi0ZqiDOoHU3YI"
audio_features = sp.audio_features(tracks=[uri])
print(audio_features)
