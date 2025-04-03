import os
import yt_dlp
import whisper
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Check if API key is loaded
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Make sure it's set in the .env file.")

# Set FFmpeg path
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\ffmpeg-master-latest-win64-gpl\bin"

def download_audio(youtube_url, output_path="audio.mp3"):
    """Download YouTube video audio."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

def transcribe_audio(audio_path):
    """Transcribe audio using Whisper."""
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

def summarize_text(text):
    """Summarize key topics and generate a headline using GPT-4."""
    prompt = (
        "Analyze the following podcast transcript and generate:\n"
        "- A concise summary of key topics.\n"
        "- A compelling headline for an article based on the discussion.\n\n"
        "Transcript:\n" + text[:4000]  # Limit to avoid token overflow
    )
    
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert journalist."},
            {"role": "user", "content": prompt}
        ]
    )

    output = response.choices[0].message.content.strip()
    
    # Extract headline and summary safely
    lines = output.split("\n")
    headline, summary = "Unknown Headline", "No summary available."
    
    for line in lines:
        if line.startswith("HEADLINE:"):
            headline = line.replace("HEADLINE:", "").strip()
        elif line.startswith("SUMMARY:"):
            summary = line.replace("SUMMARY:", "").strip()
    
    return headline, summary

def save_as_txt(headline, summary, transcript):
    """Save formatted text to files."""
    with open("article.txt", "w", encoding="utf-8") as f:
        f.write(f"{headline}\n\n{summary}\n\n---\n\n{transcript}")
    
    with open("transcript.txt", "w", encoding="utf-8") as f:
        f.write(transcript)

def main():
    youtube_url = input("Enter YouTube video URL: ")
    audio_path = "audio.mp3"

    print("Downloading audio...")
    download_audio(youtube_url, audio_path)

    print("Transcribing audio...")
    transcript = transcribe_audio(audio_path)

    print("Generating summary and headline...")
    headline, summary = summarize_text(transcript)

    print("Saving to text files...")
    save_as_txt(headline, summary, transcript)

    print("Done! The article is saved as 'article.txt', and the full transcript is saved as 'transcript.txt'.")

if __name__ == "__main__":
    main()
