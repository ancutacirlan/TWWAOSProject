import os

from flasgger import swag_from
from flask import Blueprint, redirect, url_for, session, flash
from authlib.integrations.flask_client import OAuth
from flask_login import login_user, logout_user, login_required
from app.models import User

auth_bp = Blueprint("auth", __name__)
oauth = OAuth()

def init_oauth(app):
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        access_token_url="https://oauth2.googleapis.com/token",
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        authorize_params={"scope": "openid email profile"},
        jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
        client_kwargs={"scope": "openid email profile"},
    )

@auth_bp.route("/login")
@swag_from({
    'tags': ['Autentificare'],
    'summary': 'Login Google',
    'description': 'Redirecționează utilizatorul către autentificarea Google.',
    'responses': {
        302: {
            'description': 'Redirecționare către Google pentru autentificare.'
        }
    }
})
def login():
    session["nonce"] = os.urandom(16).hex()  # Generăm un nonce aleatoriu
    return oauth.google.authorize_redirect(url_for("auth.callback", _external=True))

@auth_bp.route("/login/callback")
@swag_from({
    'tags': ['Autentificare'],
    'summary': 'Callback după login',
    'description': 'Primește tokenul de la Google, verifică emailul și loghează utilizatorul dacă există în baza de date.',
    'responses': {
        302: {
            'description': 'Redirecționare către pagina de succes sau eroare.'
        }
    }
})
def callback():
    token = oauth.google.authorize_access_token()
    print(token)

    # În loc de parse_id_token(), folosim userinfo()
    user_info = oauth.google.get("https://www.googleapis.com/oauth2/v3/userinfo").json()

    if not user_info:
        flash("Eroare la autentificare", "danger")
        return redirect(url_for("index"))

    email = user_info["email"]
    print(email)
    user = User.query.filter_by(email=email).first()
    print(user.role)

    if user:
        login_user(user)
        session["profile"] = user_info
        flash("Autentificare reușită!", "success")
        return redirect(url_for("users.get_login"))

    flash("Nu ai acces. Contactează administratorul.", "danger")
    return redirect(url_for("users.get_fail"))

@auth_bp.route("/logout")
@login_required
@swag_from({
    'tags': ['Autentificare'],
    'summary': 'Logout',
    'description': 'Deconectează utilizatorul curent și șterge sesiunea.',
    'responses': {
        302: {
            'description': 'Redirecționare după logout.'
        }
    }
})
def logout():
    logout_user()
    session.pop("profile", None)
    flash("Te-ai deconectat cu succes.", "info")
    return redirect(url_for("users.get_logout"))
