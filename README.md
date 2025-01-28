# Summ-It-All

**Summ It All** is a Python-based text summarization tool that allows you to generate concise summaries from various data formats, including documents, audio, and video. The project leverages the Hugging Face Transformers library for summarization and supports customization of summary lengths (short, medium, and long). It also provides chunking mechanisms to handle large input data seamlessly.

---

## Features

- **Supports Multiple Data Formats**:
  - Documents (e.g., PDF, Word, TXT)
  - Audio (e.g., MP3, WAV)
  - Video (e.g., MP4, AVI)
  - Image (e.g., PNG, JPG)
- **Customizable Summary Lengths**:
  - Short
  - Medium
  - Long
- **Handles Large Inputs**:
  - Automatically chunks input text exceeding model limits.
  - Introduces delays to manage rate limits.
- **Integrated Web Interface**:
  - Upload files directly through a web app.
  - View generated summaries in real-time.

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/summ-it-all.git
   cd summ-it-all
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate  # For Windows
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## Installation

Install ffmpeg

---

## Usage

### Run the Web Application

1. Start the Flask server:

   ```bash
   python run.py
   ```

2. Open your web browser and navigate to:

   ```
   http://127.0.0.1:5000
   ```
---

## Acknowledgments

- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [Flask](https://flask.palletsprojects.com/)

