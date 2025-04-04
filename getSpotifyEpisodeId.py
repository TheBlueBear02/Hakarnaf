import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch credentials from environment variables
client_id = os.getenv('spotify_client_id')
client_secret = os.getenv('spotify_client_secret')

# Auth
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

def search_episode_by_name(name, limit=5):
    results = sp.search(q=name, type='episode', limit=limit)
    episodes = results['episodes']['items']
    for ep in episodes:
        print(f"Name: {ep['name']}")
        print(f"Episode ID: {ep['id']}")
        print(f"URL: {ep['external_urls']['spotify']}")

    return ep['id'] if episodes else 'None spotify episode found'