import requests
from flask import current_app
from app.database import db
from app.models import User, UserRole, Room

API_URL_PROFESSOR = "https://orar.usv.ro/orar/vizualizare/data/cadre.php?json"
API_URL_ROOMS = "https://orar.usv.ro/orar/vizualizare/data/sali.php?json"

def fetch_and_store_professors():
    print("Fetching professors")
    """Funcție care preia cadrele didactice din API și le adaugă în baza de date."""
    response = requests.get(API_URL_PROFESSOR)
    print(response.status_code)

    if response.status_code == 200:
        professors = response.json()
        with current_app.app_context():  # Ne asigurăm că suntem în contextul Flask
            for prof in professors:
                if prof["facultyName"] == "Facultatea de Inginerie Electrică şi Ştiinţa Calculatoarelor":
                    existing_prof = User.query.filter_by(email=prof["emailAddress"]).first()
                    if not existing_prof:
                        new_professor = User(
                            name=f"{prof['firstName']} {prof['lastName']}",
                            email=prof["emailAddress"],
                            role=UserRole.CD
                        )
                        print(new_professor.name)
                        db.session.add(new_professor)
            db.session.commit()

def fetch_and_store_rooms():
    """Preia sălile din clădirile C și D și le salvează în baza de date."""
    response = requests.get(API_URL_ROOMS)
    if response.status_code == 200:
        rooms = response.json()  # Lista de săli

        with current_app.app_context():  # Ne asigurăm că suntem în contextul Flask
            for room in rooms:
                if room["buildingName"] in ["C", "D"]:  # Doar clădirile C și D
                    existing_room = Room.query.filter_by(name=room["name"]).first()
                    if not existing_room:
                        new_room = Room(
                            name=room["name"],
                            building=room["buildingName"]
                        )
                        db.session.add(new_room)
            db.session.commit()
        print("✔ Sălile au fost salvate în baza de date.")
    else:
        print("❌ Eroare la obținerea datelor:", response.status_code)