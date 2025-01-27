from flask import Flask
from app.routes import routes  # Ensure this is imported only once

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'app/uploads'


# Register the blueprint (only once)
app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(debug=True)