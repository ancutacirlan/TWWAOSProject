from flasgger import swag_from
from flask import Blueprint, jsonify, request

from app import User, db
from app.decorators import roles_required
from app.models import UserRole

users_bp = Blueprint("users", __name__, url_prefix="/users")

@users_bp.route('/professors', methods=['GET'])
@roles_required("CD","SEC","SG")
@swag_from({
    'tags': ['Utilizatori'],
    'summary': 'Obține lista cadrelor didactice',
    'description': 'Returnează o listă cu toate cadrele didactice (utilizatori cu rolul CD). Accesibil pentru SG, SEC și CD.',
    'responses': {
        200: {
            'description': 'Lista cadrelor didactice',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'user_id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'email': {'type': 'string'},
                    }
                }
            }
        },
        403: {'description': 'Acces interzis'}
    }
})
def get_professors():
    cadre = User.query.filter_by(role=UserRole.CD).all()
    return jsonify([
        {
            "user_id": c.user_id,
            "name": c.name,
            "email": c.email,
        } for c in cadre
    ]), 200


@users_bp.route("/<int:user_id>", methods=["PUT"])
@roles_required("SEC")
@swag_from({
    'tags': ['Utilizatori'],
    'summary': 'Editează un utilizator',
    'description': 'Permite secretariatului (SEC) să editeze datele unui utilizator.',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID-ul utilizatorului ce va fi editat'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'email': {'type': 'string'},
                    'role': {'type': 'string', 'enum': ['SEC', 'SG', 'CD', 'ADM']},
                    'teacherId': {'type': 'integer'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Utilizator actualizat cu succes'},
        403: {'description': 'Acces interzis'},
        404: {'description': 'Utilizatorul nu a fost găsit'},
        400: {'description': 'Date invalide'}
    }
})
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Utilizatorul nu a fost găsit"}), 404

    data = request.get_json()

    # Validări
    if 'role' in data:
        try:
            data['role'] = UserRole(data['role'])
        except ValueError:
            return jsonify({"message": "Rol invalid"}), 400

    if data.get('role') == UserRole.CD and not data.get('teacherId'):
        return jsonify({"message": "teacherId este obligatoriu pentru CD"}), 400

    if data.get("role") == UserRole.CD:
        teacher_id_value = data.get("teacherId")
        if not teacher_id_value:
            return jsonify({"message": "teacherId este obligatoriu pentru CD"}), 400

        existing_user = User.query.filter(
            User.teacherId == teacher_id_value,
            User.user_id != user.user_id
        ).first()
        if existing_user:
            return jsonify({"message": "teacherId deja utilizat de un alt user"}), 400
    else:
        data["teacherId"] = None


    # Aplicăm modificările
    for key in ['name', 'email', 'role', 'teacherId']:
        if key in data:
            setattr(user, key, data[key])

    db.session.commit()
    return jsonify({"message": "Utilizator actualizat cu succes"}), 200
