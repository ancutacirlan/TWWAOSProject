from functools import wraps

from flask import jsonify
from flask_login import current_user, login_required


def roles_required(*allowed_roles):
    """Permite accesul doar utilizatorilor cu rolurile specificate."""
    def wrapper(f):
        @login_required
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"error": "Autentificare necesară."}), 401
            if current_user.role not in allowed_roles:
                return jsonify({"error": "Acces interzis. Rol insuficient."}), 403
            return f(*args, **kwargs)
        return decorated_function
    return wrapper