"""
Initialize various settings.

Just a hack in order to avoid circular imports.
Read this:
https://stackoverflow.com/questions/22929839/circular-import-of-db-reference-using-flask-sqlalchemy-and-blueprints
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

# Init Flask
app = Flask(__name__)

# Get config from config.py
app.config.from_pyfile('config.py')

# Init SQLAlchemy for database handling
db = SQLAlchemy()

# Init flask_mail for mail sending
mail = Mail()

# Init flask_login which handles user login
login_manager = LoginManager()

# Set logging
if app.config['LOG_FILE_PATH']:
    loggingHandler = RotatingFileHandler(
        '{}/all.log'.format(app.config['LOG_FILE_PATH']),
        maxBytes=10000,
        backupCount=1
    )
else:
    loggingHandler = StreamHandler()
if app.config['DEBUG']:
    loggingHandler.setLevel(logging.DEBUG)
else:
    loggingHandler.setLevel(logging.WARNING)
app.logger.addHandler(loggingHandler)
