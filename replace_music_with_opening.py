import os
import re

def replace_in_txt_files(folder_path):
    # Define regex patterns to match both with and without space
    patterns = [
        r"\[מוזיקה\]\s*\[מחיאות כפיים\]",
        r"\[מחיאות כפיים\]\s*\[מוזיקה\]"
    ]

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            new_content = content
            for pattern in patterns:
                new_content = re.sub(pattern, "[פתיח]", new_content)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)

            print(f"Updated: {filename}")

# Example usage:
folder_path = "episodes"  # <- Replace this with your actual folder path
replace_in_txt_files(folder_path)
