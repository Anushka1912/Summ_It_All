import os
import ffmpeg
import whisper
import torch
from pydub import AudioSegment
import pytesseract
import pdfplumber
from docx import Document
import pandas as pd
from transformers import pipeline
import time
import requests
from werkzeug.utils import secure_filename
import subprocess
from pdf2image import convert_from_path


# Initialize summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Define max input length for text summarization
MAX_INPUT_LENGTH = 1024

# Define summary lengths based on type
SUMMARY_LENGTHS = {"short": 20, "medium": 50, "long": 100}


def summarize_text(text, summary_type="medium"):
    """
    Summarizes the given text based on the selected summary type.
    """
    length = SUMMARY_LENGTHS.get(summary_type, 50)
    chunks = [text[i:i + MAX_INPUT_LENGTH] for i in range(0, len(text), MAX_INPUT_LENGTH)]
    summaries = []

    for i, chunk in enumerate(chunks):
        try:
            summary = summarizer(chunk, max_length=length, min_length=25, do_sample=False)
            summaries.append(summary[0]['summary_text'])
            time.sleep(1)  # Avoid rate limiting
        except Exception as e:
            summaries.append(f"Error summarizing chunk {i + 1}: {e}")

    return " ".join(summaries)


def process_text_file(file_path):
    """Reads a text file and returns its content."""
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            return file.read().strip()
    except Exception as e:
        return f"Error processing text file: {e}"


def process_pdf_file(file_path):
    """Extracts text from a PDF file."""
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        
        # Use OCR as fallback for image-based PDFs
        if not text.strip():
            images = convert_from_path(file_path)
            for img in images:
                text += pytesseract.image_to_string(img)
        
        return text.strip()
    except Exception as e:
        return f"Error processing PDF file: {e}"


def process_docx_file(file_path):
    """Extracts text from a Word document."""
    try:
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs]).strip()
    except Exception as e:
        return f"Error processing DOCX file: {e}"


def process_image_file(file_path):
    """Extracts text from an image using OCR."""
    try:
        return pytesseract.image_to_string(file_path).strip()
    except Exception as e:
        return f"Error processing image file: {e}"


# Load Whisper model
whisper_model = whisper.load_model("base")


def process_audio_file(file_path):
    """Processes audio files, converts to WAV if needed, and transcribes using Whisper."""
    try:
        temp_audio_path = file_path.rsplit('.', 1)[0] + ".wav"

        # Convert to WAV if necessary
        audio = AudioSegment.from_file(file_path)
        if len(audio) == 0:
            return "Error: The audio file is empty."

        if not file_path.endswith(".wav"):
            audio.export(temp_audio_path, format="wav")

        # Transcribe using Whisper
        result = whisper_model.transcribe(temp_audio_path)
        return result["text"].strip()
    except Exception as e:
        return f"Error processing audio file: {e}"


def process_video_file(file_path):
    """Extracts audio from a video file and transcribes it using Whisper."""
    try:
        temp_audio_path = file_path.rsplit('.', 1)[0] + ".wav"

        # Extract audio from video
        ffmpeg.input(file_path).output(temp_audio_path, format="wav").run(overwrite_output=True, quiet=True)

        # Transcribe extracted audio
        return process_audio_file(temp_audio_path)
    except Exception as e:
        return f"Error processing video file: {e}"


def process_file(file_path):
    """
    Determines the file type and processes it accordingly.
    """
    try:
        file_extension = file_path.rsplit('.', 1)[-1].lower()

        if file_extension == 'txt':
            return process_text_file(file_path)
        elif file_extension == 'pdf':
            return process_pdf_file(file_path)
        elif file_extension == 'docx':
            return process_docx_file(file_path)
        elif file_extension in ['jpg', 'png']:
            return process_image_file(file_path)
        elif file_extension in ['mp4', 'mp3', 'wav']:
            return process_audio_file(file_path) if file_extension != 'mp4' else process_video_file(file_path)
        else:
            return "Error: Unsupported file type."
    except Exception as e:
        return f"Error processing file: {e}"


def download_file_from_url(url, save_folder):
    """
    Downloads a file from a given URL and saves it in the specified folder.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        # Extract file name from URL and create a secure filename
        filename = secure_filename(url.split("/")[-1])
        file_path = os.path.join(save_folder, filename)

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        return file_path if os.path.exists(file_path) else None
    except Exception as e:
        print(f"Error downloading file from URL: {e}")
        return None


def is_youtube_link(url):
    """
    Checks if the given URL is a valid YouTube link.
    """
    return "youtube.com/watch" in url or "youtu.be/" in url


def process_youtube_audio(url, save_folder):
    """
    Downloads and processes audio from a YouTube video using yt-dlp.
    """
    try:
        output_path = os.path.join(save_folder, "youtube_audio.mp3")
        command = f'yt-dlp -x --audio-format mp3 -o "{output_path}" "{url}"'
        subprocess.run(command, shell=True, check=True)

        if os.path.exists(output_path):
            return process_audio_file(output_path)
        else:
            return "Error: Failed to download YouTube audio."
    except Exception as e:
        return f"Error processing YouTube audio: {e}"
