from flask import Flask, render_template, request, redirect, url_for
import os
import json
import collections
import string

app = Flask(__name__)

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
                  "ערוץ 12", "ערוץ 13", "חדשות 12", "חדשות 13", "הכנסת", "ממשלה", "אופוזיציה", "תוכנית", "פוליטיקה", "בחירות", "חוק", "בגץ", "בית המשפט"]
    word_counter = collections.Counter()

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read().lower()
                for word in word_list:
                    word_counter[word] += text.count(word)

    most_common_words = word_counter.most_common()

    names = ["רונן בר", "הרצי", "ביבי", "בנימין נתניהו", "ישראל כץ", "בצלאל סמוטריץ", "בן גביר", "גנץ","בנט", "איילת שקד", " גלנט", "גדי איזנקוט", "בן גוריון","טראמפ","אמסלם"]
    name_counter = collections.Counter()

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
                for name in names:
                    name_counter[name] += text.count(name)

    most_common_names = name_counter.most_common()

    return {
        "most_common_words": most_common_words,
        "most_common_names": most_common_names
    }

def search_in_files(folder_path, search_term):
    """Search for a term in all text files inside a folder."""
    results = collections.defaultdict(list)  # Group results by episode name
    total_occurrences = 0  # Counter for total occurrences of the search term
    episodes_with_term = 0  # Counter for episodes containing the search term
    occurrences_per_episode = {}  # Track occurrences per episode

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
            occurrences_per_episode[episode_name] = episode_occurrences

    return {
        "results": results,
        "total_occurrences": total_occurrences,
        "episodes_with_term": episodes_with_term,
        "occurrences_per_episode": occurrences_per_episode  # Include occurrences per episode
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
    return render_template('index.html', episodes=episodes, stats=stats)  # Pass stats to the template

@app.route('/article/<int:article_id>')
def article_detail(article_id):
    episodes = load_episodes()
    search_term = request.args.get('q', '').strip()  # Get the search term from the query string
    if 0 <= article_id < len(episodes):
        article = episodes[article_id]
        article['id'] = article_id  # Add the id key to the article dictionary
        # Load the episode text from the corresponding .txt file
        episode_text_file = os.path.join("episodes", f"{article['title']}.txt")
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
    if not search_term:
        # Redirect back to the home page if the search term is empty
        return redirect(url_for('home'))

    folder_path = "episodes"
    search_results = search_in_files(folder_path, search_term)
    return render_template(
        'search_results.html',
        search_term=search_term,
        results=search_results['results'],
        total_occurrences=search_results['total_occurrences'],
        episodes_with_term=search_results['episodes_with_term'],  # Pass the number of episodes
        occurrences_per_episode_keys=list(search_results['occurrences_per_episode'].keys()),  # Convert keys to list
        occurrences_per_episode_values=list(search_results['occurrences_per_episode'].values())  # Convert values to list
    )

@app.route('/all_articles')
def all_articles():
    episodes = load_episodes()  # Load episodes data
    return render_template('all_articles.html', articles=episodes)  # Pass episodes as articles to the template

if __name__ == '__main__':
    app.jinja_env.globals.update(get_article_id=get_article_id)
    app.run(debug=True, host='0.0.0.0')