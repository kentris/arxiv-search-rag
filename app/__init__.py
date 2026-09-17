from flask import Flask
from flask_cors import CORS
from config import Config
from app.search import PaperSearcher

searcher = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for all routes (or restrict origins in production)
    CORS(app)

    global searcher
    searcher = PaperSearcher(app.config["VECTORIZER_PATH"])

    from app.routes import main
    app.register_blueprint(main)

    return app