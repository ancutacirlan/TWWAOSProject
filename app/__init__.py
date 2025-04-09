import app
from flasgger import Swagger
from flask import Flask
from flask_login import LoginManager

from app.config import Config
from app.database import db, migrate
from app.models import User
from app.routes.import_from_excel import upload_bp
from app.routes.auth import init_oauth, auth_bp
from app.routes.settings import settings_bp
from app.routes.users import users_bp

login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    """Funcție de creare a aplicației Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "My API",
            "description": "Documentație pentru API-ul aplicației",
            "version": "1.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Introdu Bearer <token> pentru autentificare"
            }
        }
    }
    Swagger(app, template=swagger_template)

    # Inițializăm baza de date și Flask-Migrate
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    init_oauth(app)

    # Importă modelele pentru a fi vizibile în migrații

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(settings_bp)



    return app

# Creăm aplicația și legăm migrarea
app = create_app()
