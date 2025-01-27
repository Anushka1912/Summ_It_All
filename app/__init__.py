from flask import Flask
from app.routes import routes  # Import the blueprint from routes.py

def create_app():
    app = Flask(__name__, template_folder="templates")

    #app = Flask(__name__, template_folder="templates")  # Ensure the templates folder is correctly set
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Register the blueprint for the routes
    app.register_blueprint(routes)

    return app

