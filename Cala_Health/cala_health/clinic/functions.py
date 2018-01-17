from cala_health.clinic.models import *
from cala_health import app
import jwt
import hashlib


def computeMD5hash(my_string):
    m = hashlib.md5()
    m.update(my_string.encode('utf-8'))
    return m.hexdigest()


def get_user_role_from_token(token):
    value = jwt.decode(token.encode('utf-8'), app.config['SECRET_KEY'])
    username = value['username']
    user = User.query.filter_by(username=username).first()
    userrole_data = UserRole.query.filter_by(user_id=user.id).all()

    roles = []
    for row in userrole_data:
        roles.insert(0, row.role_id)
    return roles


def get_user_id_from_token(token):
    value = jwt.decode(token.encode('utf-8'), app.config['SECRET_KEY'])
    username = value['username']
    user = User.query.filter_by(username=username).first()
    return user.id


# Compare the user's role array and action allowed roles
# Return top role of the user's for the behavior

def get_top_role(user_roles, action_roles):
    role = 10
    for i in user_roles:
        for j in action_roles:
            if i == j and i < role:
                role = i
    result = 0 if role == 10 else role
    return result
