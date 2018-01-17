from cala_health import db
from sqlalchemy_utils import UUIDType
import  uuid


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(50), nullable=False)

    def __init__(self, name):
        self.role_name = name


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    phone_no = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(50))
    password = db.Column(db.String(50), nullable=False)

    def __init__(self, first_name, last_name, username, password, phone_no=None, address=None):
        self.firstname = first_name
        self.lastname = last_name
        self.address = address
        self.phone_no = phone_no
        self.username = username
        self.password = password


class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    modify_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    modify_date = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref=db.backref('user', lazy='dynamic'), foreign_keys=[user_id])
    modify_user = db.relationship('User', backref=db.backref('modify_user', lazy='dynamic'), foreign_keys=[modify_by])
    role = db.relationship('Role', backref=db.backref('role', lazy='dynamic'))

    def __init__(self, user, role_id):
        self.user = user
        self.role_id = role_id
        self.modify_by = None
        self.modify_date = None


class Clinic(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    logo = db.Column(db.LargeBinary)
    datetime = db.Column(db.DateTime)

    def __init__(self, name, address, logo, datetime):
        self.name = name
        self.address = address
        self.logo = logo
        self.datetime = datetime


class UserClinic(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userrole_id = db.Column(db.Integer, db.ForeignKey('user_role.id'))
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinic.id'))
    modify_date = db.Column(db.DateTime)

    userrole = db.relationship('UserRole', backref=db.backref('userrole', lazy='dynamic'))
    clinic = db.relationship('Clinic', backref=db.backref('clinic', lazy='dynamic'))

    def __init__(self, userrole, clinic, modify_date=None):
        self.userrole = userrole
        self.clinic = clinic
        self.modify_date = modify_date
