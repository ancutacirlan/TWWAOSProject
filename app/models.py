from sqlalchemy.orm import relationship

from app import db  # Importă instanța globală a bazei de date
from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum, Date, Table
from enum import Enum as PyEnum

# Definirea enum-urilor
class UserRole(PyEnum):
    SEC = "SEC"
    SG = "SG"
    CD = "CD"
    ADM = "ADM"

class ExamType(PyEnum):
    EXAMEN = "EXAMEN"
    COLOCVIU = "COLOCVIU"

class ExamStatus(PyEnum):
    IN_ASTEPTARE = "IN ASTEPTARE"
    ACCEPTAT = "ACCEPTAT"
    RESPINS = "RESPINS"

class User(db.Model):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)

class Group(db.Model):
    __tablename__ = "groups"
    group_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    leader_id = Column(Integer, ForeignKey("users.user_id"))

class Room(db.Model):
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
    __tablename__ = "courses"
    course_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    # Profesor coordonator (unic)
    coordinator_id = Column(Integer, ForeignKey("users.user_id"))
    coordinator = relationship("User", foreign_keys=[coordinator_id])

    # Lista de profesori asistenți (many-to-many)

    assistants = relationship("User", secondary=course_assistants, backref="assisted_courses")

class Exam(db.Model):
    __tablename__ = "exams"
    exam_id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"))
    group_id = Column(Integer, ForeignKey("groups.group_id"))
    exam_date = Column(Date, nullable=False)
    type = Column(SQLEnum(ExamType), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.room_id"))
    professor_id = Column(Integer, ForeignKey("users.user_id"))
    assistant_id = Column(Integer, ForeignKey("users.user_id"))
    status = Column(SQLEnum(ExamStatus), default=ExamStatus.IN_ASTEPTARE)
