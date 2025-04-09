from sqlalchemy.orm import relationship, validates

from app import db  # Importă instanța globală a bazei de date
from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum, Date, Table
from enum import Enum as PyEnum

# Definirea enum-urilor
class UserRole(PyEnum):
    """
      Definirea rolurilor utilizatorilor.

      Această enum reprezintă rolurile posibile pentru un utilizator în aplicație.
      - SEC: Student la secția de examene
      - SG: Student grup
      - CD: Coordonator de curs
      - ADM: Administrator

      Exemple de utilizare:
          - UserRole.SEC: Rolul de Student la examene.
      """
    SEC = "SEC"
    SG = "SG"
    CD = "CD"
    ADM = "ADM"

class ExamType(PyEnum):
    """
       Definirea tipurilor de examene.

       Enum care specifică tipul examenului.
       - EXAMEN: Un examen propriu-zis.
       - COLOCVIU: Colocviu.

       Exemple de utilizare:
           - ExamType.EXAMEN: Tipul examenului propriu-zis.
       """
    EXAMEN = "EXAMEN"
    COLOCVIU = "COLOCVIU"

exam_type_enum = db.Enum("EXAMEN", "COLOCVIU", name="examtype", create_type=False)


class ExamStatus(PyEnum):
    """
       Definirea statusului examenelor.

       Aceasta enum reprezintă statusul unui examen.
       - IN_ASTEPTARE: Examenul așteaptă să fie programat.
       - ACCEPTAT: Examenul a fost acceptat.
       - RESPINS: Examenul a fost respins.

       Exemple de utilizare:
           - ExamStatus.IN_ASTEPTARE: Statusul examenului care așteaptă să fie evaluat.
       """
    IN_ASTEPTARE = "IN ASTEPTARE"
    ACCEPTAT = "ACCEPTAT"
    RESPINS = "RESPINS"

class User(db.Model):
    """
      Modelul pentru utilizatorii aplicației.

      Această clasă reprezintă un utilizator în sistemul de autentificare.
      Fiecare utilizator are un ID unic, un nume, un email, un rol (rolul poate fi unul dintre UserRole), și un teacherId (pentru rolul CD).

      Atribute:
          user_id (int): ID-ul unic al utilizatorului.
          name (str): Numele complet al utilizatorului.
          email (str): Adresa de email unică a utilizatorului.
          role (UserRole): Rolul utilizatorului (ex: Student, Coordonator, etc.).
          teacherId (int, optional): ID-ul profesorului asociat, necesar pentru rolul CD.

      Metode:
          get_id: Returnează ID-ul utilizatorului ca un șir de caractere.
          is_active: Verifică dacă utilizatorul este activ (returnează True).
          is_authenticated: Verifică dacă utilizatorul este autentificat (returnează True).
          is_anonymous: Verifică dacă utilizatorul este anonim (returnează False).
      """
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    teacherId = Column(Integer, nullable=True)


    @validates("teacherId")
    def validate_fields(self, key, value):
        """
        Validăm că teacherId nu poate fi NULL pentru rolul CD.
        """
        if self.role == UserRole.CD and key == "teacherId" and value is None:
            raise ValueError("teacherId nu poate fi NULL pentru un utilizator cu rolul CD.")
        return value

    def get_id(self):
        """Returnează ID-ul utilizatorului ca un șir de caractere."""
        return str(self.user_id)

    @property
    def is_active(self):
        """Verifică dacă utilizatorul este activ."""
        return True

    @property
    def is_authenticated(self):
        """Verifică dacă utilizatorul este autentificat."""
        return True

    @property
    def is_anonymous(self):
        """Verifică dacă utilizatorul este anonim."""
        return False

class Group(db.Model):
    """
     Modelul pentru grupurile de studenți.

     Această clasă reprezintă un grup de studenți dintr-o anumită specializare și an de studiu. Fiecare grup are un lider care este un utilizator din baza de date.

     Atribute:
         group_id (int): ID-ul unic al grupului.
         name (str): Numele grupului (unic).
         leader_id (int): ID-ul liderului grupului, un utilizator.
         specialization (str, optional): Specializarea grupului.
         year_of_study (int, optional): Anul de studiu al grupului.
     """
    __tablename__ = "groups"
    group_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    leader_id = Column(Integer, ForeignKey("users.user_id"))

    specialization = Column(String, nullable=True)
    year_of_study = Column(Integer, nullable=True)


class Room(db.Model):
    """
    Modelul pentru săli de examen.

    Această clasă reprezintă o sală unde pot avea loc examenele sau alte activități din cadrul aplicației. Fiecare sală are un ID unic, un nume și o locație (clădire).

    Atribute:
        room_id (int): ID-ul unic al sălii.
        name (str): Numele sălii (de exemplu, "Sala 101").
        building (str): Clădirea în care se află sala (de exemplu, "Clădirea A").

    Exemple de utilizare:
        - O sală poate fi atribuită unui examen folosind `room_id` în clasa `Exam`.
    """
    __tablename__ = "rooms"
    room_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    building = Column(String, nullable=False)

    # Tabel intermediar pentru relația many-to-many dintre cursuri și asistenți
course_assistants = Table(
    "course_assistants",
    db.Model.metadata,
    Column("course_id", Integer, ForeignKey("courses.course_id"), primary_key=True),
    Column("assistant_id", Integer, ForeignKey("users.user_id"), primary_key=True),
    )

class Course(db.Model):
    """
     Modelul pentru cursuri.

     Această clasă reprezintă un curs disponibil în cadrul aplicației. Fiecare curs are un coordonator (profesor) și un grup de asistenți. Cursul este asociat cu un anumit an de studiu și o specializare.

     Atribute:
         course_id (int): ID-ul unic al cursului.
         name (str): Numele cursului.
         studyYear (int, optional): Anul de studiu al cursului.
         specialization (str, optional): Specializarea cursului.
         coordinator_id (int): ID-ul profesorului coordonator al cursului.

     Relații:
         coordinator (User): Profesorul coordonator al cursului.
         assistants (User): Lista de asistenți ai cursului.
     """
    __tablename__ = "courses"
    course_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    studyYear = Column(Integer, nullable=True)
    specialization = Column(String, nullable=True)
    # Profesor coordonator (unic)
    coordinator_id = Column(Integer, ForeignKey("users.user_id"))

    coordinator = relationship("User", foreign_keys=[coordinator_id])

    # Lista de profesori asistenți (many-to-many)

    assistants = relationship("User", secondary=course_assistants, backref="assisted_courses")

class Exam(db.Model):
    """
       Modelul pentru examene.

       Această clasă reprezintă un examen asociat unui curs, unui grup de studenți și unei săli. Examenele pot avea diferite tipuri și statusuri, iar fiecare examen este asociat unui profesor și unui asistent.

       Atribute:
           exam_id (int): ID-ul unic al examenului.
           course_id (int): ID-ul cursului asociat examenului.
           group_id (int): ID-ul grupului de studenți pentru examen.
           exam_date (Date): Data examenului.
           type (ExamType): Tipul examenului (examen sau colocviu).
           room_id (int): ID-ul sălii de examen.
           professor_id (int): ID-ul profesorului care administrează examenul.
           assistant_id (int): ID-ul asistentului pentru examen.
           status (ExamStatus): Statusul examenului (ex: în așteptare, acceptat, respins).
       """
    __tablename__ = "exams"
    exam_id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"))
    group_id = Column(Integer, ForeignKey("groups.group_id"))
    exam_date = Column(Date, nullable=False)
    type = Column(exam_type_enum, nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.room_id"))
    professor_id = Column(Integer, ForeignKey("users.user_id"))
    assistant_id = Column(Integer, ForeignKey("users.user_id"))
    status = Column(SQLEnum(ExamStatus), default=ExamStatus.IN_ASTEPTARE)

class ExaminationPeriod(db.Model):
    """
       Modelul pentru perioada de examinare.

       Această clasă reprezintă o perioadă în care se desfășoară examenele sau colocviile. Fiecare perioadă are un ID unic, un nume (de exemplu, "Perioada de examene iarnă 2025") și datele de început și sfârșit.

       Atribute:
           examination_period_id (int): ID-ul unic al perioadei de examinare.
           name (str): Numele perioadei de examinare (de exemplu, "Examene iarnă 2025").
           period_start (Date): Data de început a perioadei de examinare.
           period_end (Date): Data de sfârșit a perioadei de examinare.

       Exemple de utilizare:
           - Perioadele de examinare pot fi folosite pentru a programa examenele.
       """
    __tablename__ = "examination_period"

    examination_period_id = Column(Integer, primary_key=True)
    name = Column(exam_type_enum, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)


