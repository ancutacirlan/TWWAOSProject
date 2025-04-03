import os

from flask import current_app

from app.database import db
from app.models import User, UserRole, Course, Room

API_PROFESSORS = "https://orar.usv.ro/orar/vizualizare/data/cadre.php?json"
API_COURSES = "https://orar.usv.ro/orar/vizualizare/data/orarSPG.php?ID={}&mod=prof&json"


# def fetch_and_store_data():
#     """ Preia profesorii și cursurile asociate și le salvează în baza de date. """
#     response = requests.get(API_PROFESSORS)
#     if response.status_code != 200:
#         print("Eroare la preluarea profesorilor")
#         return
#
#     professors = response.json()
#     with current_app.app_context():
#         for prof in professors:
#             if prof["facultyName"] == os.getenv("FACULTY_NAME"):
#                 user = User.query.filter_by(email=prof["emailAddress"]).first()
#                 if not user:
#                     user = User(
#                         name=f"{prof['firstName']} {prof['lastName']}",
#                         email=prof["emailAddress"],
#                         role=UserRole.CD,
#                         teacherId=int(prof["id"])
#                     )
#                     db.session.add(user)
#                     db.session.commit()  # Salvăm profesorul în BD
#
#                 fetch_and_store_courses(user)  # Procesăm cursurile pentru fiecare profesor

def fetch_and_store_data():
    """ Preia profesorii și cursurile asociate și le salvează în baza de date. """
    response = requests.get(API_PROFESSORS)
    if response.status_code != 200:
        print("Eroare la preluarea profesorilor")
        return

    professors = response.json()
    with current_app.app_context():
        for prof in professors:
            user = User.query.filter_by(email=prof["emailAddress"]).first()
            if not user:
                user = User(
                    name=f"{prof['firstName']} {prof['lastName']}",
                    email=prof["emailAddress"],
                    role=UserRole.CD,
                    teacherId=int(prof["id"])
                )
                db.session.add(user)
                db.session.commit()  # Salvăm profesorul în BD

                fetch_and_store_courses(user)  # Procesăm cursurile pentru fiecare profesor


def extract_year_specialization(course_groups, course_id):
    """ Extrage anul și specializarea DOAR pentru cursuri (nu pentru laboratoare). """
    if course_id not in course_groups:
        return None, None  # Dacă nu există date, returnăm None

    group_info = course_groups[course_id][0]  # Exemplu: "C an 4"

    match = re.match(r"(.+)\s+an\s+(\d+)", group_info)
    if match:
        specialization, study_year = match.groups()
        return int(study_year), specialization.strip()

    return None, None  # Dacă formatul nu este valid


import requests

# def fetch_and_store_courses(professor):
#     """Preia cursurile unui profesor și le salvează în BD."""
#     response = requests.get(API_COURSES.format(professor.teacherId))
#     if response.status_code != 200:
#         print(f"Eroare la preluarea cursurilor pentru {professor.name}")
#         return
#
#     data = response.json()
#     if not data or len(data) < 2:
#         return
#
#     course_entries, course_groups = data  # Prima parte conține cursurile, a doua parte conține anii & specializările
#     course_dict = {}  # Stocăm cursurile pentru a asocia laboratoarele/seminariile
#
#     for entry in course_entries:
#         topic_name = entry.get("topicLongName")
#         type_short_name = entry.get("typeShortName")
#
#         # Ignorăm cursurile fără nume sau fără tip valid
#         if not topic_name or type_short_name in [None, "pr"]:
#             print(f"⚠️ Curs ignorat ({'fără nume' if not topic_name else type_short_name}) pentru {professor.name}")
#             continue
#
#         # Extragem anul și specializarea, verificând facultatea FIESC
#         study_year, specialization = extract_year_specialization_from_pair(course_groups, entry["id"])
#         if study_year is None or specialization is None:
#             print(f"⚠️ Curs ignorat (nu este de la FIESC): {topic_name}")
#             continue
#
#         # Creăm cheia unică pentru curs
#         course_key = (topic_name, study_year, specialization)
#
#         # Căutăm cursul în BD sau îl creăm dacă nu există
#         if course_key in course_dict:
#             course = course_dict[course_key]
#         else:
#             course = Course.query.filter_by(
#                 name=topic_name,
#                 studyYear=study_year,
#                 specialization=specialization
#             ).first()
#
#             if not course:
#                 course = Course(
#                     name=topic_name,
#                     studyYear=study_year,
#                     specialization=specialization,
#                     coordinator_id=None  # Va fi actualizat ulterior
#                 )
#                 db.session.add(course)
#
#             course_dict[course_key] = course  # Stocăm cursul în dicționar
#
#         # Asociem profesorii în funcție de tipul activității
#         if type_short_name in ["curs", "sem"]:
#             course.coordinator_id = professor.user_id  # Profesorul devine coordonator
#         elif type_short_name == "lab":
#             if professor not in course.assistants:
#                 course.assistants.append(professor)  # Profesorul devine asistent
#
#     db.session.commit()

def fetch_and_store_courses(professor):
    """Preia cursurile unui profesor și le salvează în BD pentru toate facultățile."""
    response = requests.get(API_COURSES.format(professor.teacherId))
    if response.status_code != 200:
        print(f"Eroare la preluarea cursurilor pentru {professor.name}")
        return

    data = response.json()
    if not data or len(data) < 2:
        return

    course_entries, course_groups = data  # Prima parte conține cursurile, a doua parte conține anii & specializările
    course_dict = {}  # Stocăm cursurile pentru a asocia laboratoarele/seminariile

    for entry in course_entries:
        topic_name = entry.get("topicLongName")
        type_short_name = entry.get("typeShortName")

        # Preluăm sau creăm sala doar dacă roomLongName nu este null
        if entry.get("roomLongName"):
            room = Room.query.filter_by(name=entry["roomLongName"]).first()
            if not room:
                room = Room(name=entry["roomLongName"], building=entry.get("roomBuilding"))
                db.session.add(room)

        # Ignorăm cursurile fără nume sau de tip "pr"
        if not topic_name or type_short_name in [None, "pr"]:
            print(f"⚠️ Curs ignorat ({'fără nume' if not topic_name else type_short_name}) pentru {professor.name} - {professor.teacherId}")
            continue

        # Extragem anul și specializarea
        study_year, specialization, faculty = extract_year_specialization_from_pair(course_groups, entry["id"])

        # Creăm cheia unică pentru curs
        course_key = (topic_name, study_year, specialization)

        # Căutăm cursul în BD sau îl creăm dacă nu există
        if course_key in course_dict:
            course = course_dict[course_key]
        else:
            course = Course.query.filter_by(
                name=topic_name,
                studyYear=study_year,
                specialization=specialization
            ).first()

            if not course:
                course = Course(
                    name=topic_name,
                    studyYear=study_year,
                    specialization=specialization,
                    coordinator_id=None,  # Va fi actualizat ulterior
                    facultyShortName=faculty
                )
                db.session.add(course)

            course_dict[course_key] = course  # Stocăm cursul în dicționar

        # Asociem profesorii în funcție de tipul activității
        if type_short_name == "curs":
            course.coordinator_id = professor.user_id  # Profesorul devine coordonator
        elif type_short_name in ["lab", "sem"]:
            if professor not in course.assistants:
                course.assistants.append(professor)  # Profesorul devine asistent

    db.session.commit()



import re

def extract_year_specialization_from_pair(course_groups, course_id):
    """
    Extrage anul, specializarea și facultatea din pereche.
    Suportă ambele formate de date:
      - ["KMS an 2", "FEFS"]
      - ["1117a", "FEFS,KMS an 1"]
    """
    pair = course_groups.get(str(course_id))  # Găsim perechea pentru ID-ul cursului
    if not pair or len(pair) < 2:
        return None, None, None  # Dacă nu avem date, returnăm None

    faculty_info = pair[1]  # Al doilea element conține facultatea și uneori specializarea
    faculties = faculty_info.split(",")  # Poate conține mai multe facultăți
    faculty = faculties[0].strip()  # Prima facultate

    # Verificăm unde apare "an X"
    specialization_part = pair[0] if "an" in pair[0] else pair[1]

    # Extragem specializarea și anul
    match = re.search(r"(.+)\s+an\s+(\d+)", specialization_part)
    if match:
        specialization = match.group(1).split(",")[-1].strip()  # Ultima specializare
        year = int(match.group(2))  # Anul ca număr întreg
        return year, specialization, faculty

    return None, None, None

# def extract_year_specialization_from_pair(course_groups, course_id):
#     """
#     Extrage anul și specializarea doar dacă facultatea este FIESC.
#     - Caută "FIESC" în al doilea element al perechii.
#     - Dacă nu există, returnează None (ignorăm cursul).
#     """
#     pair = course_groups.get(str(course_id))  # Găsim perechea pentru ID-ul cursului
#     if not pair or len(pair) < 2:
#         return None, None  # Dacă nu avem date, returnăm None
#
#     # faculty_info = pair[1]  # Verificăm facultatea
#
#     # if "FIESC" not in faculty_info:
#     #     return None, None  # Dacă nu e de la FIESC, îl ignorăm
#
#     specialization_part = None
#     year = None
#
#     # Verificăm unde apare "an X"
#     if "an" in pair[0]:
#         specialization_part = pair[0]  # Ex: "SIC an 1"
#     else:
#         specialization_part = pair[1]  # Ex: "FIESC, SIC an 1"
#
#     # Extragem specializarea și anul
#     match = re.search(r"(.+)\s+an\s+(\d+)", specialization_part)
#     if match:
#         specialization = match.group(1).split(",")[-1].strip()  # Ultima specializare
#         year = int(match.group(2))  # Anul ca număr întreg
#         return year, specialization
#
#     return None, None

