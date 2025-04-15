import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Spotify client
client_credentials_manager = SpotifyClientCredentials(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load episodes data
with open('episodes/episodes.json', 'r', encoding='utf-8') as f:
    episodes = json.load(f)

# Load or create duration cache
try:
    with open('duration_cache.json', 'r', encoding='utf-8') as f:
        duration_cache = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    duration_cache = {
        "metadata": {
            "total_duration_hours": 0,
            "last_updated": None
        },
        "episode_durations": {}
    }

# Calculate total duration
total_duration_ms = 0

# Update each episode duration in cache
for episode in episodes:
    spotify_id = episode['spotify_episode_id']
    try:
        # Get episode details from Spotify
        episode_info = sp.episode(spotify_id)
        duration_ms = episode_info['duration_ms']
        
        # Add duration to cache
        duration_cache['episode_durations'][spotify_id] = duration_ms
        total_duration_ms += duration_ms
        
        print(f"Added duration for episode: {episode['title']}")
    except Exception as e:
        print(f"Error fetching duration for episode {episode['title']}: {e}")
        # If we have cached duration, use it
        if spotify_id in duration_cache['episode_durations']:
            total_duration_ms += duration_cache['episode_durations'][spotify_id]

# Update metadata
duration_cache['metadata']['total_duration_hours'] = round(total_duration_ms / (1000 * 60 * 60), 1)
duration_cache['metadata']['last_updated'] = datetime.now().strftime('%Y-%m-%d')

# Save updated duration cache
with open('duration_cache.json', 'w', encoding='utf-8') as f:
    json.dump(duration_cache, f, ensure_ascii=False, indent=4)

print(f"\nTotal duration of all episodes: {duration_cache['metadata']['total_duration_hours']} hours")
print(f"Cache updated on: {duration_cache['metadata']['last_updated']}") 