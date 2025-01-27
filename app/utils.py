import os
#import ffmpeg
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
    # Define the maximum input length for BART (1024 tokens)
    max_input_length = 1024

    # Adjust the maximum length of the summary based on the type
    if summary_type == "short":
        length = 20  # Adjust as needed
    elif summary_type == "medium":
        length = 50  # Adjust as needed
    elif summary_type == "long":
        length = 100  # Adjust as needed
    else:
        length = 50  # Default

    # Split the text into chunks
    chunks = [text[i:i + max_input_length] for i in range(0, len(text), max_input_length)]
    summaries = []

    for i, chunk in enumerate(chunks):
        try:
            # Summarize the chunk
            summary = summarizer(chunk, max_length=length, min_length=25, do_sample=False)
            summaries.append(summary[0]['summary_text'])

            # Introduce a delay to avoid rate limiting
            time.sleep(1)  # Adjust the delay as needed

        except Exception as e:
            summaries.append(f"Error summarizing chunk {i + 1}: {e}")

    # Combine all chunk summaries
    final_summary = " ".join(summaries)
    return final_summary

# Process text file
def process_text_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Process PDF file
def process_pdf_file(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Process Word document
def process_docx_file(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

# Process image file
def process_image_file(file_path):
    return pytesseract.image_to_string(file_path)
'''
# Process video/audio file
def process_audio_file(file_path):
    temp_audio_path = file_path + ".wav"
    ffmpeg.input(file_path).output(temp_audio_path).run(overwrite_output=True)
    # Add Whisper/Vosk transcription logic here (placeholder below)
    return "Transcription of audio/video not implemented yet."
'''
# General file processing function
def process_file(file_path):
    file_extension = file_path.rsplit('.', 1)[1].lower()

    if file_extension in ['txt']:
        text = process_text_file(file_path)
    elif file_extension in ['pdf']:
        text = process_pdf_file(file_path)
    elif file_extension in ['docx']:
        text = process_docx_file(file_path)
    elif file_extension in ['jpg', 'png']:
        text = process_image_file(file_path)
    elif file_extension in ['mp4', 'mp3', 'wav']:
        text = process_audio_file(file_path)
    else:
        text = "Unsupported file type."

    return text
