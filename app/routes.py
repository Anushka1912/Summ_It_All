import requests
from flask import request, render_template, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from app.utils import process_file, summarize_text, download_file_from_url, is_youtube_link, process_youtube_audio
from flask import Blueprint, current_app
import os

routes = Blueprint('routes', __name__, template_folder='templates', static_folder='static')

ALLOWED_EXTENSIONS = {'mp4', 'mp3', 'wav', 'jpg', 'png', 'pdf', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@routes.route('/')
def home():
    return render_template('upload.html')

@routes.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    link = request.form.get('link')
    summary_type = request.form.get('summary_type')

    extracted_text = None

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        extracted_text = process_file(file_path)

    elif link:
        if is_youtube_link(link):
            extracted_text = process_youtube_audio(link, current_app.config['UPLOAD_FOLDER'])
        else:
            file_path = download_file_from_url(link, current_app.config['UPLOAD_FOLDER'])
            if file_path and allowed_file(file_path.rsplit('.', 1)[-1]):
                extracted_text = process_file(file_path)
            else:
                if file_path:
                    os.remove(file_path)  # Delete invalid downloaded files
                return "Unsupported file type or invalid link.", 400

    else:
        return "No file or valid link provided.", 400

    # Generate summary
    summary = summarize_text(extracted_text, summary_type) if extracted_text else "Unable to extract text from the file or link."

    return render_template('results.html', text=extracted_text, summary=summary, summary_type=summary_type)
