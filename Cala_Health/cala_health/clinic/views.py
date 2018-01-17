from flask import json, make_response, send_file
from sqlalchemy import *

from cala_health.clinic.middleware import *
from cala_health.clinic.functions import *
from cala_health.clinic.variables import *

from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from werkzeug import datastructures
import datetime
import jwt
import jsonschema
from io import BytesIO
import base64


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        status = 400  # Request data is not correct
    else:
        user = User.query.filter_by(username=username).first()
        if user and safe_str_cmp(user.password, computeMD5hash(password)):
            token = jwt.encode({'username': username}, app.config['SECRET_KEY']).decode('utf-8')
            status = 200  # Login Success

            user_role = UserRole.query.filter_by(user_id=user.id).all()

            roles = []
            for row in user_role:
                roles.insert(0, row.role_id)

            data = jsonify({
                "firstname": user.firstname,
                "lastname": user.lastname,
                "roles": json.loads(json.dumps(roles))
            })
            resp = make_response((data, status))
            resp.set_cookie('token', token)
            return resp
        else:
            status = 404  # Not found the User

    return make_response((jsonify({'status': 'failed'}), status))


@app.route('/api/v1/images', methods=['POST'])
def download_image():
    clinic_id = request.form.get('clinic_id')
    logo = Clinic.query.filter_by(id=3).first().logo
    return send_file(BytesIO(logo), attachment_filename='logo.jpg', as_attachment=True)

parser = reqparse.RequestParser()
parser.add_argument('firstname', type=str)
parser.add_argument('lastname', type=str)
parser.add_argument('username', type=str)
parser.add_argument('phone_no', type=str)
parser.add_argument('address', type=str)
parser.add_argument('role_id', type=int)
parser.add_argument('clinic_id', type=int)

class UserApi(Resource):
    @is_authenticated
    def get(self, id=None):
        status = 204
        token = request.cookies.get('token')
        roles = get_user_role_from_token(token)
        res = {}
        researcher_role_no = 2
        restricted_role_no = 3

        if not id:  # /api/v1/users
            if researcher_role_no in roles:
                userroles = UserRole.query.filter_by(role_id=7).all()
                users = []
                for one in userroles:
                    user = User.query.filter_by(id=one.user_id).first()
                    users.insert(0, user)

                    userclinics = UserClinic.query.filter_by(userrole_id=one.id).all()
                    clinics = []
                    for clinic in userclinics:
                        clinics.insert(0, clinic.clinic_id)

                    res[user.id] = {
                        'firstname': user.firstname,
                        'lastname': user.lastname,
                        'clinics': json.loads(json.dumps(clinics))
                    }

                if res:
                    status = 200
                elif not res:
                    status = 204
            #elif restricted_role_no in roles:
            else:
                status = 403
        else:  # /api/v1/users/<id>
            # check if user has the role to view spec user's info
            user_id = get_user_id_from_token(token)
            if researcher_role_no in roles or id == user_id:  # if user is researcher or patient of this id
                user = User.query.filter_by(id=id).first()
                if not user:
                    status = 400
                else:
                    userrole_id = UserRole.query.filter(UserRole.role_id == 7).join(UserRole.user, aliased=True)\
                        .filter_by(id=user.id).first().id
                    clinics = UserClinic.query.join(UserClinic.userrole, aliased=True)\
                        .filter_by(id=userrole_id).all()
                    clinic_ids = []
                    for row in clinics:
                        clinic_ids.insert(0, row.clinic_id)
                    res = {
                        'id': user.id,
                        'firstname': user.firstname,
                        'lastname': user.lastname,
                        'username': user.username,
                        'address': user.address,
                        'phone_no': user.phone_no,
                        'clinics': json.dumps(clinic_ids)
                    }
                    status = 200
            else:
                status = 403
        if status == 200:
            resp = make_response((jsonify(res), status))
            return resp
        else:
            res = {
                'result': 'failed'
            }
            resp = make_response((jsonify(res), status))
            return resp

    @is_authenticated
    def post(self):
        args = parser.parse_args()
        try:
            # Get top role that can be user creatable
            token = request.cookies.get('token')
            user_id = get_user_id_from_token(token)
            roles = get_user_role_from_token(token)
            create_user_enable_roles = [1, 5, 6]
            creator_role = get_top_role(roles, create_user_enable_roles)

            # Get the request data
            jsonschema.validate(args, user_create_schema)
            firstname = args['firstname']
            lastname = args['lastname']
            username = args['username']
            phone_no = args['phone_no']
            address = args['address']
            role_id = args['role_id']
            clinic_id = args['clinic_id']
            if creator_role == 0:
                result = {'result': 'You can\'t create this role'}
                status = 403
            else:
                if role_id in role_match_creatable[creator_role - 1]:  # if creator can create requested user account
                    try:
                        password = computeMD5hash("kjy")
                        new_user = User(firstname, lastname, username, password, phone_no, address)
                        user_role = UserRole(new_user, role_id)
                        db.session.add(new_user)
                        db.session.add(user_role)
                        db.session.commit()
                    except:
                        return jsonify({'result': 'User Create Failed!'})

                    if creator_role == 6:  # if role of creator is Clinician, patient should be added to his clinic
                        query = UserRole.query.filter(
                            and_(UserRole.user_id == user_id, UserRole.role_id == creator_role)).first()
                        userrole_id = query.id
                        query = UserClinic.query.filter_by(userrole_id=userrole_id).all()
                        clinic_ids = []
                        for row in query:
                            clinic_ids.insert(0, row.clinic_id)

                        for clinic_id in clinic_ids:
                            clinic = Clinic.query.filter_by(id=clinic_id).first()
                            userclinic = UserClinic(user_role, clinic)
                            db.session.add(userclinic)
                            db.session.commit()
                    if creator_role == 1:
                        if clinic_id:  # if Cala SuperUser create patient and assign them spec clinic
                            try:
                                clinic = Clinic.query.filter_by(id=clinic_id).first()
                                userclinic = UserClinic(user_role, clinic)
                                db.session.add(userclinic)
                                db.session.commit()
                            except:
                                return jsonify({'result': 'User Create Failed!'})
                    status = 201
                    result = {'result': 'Success'}
                else:
                    status = 403
                    result = {'result': 'You can\'t create this role'}
        except jsonschema.exceptions.ValidationError as ev:
            status = 400
            result = {'result': ev.message}

        return make_response((jsonify(result), status))

    @is_authenticated
    def put(self, id):
        token = request.cookies.get('token')
        roles = get_user_role_from_token(token)
        user_id = get_user_id_from_token(token)
        patient_role = 7
        if (patient_role in roles) and (user_id == id):
            args = parser.parse_args()

            firstname = args['firstname']
            lastname  = args['lastname']
            phone_no  = args['phone_no']
            address   = args['address']
            clinic_id = args['clinic_id']

            User.query.filter_by(id=id).update({
                'firstname': firstname,
                'lastname': lastname,
                'address': address,
                'phone_no': phone_no
            })

            UserRole.query.filter(and_(UserRole.user_id == id, UserRole.role_id == 7)).update({
                'modify_by': id,
                'modify_date': datetime.datetime.now()
            })

            db.session.commit()
            return make_response((jsonify({'result': 'success'}), 200))
        return make_response((jsonify({'result': 'failed'}), 403))

    @is_authenticated
    def delete(self, id):
        token = request.cookies.get('token')
        roles = get_user_role_from_token(token)
        clinic_superuser_role_no = 5

        args = parser.parse_args()
        role_id = args["role_id"]
        clinic_id = args["clinic_id"]

        if clinic_superuser_role_no in roles and role_id in [5, 6, 7]:

            user = User.query.filter_by(id=id)
            userrole = UserRole.query.filter(and_(UserRole.user_id == id, UserRole.role_id == role_id))
            userclinic = UserClinic.query.filter(and_(UserClinic.userrole_id == userrole.first().id, UserClinic.clinic_id == clinic_id))

            #try:
            userclinic.delete()
            userrole.delete()
            user.delete()
            db.session.commit()
            status = 200
            result = {'result': 'success'}
            # except:
            #     status = 500
            #     result = {'result': 'failed'}
        else:
            status = 403
            result = {'result': 'You are not allowed to remove user'}

        return make_response((jsonify(result), status))

#parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('address', type=str)
parser.add_argument('logo', type=datastructures.FileStorage, location='files')

class ClinicApi(Resource):
    @is_authenticated
    def get(self, clinic_id=None):
        token = request.cookies.get('token')
        user_id = get_user_id_from_token(token)
        roles = get_user_role_from_token(token)
        status = 403

        if 5 in roles and 6 in roles:
            clinics = UserClinic.query.join(UserClinic.userrole, aliased=True) \
                .filter(and_(UserRole.user_id == user_id, or_(UserRole.role_id == 5, UserRole.role_id == 6))).all()
        elif 5 in roles:
            clinics = UserClinic.query.join(UserClinic.userrole, aliased=True)\
                .filter(and_(UserRole.user_id == user_id, UserRole.role_id == 5)).all()
        elif 6 in roles:
            clinics = UserClinic.query.join(UserClinic.userrole, aliased=True) \
                .filter(and_(UserRole.user_id == user_id, UserRole.role_id == 6)).all()
        else:
            status = 403

        if clinics:
            clinic_ids = []
            for row in clinics:
                clinic_ids.insert(0, row.clinic_id)
            if clinic_id in clinic_ids:
                status = 200
            else:
                status = 403

        if status == 200:
            data = Clinic.query.filter_by(id=clinic_id).first()
            result = jsonify({
                "name": data.name,
                "address": data.address,
                 "logo": "/api/v1/images/"+str(data.id),
                "datetime": data.datetime
            })
            return make_response(send_file(BytesIO(data.logo), attachment_filename="messi.jpg", as_attachment=True))
        result = {'result': 'You can\'t view the user profile'}
        return make_response(jsonify(result), status)

    @is_authenticated
    def post(self):
        token = request.cookies.get('token')
        #user_id = get_user_id_from_token(token)
        roles = get_user_role_from_token(token)
        cala_superuser_role_no = 1
        if cala_superuser_role_no in roles:
            args = parser.parse_args()
            name = args['name']
            address = args['address']
            logo = args['logo']
            date_time = datetime.datetime.now()

            clinic = Clinic(name, address, logo.read(), date_time)
            db.session.add(clinic)
            db.session.commit()
            status = 200
            result = {'result': 'success'}
        else:
            status = 403
            result = {'result': 'You are not allowed to create Clinic'}
        return make_response((result, status))
