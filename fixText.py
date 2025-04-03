from dotenv import load_dotenv
import openai
import os

# Load environment variables from .env
load_dotenv()

def split_text(text, max_length=8000):
    """Splits text into chunks of max_length tokens."""
    chunks = []
    while len(text) > max_length:
        split_index = text.rfind(" ", 0, max_length)
        if split_index == -1:
            split_index = max_length
        chunks.append(text[:split_index])
        text = text[split_index:].lstrip()
    chunks.append(text)
    return chunks

def process_text(text, api_key):
    """Fixes spelling, punctuation, and paragraph formatting for the text."""
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": (
                "אתה עורך טקסט בעברית. המשימה שלך היא:"
                "\n1. לתקן שגיאות כתיב."
                "\n2. להוסיף פיסוק מתאים תוך שמירה על המשמעות המקורית."
                "\n3. לחלק את הטקסט לפסקאות ברורות ומסודרות."
                "\nשמור על עברית תקינה ואל תתרגם את הטקסט אלא אם יש קטע באנגלית בטקסט המקורי."
            )},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

def process_file(input_file, output_file, api_key):
    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Split text into chunks
    text_chunks = split_text(text)
    
    # Process the text in chunks for correction
    processed_chunks = [process_text(chunk, api_key) for chunk in text_chunks]
    processed_text = "\n\n".join(processed_chunks)
    
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(processed_text)

if __name__ == "__main__":
    input_file = "youtube_transcript.txt"
    output_file = "output.txt"
    
    # Load API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("Missing OpenAI API key. Ensure you have a .env file with OPENAI_API_KEY set.")
    
    process_file(input_file, output_file, api_key)
    print(f"Processed text saved to {output_file}")