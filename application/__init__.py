import os
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

with open("/etc/project_config.json") as config_file:
    config = json.load(config_file)

application = Flask(__name__)
application.config['SECRET_KEY'] = config["SECRET_KEY"]
application.config['SQLALCHEMY_DATABASE_URI'] = config["DATABASE_URI"]
db = SQLAlchemy(application)
bcrypt = Bcrypt(application)
login_manager = LoginManager(application)
login_manager.login_view = 'login'
login_manager.login_message_category = 'primary'
application.config['MAIL_SERVER'] = 'smtp.googlemail.com'
application.config['MAIL_PORT'] = 587
application.config['MAIL_USE_TLS'] = True
application.config['MAIL_USERNAME'] = config["USER_EMAIL"]
application.config['MAIL_PASSWORD'] = config["USER_PASS"]
mail = Mail(application)

from application import routes
