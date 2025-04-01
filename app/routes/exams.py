from flask import Blueprint, jsonify
from app.models import Exam

exams_bp = Blueprint("exams", __name__, url_prefix="/exams")

@exams_bp.route("/", methods=["GET"])
def get_exams():
    exams = Exam.query.all()
    return jsonify([{"id": exam.id, "date": exam.date.strftime("%Y-%m-%d")} for exam in exams])
