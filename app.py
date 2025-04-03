from flask import Flask, render_template, request
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
            return json.load(file)
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
        "כולם", "שלי", "נראה", "בעצם", "אליי", "אותך", "משהו"
    }

    word_counter = collections.Counter()
    total_words = 0
    file_count = 0

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_count += 1
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read().lower()
                text = text.translate(str.maketrans("", "", string.punctuation))
                words = text.split()
                filtered_words = [word for word in words if word not in stopwords]
                word_counter.update(filtered_words)
                total_words += len(words)

    most_common_words = word_counter.most_common(5)
    avg_words_per_file = total_words / file_count if file_count > 0 else 0

    return {
        "file_count": file_count,
        "total_words": total_words,
        "avg_words_per_file": int(avg_words_per_file),
        "most_common_words": most_common_words
    }

def search_in_files(folder_path, search_term):
    """Search for a term in all text files inside a folder."""
    results = collections.defaultdict(list)  # Group results by episode name
    total_occurrences = 0  # Counter for total occurrences of the search term
    episodes_with_term = 0  # Counter for episodes containing the search term

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

    return {
        "results": results,
        "total_occurrences": total_occurrences,
        "episodes_with_term": episodes_with_term
    }

@app.route('/')
def home():
    episodes = load_episodes()  # Load episodes data
    stats = calculate_episode_stats()  # Calculate episode statistics
    return render_template('index.html', episodes=episodes, stats=stats)  # Pass stats to the template

@app.route('/article/<int:article_id>')
def article_detail(article_id):
    episodes = load_episodes()
    if 0 <= article_id < len(episodes):
        article = episodes[article_id]
        # Load the episode text from the corresponding .txt file
        episode_text_file = os.path.join("episodes", f"{article['title']}.txt")
        if os.path.exists(episode_text_file):
            with open(episode_text_file, "r", encoding="utf-8") as file:
                article_text = file.read()
        else:
            article_text = "Text for this episode is not available."
        return render_template('article_detail.html', article=article, article_text=article_text)
    return "Article not found", 404

@app.route('/search', methods=['GET'])
def search():
    search_term = request.args.get('q', '').strip()  # Get the search term from the query string
    if not search_term:
        return render_template('search_results.html', search_term=search_term, results=[], total_occurrences=0, episodes_with_term=0)

    folder_path = "episodes"
    search_results = search_in_files(folder_path, search_term)
    return render_template(
        'search_results.html',
        search_term=search_term,
        results=search_results['results'],
        total_occurrences=search_results['total_occurrences'],
        episodes_with_term=search_results['episodes_with_term']  # Pass the number of episodes
    )

if __name__ == '__main__':
    app.run(debug=True)