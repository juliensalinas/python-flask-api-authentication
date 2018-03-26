"""General config of flaskapp."""

import os

# Get db host from Docker run and set it to localhost by default
# for local development
db_host = os.getenv("DB_HOST")
if not db_host:
    db_host = "127.0.0.1"

# Connection to database
SQLALCHEMY_DATABASE_URI = ("postgresql://"
                           "flaskapp_user:"
                           "flaskapp_pass@"
                           "{}/"
                           "flaskapp_db"
                           .format(db_host))

# Recommended in order to reduce memory overhead
SQLALCHEMY_TRACK_MODIFICATIONS = False

# For various security features like CSRF or token generation
SECRET_KEY = ""
SECURITY_PASSWORD_SALT = ""
EMAIL_TOKEN_EXPIRATION = 172800  # Tokens sent by emails are valid for 2 days

# Mail settings used for email sending
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = ""
MAIL_PASSWORD = ""
MAIL_DEFAULT_SENDER = ""

# User folders path set by Docker run.
# If nothing set, put folders at the root of project.
USER_FOLDERS_PATH = os.getenv("USER_FOLDERS_PATH")
if not USER_FOLDERS_PATH:
    USER_FOLDERS_PATH = "."

# Logging settings.
# Log file path is set by Docker run.
# If nothing set, log to console (specified in setup.py).
# Set DEBUG to True during dev and False in production.
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH")
DEBUG = True
