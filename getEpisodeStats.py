import collections
import string

# Define stopwords
stopwords = {
    "אז", "של", "על", "את", "עם", "כי", "זה", "אם", "הוא", "היא", "אני", "אתה", "אנחנו", "הם", "הן", "לא", "יש", 
    "עכשיו", "כאילו", "אין", "מה", "שאני", "לו", "יותר", "עוד", "טוב", "שזה", "מאוד", "שלו", "וזה", "רגע", "אותי", 
    "אומר", "ממש", "בסדר", "איזה", "כמה", "תודה", "פה", "אותו", "מי", "איפה", "מתי", "איך", "למה", "בגלל", "כדי", 
    "או", "אבל", "גם", "רק", "כל", "אל", "לי", "היה", "כן", "הזה", "שהוא", "לנו",
    "בוא", "נו", "שוב", "ככה", "אולי", "הייתי", "הייתה", "היית", "באמת", "דרך", "בינתיים", "לפני", "אחר", "אחרי", 
    "היום", "אתמול", "מחר", "כולם", "שלי", "נראה", "בעצם", "אליי", "אותך", "משהו"
}

def analyze_text_file(file_path):
    """Analyze a single text file: count words and show the most common words."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read().lower()  # Convert to lowercase
            text = text.translate(str.maketrans("", "", string.punctuation))  # Remove punctuation
            words = text.split()  # Split into words
            
            total_words = len(words)  # Total word count
            filtered_words = [word for word in words if word not in stopwords]  # Remove stopwords
            
            word_counter = collections.Counter(filtered_words)  # Count word frequency
            most_common_words = word_counter.most_common(5)  # Get 20 most common words

            # Display results
            print(f"\nFile: {file_path}")
            print(f"Total number of words: {total_words}")
            print("\nMost common meaningful words:")
            for word, count in most_common_words:
                print(f"{word}: {count}")
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
file_name = "episodes\פרק 1 - משיח, משיח, משיח.txt"  # Change this to your actual file path
analyze_text_file(file_name)
