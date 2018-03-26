"""Database models of user_account."""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (JSONWebSignatureSerializer
                          as Serializer, BadSignature)

from setup import db, login_manager, app


@login_manager.user_loader
def load_user(user_email):
    """Make flask-login talk to database."""
    return User.query.get(user_email)


class User(UserMixin, db.Model):
    """
    User who registered to the app.

    We set a different name in db because user is a reserved
    posgtgresql name.
    """

    __tablename__ = "flask_user"

    email = db.Column(db.String(120), primary_key=True)
    password = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    company_name = db.Column(db.String(50), nullable=True)
    sector = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), nullable=True)
    address = db.Column(db.String(50), nullable=True)
    is_premium = db.Column(db.Boolean(), default=False, nullable=False)
    registered_on = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        nullable=False
    )
    updated_on = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
        nullable=True
    )
    confirmed = db.Column(db.Boolean(), nullable=False)

    def set_password(self, password):
        """Hash password before saving."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check password hash against a pwd provided by user."""
        return check_password_hash(self.password, password)

    def get_id(self):
        """
        Override pk definition for flask-login.

        By default flask-login expects an id as a pk but here we set email
        as the pk, so need to override flask-login's get_id() method.
        """
        return self.email

    def generate_auth_token(self):
        """Generate an API auth token for user."""
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'email': self.email})

    @staticmethod
    def verify_auth_token(token):
        """Check that user API token is correct."""
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['email'])
        return user

    def __repr__(self):
        """User object is represented by an email."""
        return '<{}>'.format(self.email)
