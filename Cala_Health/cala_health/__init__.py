from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_restful import Api

app = Flask(__name__)
app.config.from_object('configuration.DevelopmentConfig')
api = Api(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

from cala_health.clinic.url import *
db.create_all()
