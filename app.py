from flask import Flask, render_template, request, redirect, url_for
import os
import json
import collections
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()

def get_spotify_client():
    """Initialize and return Spotify client."""
    client_id = os.getenv('spotify_client_id')
    client_secret = os.getenv('spotify_client_secret')
    
    if not client_id or not client_secret:
        return None
        
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(auth_manager=auth_manager)

def get_episode_durations(episodes):
    """Get episode durations from Spotify."""
    sp = get_spotify_client()
    if not sp:
        return {
            "total_duration_hours": "N/A",
            "total_duration_minutes": "N/A",
            "avg_duration_minutes": "N/A"
        }
    
    total_duration_ms = 0
    episode_count = 0
    
    for episode in episodes:
        if 'spotify_episode_id' in episode:
            try:
                result = sp.episode(episode['spotify_episode_id'])
                if result and 'duration_ms' in result:
                    total_duration_ms += result['duration_ms']
                    episode_count += 1
            except Exception as e:
                print(f"Error fetching episode duration: {e}")
                continue
    
    if episode_count == 0:
        return {
            "total_duration_hours": "N/A",
            "total_duration_minutes": "N/A",
            "avg_duration_minutes": "N/A"
        }
    
    # Convert total duration from ms to minutes and hours
    total_minutes = total_duration_ms / (1000 * 60)
    total_hours = total_minutes / 60
    avg_minutes = total_minutes / episode_count
    
    return {
        "total_duration_hours": f"{total_hours:.1f}",
        "total_duration_minutes": f"{total_minutes:.0f}",
        "avg_duration_minutes": f"{avg_minutes:.0f}"
    }

def load_episodes():
    """Loads episodes data from the episodes.json file."""
    episodes_file = os.path.join("episodes", "episodes.json")
    if os.path.exists(episodes_file):
        with open(episodes_file, "r", encoding="utf-8") as file:
            episodes = json.load(file)
            # Ensure each episode has a properly formatted date
            for episode in episodes:
                if 'upload_date' in episode:
                    episode['date'] = episode['upload_date']  # Map 'upload_date' to 'date'
            return episodes
    return []

def calculate_episode_stats():
    """Calculates statistics for all episodes."""
    folder_path = "episodes"
    stopwords = {
        "אז", "של", "על", "את", "עם", "כי", "זה", "אם", "הוא", "היא", "אני", "אתה", "אנחנו", "הם", "הן", "לא", "יש",
        "עכשיו", "כאילו", "אין", "מה", "שאני", "לו", "יותר", "עוד", "טוב", "שזה", "מאוד", "שלו", "וזה", "רגע", "אותי",
        "אומר", "ממש", "בסדר", "איזה", "כמה", "תודה", "פה", "אותו", "מי", "איפה", "מתי", "איך", "למה", "בגלל", "כדי",
        "או", "אבל", "גם", "רק", "כל", "אל", "לי", "היה", "כן", "הזה", "שהוא", "לנו", "אתם", "בוא", "נו", "שוב", "ככה",
        "אולי", "הייתי", "הייתה", "היית", "באמת", "דרך", "בינתיים", "לפני", "אחר", "אחרי", "היום", "אתמול", "מחר",
        "כולם", "שלי", "נראה", "בעצם", "אליי", "אותך", "משהו", "להיות", "הזאת", "להגיד", "חושב", "יודע", "פשוט", "לכם", "כך", "וגם","משמעות", "רוצה",
        "שהיא", "כבר", "שלא", "נכון", "שהם", "ואני", "כמו", "שיש", "אפשר", "אוקיי", "אומרים", "שם", "צריך", "יכול", "הרבה","זו", "לעשות","אחד","הכל","מחיאות","כפיים","עושה","ולא","הולך","בני"
    }

    word_list = ["ראש הממשלה", "ישראל", "איראן", "הרמט\"ל"," צה\"ל", "צבא", "חמאס", "חיזבאללה", "עזה", "שר הביטחון", "הקרנף", "שמאל", "ימין", "ערוץ 14"
                  "ערוץ 12", "ערוץ 13", "חדשות 12", "חדשות 13", "הכנסת", "אופוזיציה", "תוכנית", "פוליטיקה", "בחירות", "חוק", "בגץ", "בית המשפט",
                  "משטרה", "שב\"כ", "מלחמה", "קטאר"
                  ]
    word_counter = collections.Counter()
    total_words = 0  # Track total words across all episodes
    episode_count = 0  # Track the number of episodes

    # Load episodes for duration stats
    episodes = load_episodes()
    duration_stats = get_episode_durations(episodes)

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            episode_count += 1  # Increment episode count
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read().lower()
                total_words += len(text.split())  # Count words in the episode
                for word in word_list:
                    word_counter[word] += text.count(word)

    most_common_words = word_counter.most_common()

    # Calculate average words per episode
    avg_words_per_episode = total_words // episode_count if episode_count > 0 else 0

    # Format total words and average words per episode with commas
    total_words_formatted = f"{total_words:,}"
    avg_words_per_episode_formatted = f"{avg_words_per_episode:,}"

    names = ["רונן בר", "הרצי", "ביבי", "בנימין נתניהו", "ישראל כץ", "בצלאל סמוטריץ", "בן גביר", "גנץ","בנט", "איילת שקד", " גלנט", "גדי איזנקוט", "בן גוריון","טראמפ","אמסלם","האריס", "לפיד", "ליברמן", "אהוד ברק", "אהרון ברק",
             "ביידן", "פלדשטיין","בוגי","טלי גוטליב", "יריב לוין", "קרעי", "סינוואר", "נסראללה", "ברדוגו"
             ]
    name_counter = collections.Counter()

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
                for name in names:
                    name_counter[name] += text.count(name)

    most_common_names = name_counter.most_common()

    # Add duration stats to the return value
    return {
        "most_common_words": most_common_words,
        "most_common_names": most_common_names,
        "total_words": total_words_formatted,
        "episode_count": episode_count,
        "avg_words_per_episode": avg_words_per_episode_formatted,
        "total_duration_hours": duration_stats["total_duration_hours"],
        "total_duration_minutes": duration_stats["total_duration_minutes"],
        "avg_duration_minutes": duration_stats["avg_duration_minutes"]
    }

def search_in_files(folder_path, search_term):
    """Search for a term in all text files inside a folder."""
    results = collections.defaultdict(list)  # Group results by episode name
    total_occurrences = 0  # Counter for total occurrences of the search term
    episodes_with_term = 0  # Counter for episodes containing the search term
    episodes_occurrences = {}  # Track occurrences per episode

    episodes = load_episodes()  # Load episodes to preserve their order
    episode_order = {episode['title']: index for index, episode in enumerate(episodes)}  # Map episode titles to their order
    episodes_occurrences = {episode['title']: 0 for episode in episodes}  # Initialize all episodes with 0 occurrences

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):  # Process only text files
            file_path = os.path.join(folder_path, filename)
            episode_name = os.path.splitext(filename)[0]  # Extract episode name
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                episode_occurrences = 0  # Track occurrences in the current episode
                for line in lines:
                    occurrences = line.count(search_term)  # Count occurrences in the line
                    total_occurrences += occurrences
                    episode_occurrences += occurrences
                    if occurrences > 0:
                        # Highlight the search term in the line with a background color
                        highlighted_line = line.replace(
                            search_term, f"<span class='highlight'>{search_term}</span>"
                        )
                        results[episode_name].append({
                            "line": highlighted_line.strip(),
                            "occurrences": occurrences
                        })
                if episode_occurrences > 0:
                    episodes_with_term += 1
                    results[episode_name] = results[episode_name]  # Ensure results are grouped by episode_name
                episodes_occurrences[episode_name] = episode_occurrences  # Update occurrences for the episode

    return {
        "results": results,
        "total_occurrences": total_occurrences,
        "episodes_with_term": episodes_with_term,
        "occurrences_per_episode": episodes_occurrences
    }

def get_article_id(episode_name):
    """Returns the article ID for a given episode name."""
    episodes = load_episodes()
    for index, episode in enumerate(episodes):
        if episode['title'] == episode_name:
            return index
    return -1  # Return -1 if the episode name is not found

@app.route('/')
def home():
    episodes = load_episodes()  # Load episodes data
    stats = calculate_episode_stats()  # Calculate episode statistics
    return render_template(
        'index.html',
        episodes=episodes,
        stats=stats,
        total_words=stats["total_words"],  # Pass formatted total words
        episode_count=stats["episode_count"] + 1,  # Pass episode count
        avg_words_per_episode=stats["avg_words_per_episode"]  # Pass formatted average words per episode
    )

@app.route('/article/<int:article_id>')
def article_detail(article_id):
    episodes = load_episodes()
    search_term = request.args.get('q', '').strip()  # Get the search term from the query string
    if 0 <= article_id < len(episodes):
        article = episodes[article_id]
        article['id'] = article_id  # Add the id key to the article dictionary
        # Load the episode text from the corresponding .txt file
        episode_text_file = os.path.join("episodes", f"{article['transcript_file']}")
        occurrences_count = 0  # Initialize occurrences count
        if os.path.exists(episode_text_file):
            with open(episode_text_file, "r", encoding="utf-8") as file:
                article_text = file.read()
                if search_term:
                    # Count occurrences of the search term in the article text
                    occurrences_count = article_text.count(search_term)
                    # Highlight the search term in the article text
                    article_text = article_text.replace(
                        search_term, f"<span class='highlight'>{search_term}</span>"
                    )
           
        else:
            article_text = "Text for this episode is not available."

        # Add Spotify embed URL to the article
        spotify_embed_url = f"https://open.spotify.com/embed/episode/{article['spotify_episode_id']}"
        article['spotify_embed_url'] = spotify_embed_url

        return render_template(
            'article_detail.html',
            article=article,
            article_text=article_text,
            search_term=search_term,  # Pass the search term to the template
            occurrences_count=occurrences_count  # Pass the occurrences count to the template
        )
    return "Article not found", 404

@app.route('/search', methods=['GET'])
def search():
    search_term = request.args.get('q', '').strip()  # Get the search term from the query string
    reverse_order = request.args.get('reverse', 'true').lower() == 'true'  # Default to true for newest first
    if not search_term:
        # Redirect back to the home page if the search term is empty
        return redirect(url_for('home'))

    folder_path = "episodes"
    search_results = search_in_files(folder_path, search_term)
    
    # Load all episodes to establish correct order
    all_episodes = load_episodes()
    
    # Create a mapping of episode title to its chronological position
    episode_positions = {}
    transcript_to_title = {}
    
    # First, create mapping of transcript filenames to episode titles
    for episode in all_episodes:
        if 'transcript_file' in episode:
            transcript_name = os.path.splitext(episode['transcript_file'])[0]
            transcript_to_title[transcript_name] = episode['title']
            
    # Then create position mapping for all possible names
    for i, episode in enumerate(all_episodes):
        # Map the episode title to its position
        episode_positions[episode['title']] = i
        
        # If there's a transcript file, map its name too
        if 'transcript_file' in episode:
            transcript_name = os.path.splitext(episode['transcript_file'])[0]
            episode_positions[transcript_name] = i
    
    # Convert the results OrderedDict to a regular dict for easier manipulation
    results_dict = dict(search_results['results'])
    
    # Sort the results based on episode position in the full episodes list
    def get_position(episode_name):
        # First try direct lookup
        if episode_name in episode_positions:
            return episode_positions[episode_name]
        
        # Try to find a close match
        for known_name in episode_positions:
            if episode_name in known_name or known_name in episode_name:
                return episode_positions[known_name]
        
        # If we couldn't find any match, put it at the end
        print(f"Warning: Could not find position for episode: {episode_name}")
        return 999999
    
    sorted_results = dict(
        sorted(
            results_dict.items(),
            key=lambda x: get_position(x[0])
        )
    )
    
    # If reverse_order is true, reverse the sorted dictionary after sorting
    if reverse_order:
        sorted_results = dict(reversed(list(sorted_results.items())))
    
    # Keep the original order for the graph data
    original_occurrences = search_results['occurrences_per_episode']
    
    return render_template(
        'search_results.html',
        search_term=search_term,
        results=sorted_results,
        total_occurrences=search_results['total_occurrences'],
        episodes_with_term=search_results['episodes_with_term'],
        occurrences_per_episode_keys=list(original_occurrences.keys()),
        occurrences_per_episode_values=list(original_occurrences.values()),
        reverse_order=reverse_order
    )

@app.route('/all_articles')
def all_articles():
    episodes = load_episodes()  # Load episodes data in the order they appear in the JSON file
    reverse_order = request.args.get('reverse', 'true').lower() == 'true'  # Default to true for newest first
    if reverse_order:
        episodes = list(reversed(episodes))  # Reverse the order of episodes
    return render_template('all_articles.html', articles=episodes, reverse_order=reverse_order)  # Pass reverse_order to the template

@app.route('/terms_of_service')
def terms_of_service():
    return render_template('terms_of_service.html')

# Register get_article_id as a global function for Jinja2 templates
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Optional: Enable auto-reloading of templates
app.jinja_env.globals.update(get_article_id=get_article_id)

if __name__ == '__main__':
    app.run()