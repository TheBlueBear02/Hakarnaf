import os

def replace_in_txt_files(folder_path):
    targets = [
        "[מוזיקה][מחיאות כפיים]",
        "[מחיאות כפיים][מוזיקה]"
    ]

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            for target in targets:
                content = content.replace(target, "[פתיח]")

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

            print(f"Updated: {filename}")

# Example usage:
folder_path = "episodes"  # <- Replace this with your actual folder path
replace_in_txt_files(folder_path)
