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

# Initialize summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Text summarization
def summarize_text(text, summary_type):
    max_input_length = 1024

    # Define summary length based on type
    length_options = {"short": 20, "medium": 50, "long": 100}
    length = length_options.get(summary_type, 50)  # Default to "medium"

    # Split the text into chunks
    chunks = [text[i:i + max_input_length] for i in range(0, len(text), max_input_length)]
    summaries = []

    for i, chunk in enumerate(chunks):
        try:
            summary = summarizer(chunk, max_length=length, min_length=25, do_sample=False)
            summaries.append(summary[0]['summary_text'])
            time.sleep(1)  # Avoid rate limiting
        except Exception as e:
            summaries.append(f"Error summarizing chunk {i + 1}: {e}")

    return " ".join(summaries)

# Process text file
def process_text_file(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        return file.read()

# Process PDF file
def process_pdf_file(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""  # Handle None values
    return text.strip()

# Process Word document
def process_docx_file(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

# Process image file
def process_image_file(file_path):
    return pytesseract.image_to_string(file_path)

# Load Whisper model
whisper_model = whisper.load_model("base")

# Process audio file
def process_audio_file(file_path):
    temp_audio_path = file_path.rsplit('.', 1)[0] + ".wav"

    # Convert to WAV if needed
    audio = AudioSegment.from_file(file_path)
    if len(audio) == 0:
        raise ValueError("Error: The audio file is empty.")

    if not file_path.endswith(".wav"):
        audio.export(temp_audio_path, format="wav")

    # Transcribe using Whisper
    result = whisper_model.transcribe(temp_audio_path)
    return result["text"]

# Process video file
def process_video_file(file_path):
    temp_audio_path = file_path.rsplit('.', 1)[0] + ".wav"

    # Extract audio from video
    ffmpeg.input(file_path).output(temp_audio_path, format="wav").run(overwrite_output=True, quiet=True)

    # Transcribe extracted audio
    return process_audio_file(temp_audio_path)

# General file processing function
def process_file(file_path):
    file_extension = file_path.rsplit('.', 1)[1].lower()

    if file_extension == 'txt':
        text = process_text_file(file_path)
    elif file_extension == 'pdf':
        text = process_pdf_file(file_path)
    elif file_extension == 'docx':
        text = process_docx_file(file_path)
    elif file_extension in ['jpg', 'png']:
        text = process_image_file(file_path)
    elif file_extension in ['mp4', 'mp3', 'wav']:
        text = process_audio_file(file_path)
    else:
        text = "Unsupported file type."

    return text
