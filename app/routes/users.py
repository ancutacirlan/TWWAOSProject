from flask import Blueprint, jsonify

users_bp = Blueprint("users", __name__)

@users_bp.route("/users")
def get_users():
    return jsonify({"message": "Lista de utilizatori!"})
