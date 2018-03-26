"""Forms of user_account."""

from wtforms import Form, StringField, PasswordField, validators

from .models import User


class RegistrationForm(Form):
    """Registration."""

    email = StringField('Email Address', [
        validators.DataRequired(),
        validators.Length(min=6, max=100)
    ])
    password = PasswordField('Password (at least 8 characters)', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match'),
        validators.Length(min=8, max=20)
    ])
    confirm = PasswordField('Confirm Password', [validators.DataRequired()])

    def validate(self):
        """
        Custom validation of email.

        We want to check if user already exists in db before
        registering him.
        """
        fv = Form.validate(self)
        if not fv:
            return False

        if User.query.get(self.email.data):
            self.email.errors.append('User already registered')
            return False

        return True


class LoginForm(Form):
    """Login."""

    email = StringField('Email Address', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])


class SendResetEmailForm(Form):
    """Enter email for a reset pwd link."""

    email = StringField('Email Address', [validators.DataRequired()])


class ResetPwdForm(Form):
    """Set new password in case of lost password."""

    password = PasswordField('Password (at least 8 characters)', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match'),
        validators.Length(min=8, max=20)
    ])
    confirm = PasswordField('Confirm Password', [validators.DataRequired()])
