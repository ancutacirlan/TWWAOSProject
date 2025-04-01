from flask import Flask

from app.config import Config
from app.database import db, migrate
from app.import_professors import fetch_and_store_professors, fetch_and_store_rooms


def create_app():
    """Funcție de creare a aplicației Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inițializăm baza de date și Flask-Migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # Importă modelele pentru a fi vizibile în migrații
    from app.models import User, Group, Room, Course, Exam
    from app.routes.users import users_bp
    app.register_blueprint(users_bp)

    # Populăm baza de date la prima cerere către server
    @app.before_request
    def populate_db():
        fetch_and_store_professors()
        fetch_and_store_rooms()

    return app

# Creăm aplicația și legăm migrarea
app = create_app()
