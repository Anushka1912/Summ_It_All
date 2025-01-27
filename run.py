from flask import Flask
from app.routes import routes
import os  # Ensure this is imported only once

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'app/uploads')


# Register the blueprint (only once)
app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(debug=True)