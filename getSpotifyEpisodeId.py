import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
from datetime import datetime  # Import datetime for date formatting

# Load environment variables from .env
load_dotenv()

# Fetch credentials from environment variables
client_id = os.getenv('spotify_client_id')
client_secret = os.getenv('spotify_client_secret')

# Auth
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

def search_episode_by_name(name, limit=1):
    results = sp.search(q=name, type='episode', limit=limit)
    episodes = results['episodes']['items']
    for ep in episodes:
        print(f"Name: {ep['name']}")
        print(f"Episode ID: {ep['id']}")
        print(f"URL: {ep['external_urls']['spotify']}")
        
        # Reformat release date to dd/mm/yyyy
        release_date = ep['release_date']
        formatted_date = datetime.strptime(release_date, "%Y-%m-%d").strftime("%d/%m/%Y")
        print(f"Release Date: {formatted_date}")  # Print the formatted release date

    return {
        "id": ep['id'],
        "release_date": formatted_date  # Return the formatted date
    } if episodes else 'None spotify episode found'