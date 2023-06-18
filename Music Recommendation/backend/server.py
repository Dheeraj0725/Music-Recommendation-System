from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse
from schema import RequestToken
from key import generate_token
import uvicorn
from confluent_kafka import Producer
import socket
import random
import datetime
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from starlette.middleware.cors import CORSMiddleware
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import NearestNeighbors

app = FastAPI(title="Recommendation Engine APIs", version="1.0.0")
conf = {'bootstrap.servers': "35.230.26.27:9092,34.105.108.110:9092,34.127.48.20:9092",
        'client.id': socket.gethostname(), 'queue.buffering.max.messages': 10000000}
# producer = Producer(conf)
client_credentials_manager = SpotifyClientCredentials(client_id='b1a36f257455497d928527ae908dfa06',
                                                    client_secret='4812348d24124b62b94128bc60cfd5ed')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:5500/', 'http://localhost:5500', 'http://127.0.0.1:5500/', 'http://127.0.0.1:5500'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
song_features = pd.read_csv(r'D:\big_data_project\backend\processeddata')
song_features = song_features.dropna() # drop any NaN values
song_features = song_features.drop_duplicates(subset='id') # drop duplicate songs
song_features = song_features.set_index('id')
song_features = song_features[['danceability', 'energy', 'loudness', 'speechiness',
                               'acousticness', 'instrumentalness', 'liveness',
                               'valence', 'tempo']]

# perform dimensionality reduction on the song features
svd = TruncatedSVD(n_components=9, random_state=42)
song_features_reduced = svd.fit_transform(song_features)

# fit nearest neighbors model
nn = NearestNeighbors(n_neighbors=15, metric='cosine')
nn.fit(song_features_reduced)

@app.get("/", tags=['Default'])
def base(request: Request):
    return RedirectResponse(url="/docs")


@app.post("/token", tags=['Engine APIs'])
def token(request: Request, token: RequestToken):
    topic = 'users'
    d = {
        'subscribed': random.choice(['Male', 'Female', None]),
        "id": token.uuid,
        'gender': random.choice(['Male', 'Female', None])
    }
    # producer.produce(topic, json.dumps(d))
    return {"message": "successfully logged in"}


@app.get("/search", tags=['Engine APIs'])
async def search(request: Request, track):
    topic = 'search'
    d = {
        'track': track
    }
    # producer.produce(topic, json.dumps(d))
    res = sp.search(q=track, type="track")
    items = res.get('tracks').get('items')
    songs = []
    for each in items:
        d = {
            'name': each.get('name', ''),
            'artists': ','.join([each_ar['name'] for each_ar in each.get('artists')]),
            'id': each.get('id')
        }
        songs.append(d)
    return {'items': songs}


@app.get('/recommend', tags=['Engine APIs'])
def recommend(request: Request, song_uri):
    topic = 'searchclicks'
    d = {
        'track_uri': song_uri
    }

    # producer.produce(topic, json.dumps(d))

    track_id = [song_uri]
    fea = sp.audio_features(tracks=song_uri)
    f = {} #{'id': track_id}
    for each in ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness',
       'instrumentalness', 'liveness', 'valence', 'tempo']:
        f[each] = fea[0][each]
    a = pd.DataFrame(f, index=track_id)
    # a.set_index(['id'], inplace=True)
    user_features = a.loc[track_id].mean(axis=0).values.reshape(1, -1)
    user_features_reduced = svd.transform(user_features)
    distances, indices = nn.kneighbors(user_features_reduced)
    recommended_songs = song_features.iloc[indices[0]].index.tolist()
    t = sp.tracks(tracks=[f'spotify:track:{each}' for each in recommended_songs]).get('tracks')
    return {"items": [{"name": each['name']} for each in t]}


if __name__ == "__main__":
    uvicorn.run(app=app)
