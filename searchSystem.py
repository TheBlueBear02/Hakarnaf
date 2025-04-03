import os

def shorten_line(line, search_term):
    """Shorten long lines by keeping only 2-3 sentences around the search term."""
    sentences = line.split(". ")  # Split the line into sentences
    matching_sentences = [s for s in sentences if search_term in s]

    if not matching_sentences:
        return line.strip()  # Return the full line if no match is found

    # Find the index of the first matching sentence
    index = sentences.index(matching_sentences[0])

    # Get up to 2 sentences before and 1 sentence after the match
    start = max(0, index - 2)
    end = min(len(sentences), index + 2)
    shortened = ". ".join(sentences[start:end])

    # Add "..." if text was cut
    if start > 0:
        shortened = "... " + shortened
    if end < len(sentences):
        shortened += " ..."

    return shortened.strip()

def search_in_files(folder_path, search_term):
    """Search for a term in all text files inside a folder."""
    matching_files = []  # List to store files that contain the search term
    total_occurrences = 0  # Counter for total occurrences of the search term

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):  # Process only text files
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                found = False  # Track if term is found in the file
                
                for line in lines:
                    occurrences = line.count(search_term)  # Count occurrences in the line
                    total_occurrences += occurrences
                    if occurrences > 0:
                        if not found:  
                            matching_files.append(filename)  # Add file only once
                            found = True
                        print(f"📄 {filename}: {shorten_line(line, search_term)}")  # Show shortened line
                
    # Show results
    if matching_files:
        print("\n🔍 Search Results:")
        for file in matching_files:
            print(f"- {file}")
        print(f"\n📊 The term '{search_term}' appeared {total_occurrences} times across all files.")
    else:
        print("\n❌ No matches found.")

# Example usage
folder_path = "episodes"  # Change this to your actual folder path
search_term = input("Enter search term: ")  # Ask user for search input
search_in_files(folder_path, search_term)
