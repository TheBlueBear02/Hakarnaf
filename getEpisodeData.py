import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import re
from dotenv import load_dotenv
import openai
import os
from datetime import datetime
import time  # Import the time module to measure runtime
import json  # Import the json module
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from getSpotifyEpisodeId import search_episode_by_name

# Load environment variables from .env
load_dotenv()

def split_text(text, max_length=3000):
    """Splits text into chunks of max_length tokens."""
    chunks = []
    while (len(text) > max_length):
        split_index = text.rfind(" ", 0, max_length)
        if split_index == -1:
            split_index = max_length
        chunks.append(text[:split_index])
        text = text[split_index:].lstrip()
    chunks.append(text)  # Add the remaining text as the last chunk
    return chunks


def process_text(text, api_key):
    """Fixes spelling, punctuation, and paragraph formatting for the text."""
    openai.api_key = api_key  # Set the API key directly
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=[
                {"role": "system", "content": (
                    "אתה עורך טקסט בעברית. המשימה שלך היא:"
                    "\n1. לתקן שגיאות כתיב בטקסט."
                    "\n2. להוסיף פיסוק מתאים תוך שמירה על המשמעות המקורית של הטקסט."
                    "\n3. לחלק את הטקסט לפסקאות ברורות ומסודרות"
                    "\n4. לשמור על מבנה הטקסט המקורי ולא לשנות את סדר המשפטים או המילים."
                    "\n5. לא להוסיף מידע חדש או לשנות את המשמעות של הטקסט."
                    "\n6. להחזיר את הטקסט המעובד במלואו, ללא קיצורים או השמטות."
                    "\nרשימת מילים נפוצות בעברית שעליך להכיר: "
                    "שב\"כ רונן בר, הרצי הלוי, ביבי, בנימין נתניהו, ישראל כץ, בצלאל סמוטריץ, בן גביר, הקרנף."
                )},
                {"role": "user", "content": text}
            ]
        )
        # Check if the response is complete
        if not response.choices or not response.choices[0].message.content:
            raise ValueError("Empty response from OpenAI API")
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error processing text chunk: {e}")
        return ""

def extract_topics(text, api_key):
    """Extracts specific topical issues from the text."""
    openai.api_key = api_key  # Set the API key directly
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0,  # Set temperature to 0 for deterministic output
            messages=[
                {"role": "system", "content": (
                    "אתה עוזר לניתוח טקסט. המשימה שלך היא:"
                    "\n1. לזהות את הנושאים המרכזיים והספציפיים שעלו בטקסט."
                    "\n2. הנושאים צריכים להיות ממוקדים ומפורטים, לדוגמה: 'פיטורי ראש השב\"כ', 'הופעתה של מירי רגב בערוץ 14'."
                    "\n3. להימנע מנושאים כלליים מדי כמו 'המצב הביטחוני' או 'הפוליטיקה בישראל'."
                    "\n4. להחזיר רשימה מסודרת של הנושאים המרכזיים בלבד, כאשר כל נושא מופיע בשורה נפרדת."
                    "\n5. לשמור על ניסוח ברור ותמציתי."
                    "בנוסף תתקן את המילה שבק לשבכ"
                )},
                {"role": "user", "content": text}
            ]
        )
        # Check if the response is complete
        if not response.choices or not response.choices[0].message.content:
            raise ValueError("Empty response from OpenAI API")
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error extracting topics: {e}")
        return "Error extracting topics."

def extract_topics_from_chunks(text_chunks, api_key):
    """Extracts the most important topic from each text chunk."""
    openai.api_key = api_key  # Set the API key directly

    top_topics = []
    for i, chunk in enumerate(text_chunks):
        print(f"Extracting the top topic from chunk {i + 1}/{len(text_chunks)}...")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                temperature=0,  # Set temperature to 0 for deterministic output
                messages=[
                    {"role": "system", "content": (
                        "אתה עוזר לניתוח טקסט. המשימה שלך היא:" 
                        "\n1. לזהות את הנושא המרכזי והחשוב ביותר שעלה בטקסט." 
                        "\n2. הנושא צריך להיות ממוקד, מפורט וברור, לדוגמה: 'פיטורי ראש השב\"כ', 'הופעתה של מירי רגב בערוץ 14'." 
                        "\n3. להימנע מנושאים כלליים מדי כמו 'המצב הביטחוני' או 'הפוליטיקה בישראל'." 
                        "\n4. מאוד חשוב להחזיר את הנושא בלבד!, ללא הקדמות או הסברים נוספים." 
                        "\n5. להימנע מהוספת טקסט כמו 'הנושא המרכזי בקטע הוא'." 
                        "בנוסף חשוב שזה יהיה תמציתי מקסימום משפט אחד קצר"
                    )},
                    {"role": "user", "content": chunk}
                ]
            )
            # Check if the response is complete
            if not response.choices or not response.choices[0].message.content:
                raise ValueError("Empty response from OpenAI API")
            top_topic = response.choices[0].message.content.strip()
            top_topics.append(top_topic)
        except Exception as e:
            print(f"Error extracting topic from chunk {i + 1}: {e}")

    return top_topics

def get_video_info(video_url):
    """Fetches video title and upload date using yt-dlp, formats date as dd/mm/yy."""
    ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        video_title = info.get("title", "Unknown Title")
        video_date = info.get("upload_date", "Unknown Date")  # Format: YYYYMMDD

        # Convert date to dd/mm/yy format
        if video_date != "Unknown Date":
            video_date = datetime.strptime(video_date, "%Y%m%d").strftime("%d/%m/%y")
        
        print("got video info")
        return video_title, video_date

def get_video_transcript(video_url, lang="iw"):
    """Fetches the transcript in the specified language (default: Hebrew) and combines it into one paragraph."""
    video_id_match = re.search(r"(?<=v=)[^&]+", video_url) or re.search(r"(?<=youtu\.be/)[^?]+", video_url)

    if not video_id_match:
        return "Invalid video URL"

    video_id = video_id_match.group(0)

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
        transcript_text = " ".join([t['text'] for t in transcript])  # Combine all sentences into one paragraph
        print("got episode's transcript")
        return transcript_text
    except NoTranscriptFound:
        return "No Hebrew transcript available."
    except TranscriptsDisabled:
        return "Transcripts are disabled for this video."
    except Exception as e:
        return f"Error retrieving transcript: {e}"

def save_to_file(title, date, transcript, filename):
    """Saves the video info and transcript to a text file."""
    filename = filename.replace("_", " ")  # Replace underscores with spaces in the filename
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"Title: {title}\n")
        file.write(f"Upload Date: {date}\n\n")
        file.write("Transcript:\n")
        file.write(transcript)

def get_spotify_episode_date(episode_id):
    """Fetches the release date of a Spotify episode using its ID."""
    try:
        episode_details = get_episode_details(episode_id)  # Fetch episode details
        return episode_details.get("release_date", "Unknown Date")  # Return release date or default
    except Exception as e:
        print(f"Error fetching Spotify episode date: {e}")
        return "Unknown Date"

def update_duration_cache(spotify_id, duration_ms):
    """Updates the duration cache with a new episode's duration."""
    try:
        # Load existing cache
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

        # Add new episode duration
        duration_cache['episode_durations'][spotify_id] = duration_ms

        # Update total duration (convert from ms to hours)
        total_duration_ms = sum(duration_cache['episode_durations'].values())
        duration_cache['metadata']['total_duration_hours'] = round(total_duration_ms / (1000 * 60 * 60), 1)
        duration_cache['metadata']['last_updated'] = datetime.now().strftime('%Y-%m-%d')

        # Save updated cache
        with open('duration_cache.json', 'w', encoding='utf-8') as f:
            json.dump(duration_cache, f, ensure_ascii=False, indent=4)

        print(f"Updated duration cache. Total duration: {duration_cache['metadata']['total_duration_hours']} hours")
    except Exception as e:
        print(f"Error updating duration cache: {e}")

def get_episode_duration(spotify_id):
    """Gets episode duration from Spotify API."""
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        # Get episode details from Spotify
        episode_info = sp.episode(spotify_id)
        duration_ms = episode_info['duration_ms']
        
        return duration_ms
    except Exception as e:
        print(f"Error fetching episode duration: {e}")
        return None

if __name__ == "__main__":
    # Record the start time
    start_time = time.time()

    video_url = input("Enter YouTube video URL: ")
    title, date = get_video_info(video_url)
    transcript = get_video_transcript(video_url, lang="iw")

    # Split text into chunks
    text_chunks = split_text(transcript)

    api_key = os.getenv("OPENAI_API_KEY")
    # Process the text in chunks for correction
    processed_chunks = []
    for i, chunk in enumerate(text_chunks):
        print(f"Processing chunk {i + 1}/{len(text_chunks)}...")
        processed_chunk = process_text(chunk, api_key)
        if processed_chunk:
            processed_chunks.append(processed_chunk)
        else:
            print(f"Chunk {i + 1} was not processed correctly.")

    # Combine all processed chunks
    processed_text = "\n\n".join(processed_chunks)

    # Split the processed text into smaller chunks for topic extraction
    topic_chunks = split_text(processed_text, max_length=3000)

    # Extract the most important topic from each chunk
    print("Extracting the most important topic from each chunk...")
    top_topics = extract_topics_from_chunks(topic_chunks, api_key)

    # Fetch Spotify episode ID
    spotify_episode_id = None
    spotify_episode_date = "Unknown Date"  # Default value
    try:
        print(f"Searching for Spotify episode ID for: {title}")
        episode_data = search_episode_by_name(title, limit=1)
        if episode_data != 'None spotify episode found':
            spotify_episode_id = episode_data['id']  # Assuming the first result is the most relevant
            spotify_episode_date = episode_data['release_date']  # Fetch release date
    except Exception as e:
        print(f"Error fetching Spotify episode ID or date: {e}")

    # Remove the term " | הקרנף" from the title
    clean_title = title.replace(" | הקרנף", "")

    # Format the filename using the cleaned title
    safe_title = re.sub(r'[\\/*?:"<>|]', "_", clean_title)  # Replace invalid characters

    episodes_dir = "episodes"
    os.makedirs(episodes_dir, exist_ok=True)  # Ensure the episodes directory exists
    transcript_filename = os.path.join(episodes_dir, f"{safe_title}.txt")
    json_filename = os.path.join(episodes_dir, "episodes.json")

    # Save the processed text to a separate text file
    with open(transcript_filename, "w", encoding="utf-8") as file:
        file.write(processed_text)

    # Create or update the JSON file with episode metadata
    episode_data = {
        "title": clean_title,
        "upload_date": spotify_episode_date,
        "topical_issues": top_topics,
        "transcript_file": os.path.basename(transcript_filename),
        "spotify_episode_id": spotify_episode_id  # Assuming you have this variable defined
    }

    if os.path.exists(json_filename):
        with open(json_filename, "r", encoding="utf-8") as json_file:
            episodes = json.load(json_file)
    else:
        episodes = []

    episodes.append(episode_data)

    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(episodes, json_file, ensure_ascii=False, indent=4)

    # Calculate and print the total runtime
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Transcript saved in: {transcript_filename}")
    print(f"Episode metadata updated in: {json_filename}")
    print(f"Script completed in {elapsed_time:.2f} seconds.")

    # Get Spotify episode ID
    spotify_id = search_episode_by_name(title)
    if spotify_id:
        # Get episode duration and update cache
        duration_ms = get_episode_duration(spotify_id)
        if duration_ms:
            update_duration_cache(spotify_id, duration_ms)
