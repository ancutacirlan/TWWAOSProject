from flask import Blueprint, jsonify

users_bp = Blueprint("users", __name__)

@users_bp.route("/users")
def get_users():
    return jsonify({"message": "Lista de utilizatori!"})

@users_bp.route("/test/logout")
def get_logout():
    return jsonify({"message": "test logout!"})

@users_bp.route("/test/login")
def get_login():
    return jsonify({"message": "test login!"})

@users_bp.route("/test/fail")
def get_fail():
    return jsonify({"message": "test fail!"})
