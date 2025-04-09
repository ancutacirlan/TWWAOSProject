import os

import pandas as pd
from flasgger import swag_from
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from app.decorators import roles_required
from app.models import db, User, UserRole, Group

upload_bp = Blueprint("upload", __name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"xlsx"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/upload-users", methods=["POST"])
@roles_required(UserRole.ADM, UserRole.SEC)
@swag_from({
    'tags': ['Upload'],
    "summary": "Încarcă un fișier Excel cu utilizatori.",
    "description": "    Încarcă un fișier Excel cu utilizatori.",
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'Fișier Excel .xlsx'
        }
    ],
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'Fișier procesat cu succes.'
        },
        401: {
            'description': 'Autentificare necesară.'
        },
        403: {
            'description': 'Acces interzis. Rol insuficient.'
        }
    }
})
def upload_users():
    if "file" not in request.files:
        return jsonify({"error": "Niciun fișier trimis"}), 400

    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Fișier invalid. Trimite un fișier Excel (.xlsx)"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    try:
        df = pd.read_excel(file_path)

        # Coloanele necesare
        required_columns = {"name", "email", "role", "groupName", "specialization", "year_of_study", "teacherId"}
        if not required_columns.issubset(df.columns):
            return jsonify({"error": "Fișierul trebuie să conțină: name, email, role, groupName, specialization, year_of_study, teacherId"}), 400

        users_added = 0
        for _, row in df.iterrows():
            if pd.isna(row["name"]) or pd.isna(row["email"]):
                continue

            # Verificăm dacă utilizatorul există deja
            existing_user = User.query.filter_by(email=row["email"]).first()
            if not existing_user:
                user = User(
                    name=row["name"],
                    email=row["email"],
                    role=row["role"],
                    teacherId=int(row["teacherId"]) if not pd.isna(row["teacherId"]) else None
                )
                db.session.add(user)

                # Dacă utilizatorul este SG, creăm și grupa aferentă
                if row["role"] == "SG":  # Sau UserRole.SEC, depinde de definirea rolului
                    # Asigură-te că groupName este tratat ca un șir de caractere
                    group_name = str(row["groupName"])  # Convertește groupName într-un șir de caractere

                    # Verificăm dacă grupa există deja
                    existing_group = Group.query.filter_by(name=group_name).first()

                    if not existing_group:
                        # Dacă grupa nu există, creăm o nouă grupă
                        group = Group(
                            name=group_name,
                            specialization=row["specialization"],
                            year_of_study=row["year_of_study"],
                            leader_id=user.user_id  # Setăm utilizatorul ca lider
                        )
                        db.session.add(group)
                        db.session.commit()  # Este important să facem commit pentru a salva grupa în BD

                    #     # După ce grupa este salvată, actualizăm group_id pentru utilizator
                    #     user.group_id = group.group_id
                    # else:
                    #     # Dacă există deja grupa, o asociem utilizatorului
                    #     user.group_id = existing_group.group_id

                    users_added += 1  # Incrementăm contorul pentru utilizatori adăugați

        db.session.commit()
        return jsonify({"message": f"{users_added} utilizatori adăugați cu succes"}), 201

    except Exception as e:
        return jsonify({"error": f"Eroare la procesarea fișierului: {str(e)}"}), 500

