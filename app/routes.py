import os
from flask import request, render_template, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from app.utils import process_file, summarize_text
from flask import Blueprint
from flask import current_app



print(f"Templates folder path: {os.path.join(os.getcwd(), 'app/templates')}")
print(f"Templates folder exists? {os.path.exists(os.path.join(os.getcwd(), 'app/templates'))}")

print("Current Working Directory:", os.getcwd())


routes = Blueprint('routes', __name__, template_folder='templates', static_folder='static')




ALLOWED_EXTENSIONS = {'mp4', 'mp3', 'wav', 'jpg', 'png', 'pdf', 'docx', 'txt', 'html'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@routes.route('/')
def home():
    print("Current Working Directory:", os.getcwd())
    print("Rendering upload.html...")
    return render_template('upload.html')


@routes.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded.", 400

    file = request.files['file']
    summary_type = request.form.get('summary_type')  # Get summary type from form

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # Save the uploaded file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Extract text from the file
        extracted_text = process_file(file_path)

        # Generate summary using the extracted text
        if extracted_text:
            summary = summarize_text(extracted_text, summary_type)
        else:
            summary = "Unable to extract text from the file."

        # Render results.html with the extracted text and summary
        return render_template('results.html', text=extracted_text, summary=summary, summary_type=summary_type)
    else:
        return "Invalid file type.", 400

    if 'file' not in request.files:
        return "No file uploaded.", 400

    file = request.files['file']
    summary_type = request.form.get('summary_type')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Use current_app inside the route where context is available
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process file and get results
        extracted_text = process_file(file_path)

        # Debugging: Check if results.html exists
        template_path = os.path.join(os.getcwd(), "app/templates/results.html")
        print(f"Checking if template exists: {template_path}")
        print(f"File exists? {os.path.exists(template_path)}")
        return render_template('results.html', text=extracted_text, summary_type=summary_type)
    else:
        return "Invalid file type.", 400