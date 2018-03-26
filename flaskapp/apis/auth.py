"""Authentication utilities needed by API."""

from flask import request
from functools import wraps

from setup import app
from user_account.models import User

# Auth dict needed by Swagger
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}


def token_required(f):
    """
    Perform token based authentication.

    Token is supposed to be passed in headers.
    If found, decrypt token and get matching user.
    If no token in header or user not found, return an error message.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        """Use this decorator on every API endpoints."""
        token = None

        # Check if token
        try:
            token = request.headers["X-API-KEY"]
        except KeyError:
            app.logger.debug("Auth token is missing.")
            return {"message": "Authentication token is missing."}, 401

        app.logger.debug("Got auth token: {}.".format(token))
        # Get user from JWT token and check if exists
        user = User.verify_auth_token(token)
        if not user:
            app.logger.debug("User not found for this token: {}".format(token))
            return {"message": "User not found."}, 401

        return f(*args, **kwargs)

    return decorated


def premium_required(f):
    """
    Check if user is premium.

    We know that user exists thanks to the token_required decorator.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        """Use this decorator on API endpoints restricted to premium users."""
        token = None

        # Get user and check if is premium
        token = request.headers["X-API-KEY"]
        user = User.verify_auth_token(token)
        if not user.is_premium:
            return {"message": "Restricted to premium users."}, 402

        return f(*args, **kwargs)

    return decorated
