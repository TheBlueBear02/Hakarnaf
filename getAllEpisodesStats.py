import os
import collections
import string

# Define the folder path
folder_path = "episodes"

# List of common Hebrew stopwords (expand as needed)
stopwords = {
    "אז", "של", "על", "את", "עם", "כי", "זה", "אם", "הוא", "היא", "אני", "אתה", "אנחנו", "הם", "הן", "לא", "יש", 
    "עכשיו", "כאילו", "אין", "מה", "שאני", "לו", "יותר", "עוד", "טוב", "שזה", "מאוד", "שלו", "וזה", "רגע", "אותי", 
    "אומר", "ממש", "בסדר", "איזה", "כמה", "תודה", "פה", "אותו", "מי", "איפה", "מתי", "איך", "למה", "בגלל", "כדי", 
    "או", "אבל", "גם", "רק", "כל", "אל", "לי", "היה", "כן", "הזה", "שהוא", "לנו","אתם",
    # 20 מילים נוספות
    "בוא", "נו", "שוב", "ככה", "אולי", "הייתי", "הייתה", "היית", "באמת", "דרך", "בינתיים", "לפני", "אחר", "אחרי", 
    "היום", "אתמול", "מחר", "כולם", "שלי", "נראה", "בעצם", "אליי", "אותך", "משהו"
}

# Initialize counters
word_counter = collections.Counter()
total_words = 0
file_count = 0

# Read all text files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".txt"):  # Process only text files
        file_count += 1
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read().lower()  # Convert to lowercase
            text = text.translate(str.maketrans("", "", string.punctuation))  # Remove punctuation
            words = text.split()  # Split into words
            filtered_words = [word for word in words if word not in stopwords]  # Remove stopwords
            word_counter.update(filtered_words)  # Update word frequency counter
            total_words += len(words)  # Count total words before filtering

# Get the 20 most common words
most_common_words = word_counter.most_common(5)

# Calculate the average words per file
avg_words_per_file = total_words / file_count if file_count > 0 else 0
avg_words_per_file = int(avg_words_per_file)

# Display results
print(f"Total number of files processed: {file_count}")
print(f"Total number of words (before filtering): {total_words}")
print(f"Average words per file: {avg_words_per_file:.2f}")
print("\nMost common meaningful words:")
for word, count in most_common_words:
    print(f"{word}: {count}")