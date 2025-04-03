from flask import Flask
from flask_login import LoginManager

from app.config import Config
from app.database import db, migrate
from app.routes.auth import init_oauth, auth_bp

login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    """Funcție de creare a aplicației Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inițializăm baza de date și Flask-Migrate
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    init_oauth(app)

    # Importă modelele pentru a fi vizibile în migrații
    from app.models import User, Group, Room, Course, Exam
    from app.routes.users import users_bp
    app.register_blueprint(users_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)

    return app

# Creăm aplicația și legăm migrarea
app = create_app()
