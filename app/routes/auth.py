import os

from flasgger import swag_from
from flask import Blueprint, request, jsonify, session, redirect, url_for, current_app
from authlib.integrations.flask_client import OAuth
from flask_jwt_extended import create_access_token

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
    session["nonce"] = os.urandom(16).hex()
    print(current_app.config["GOOGLE_REDIRECT_URI"])
    return oauth.google.authorize_redirect(current_app.config["GOOGLE_REDIRECT_URI"])


@auth_bp.route("/auth/callback")
@swag_from({
    'tags': ['Autentificare'],
    'summary': 'Callback după login',
    'description': 'Primește tokenul de la Google, verifică emailul și loghează utilizatorul dacă există în baza de date.',
    'responses': {
        200: {
            'description': 'Token de acces JWT trimis utilizatorului.'
        },
        403: {
            'description': 'Acces refuzat. Utilizatorul nu are permisiune.'
        }
    }
})
def callback():
    # Schimbăm codul de autorizare pentru un token de acces
    token = oauth.google.authorize_access_token()

    # Obținem informațiile despre utilizator
    user_info = oauth.google.get("https://www.googleapis.com/oauth2/v3/userinfo").json()

    if not user_info:
        return jsonify({"error": "Nu s-au putut obține informațiile utilizatorului."}), 400

    email = user_info["email"]
    user = User.query.filter_by(email=email).first()

    if user:
        # Creăm tokenul JWT pentru utilizator
        access_token = create_access_token(
            identity=str(user.user_id),
            additional_claims={"role": user.role.value}
        )
        return jsonify(access_token=access_token), 200

    return jsonify({"error": "Nu ai acces. Contactează administratorul."}), 403


@auth_bp.route("/logout")
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
    # Închide sesiunea utilizatorului
    session.pop("profile", None)
    return redirect(url_for("login"))