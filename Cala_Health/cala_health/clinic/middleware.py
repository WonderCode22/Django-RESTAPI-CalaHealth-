from functools import wraps
from flask import request, jsonify
from cala_health.clinic.functions import *


# middleware that check if can create user with current role

# def has_role_create_user(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = request.cookies.get('token')
#         if not token:
#             return jsonify({'result': 'Please login!'})
#         roles = get_user_role_from_token(token)
#         create_user_enable_roles = [1, 5, 6]
#         result = get_role(roles, create_user_enable_roles)
#
#         if result == 0:
#             return jsonify({'result': 'You are not allowed to create user'})
#         return f(*args, **kwargs)
#     return decorated


def is_authenticated(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return jsonify({'result': 'Please login'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'result': 'Login information is not correct'}), 403

        return f(*args, **kwargs)
    return decorated
