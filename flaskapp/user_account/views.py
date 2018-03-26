"""Backend of the user_account blueprint."""

from flask import (
    Blueprint,
    render_template,
    request,
    abort,
    redirect,
    url_for,
    flash
)
from jinja2 import TemplateNotFound
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from flask_login import (
    login_user,
    login_required,
    logout_user,
    current_user
)
import pathlib

from setup import db, mail, app
from .models import User
from .forms import (
    RegistrationForm,
    LoginForm,
    SendResetEmailForm,
    ResetPwdForm
)

user_account_pages = Blueprint(
    'user_account_pages',
    __name__,
    template_folder='templates'
)


@user_account_pages.route('/', defaults={'page': 'index'})
@user_account_pages.route('/<page>')
@login_required
def user_playground(page):
    """
    Show the user backoffice.

    If the user is not logged in, he is redirected to a
    login/register page.
    If logged in, show the user API token.
    """
    api_token = current_user.generate_auth_token().decode('ascii')
    try:
        return render_template('%s.html' % page, api_token=api_token)
    except TemplateNotFound:
        abort(404)


@user_account_pages.route(
    '/login',
    methods=['GET', 'POST'],
    defaults={'page': 'login'}
)
@user_account_pages.route('/<page>')
def login(page):
    """
    Log a user in.

    Checks if user exists in DB. If so, set a session for him.
    """
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data
        user = User.query.get(email)
        if user is None or not user.check_password(password):
            # If could not log in, stay on login page and raise an error
            flash('Invalid username or password')
            return redirect(url_for('user_account_pages.login'))
        # If user found in db, log him and redirect him to user_playground.
        # Remember user so no need to login again next time.
        login_user(user, remember=True)
        app.logger.debug("{} logged in.".format(user))
        return redirect(url_for('user_account_pages.user_playground'))
    try:
        return render_template('%s.html' % page, form=form)
    except TemplateNotFound:
        abort(404)


@user_account_pages.route('/logout', defaults={'page': 'logout'})
def logout(page):
    """Log user out."""
    logout_user()
    app.logger.debug("User logged out.")
    return redirect(url_for('user_account_pages.login'))


def send_registration_email(user):
    """
    Send an email to user in order for him to complete registration.

    Email contains a unique id which is an encrypted email + an encrypted
    current time.
    """
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    activation_token = serializer.dumps(
        user.email,
        salt=app.config['SECURITY_PASSWORD_SALT']
    )
    confirm_url = url_for(
        'user_account_pages.get_registration_confirmation',
        token=activation_token,
        _external=True
    )
    html = render_template(
        'emails/activate.html',
        confirm_url=confirm_url
    )
    subject = "Activation email"
    msg = Message(
        subject,
        recipients=[user.email],
        html=html
    )
    mail.send(msg)
    app.logger.debug("Activation email sent to {}.".format(user))


@user_account_pages.route(
    '/get-registration-confirmation',
    defaults={'page': 'get_registration_confirmation'}
)
@user_account_pages.route('/<page>')
def get_registration_confirmation(page):
    """
    Get a registration confirmation after clicking the email's link.

    Must find user based on encrypted email + decrypt time in order to make
    sure the link is not too old.
    If everything ok, user is flagged as active in DB and user folders are
    created.
    Then user is redirected to user_playground.
    """
    # Activation token is not passed as a positional argument but as a get
    # parameter we retrieve it here.
    activation_token = request.args.get('token')
    if not activation_token:
        app.logger.debug("Activation token not retrieved.")
        return redirect(url_for('user_account_pages.register'))

    # Decrypt email from url and check expiration
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            activation_token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=app.config['EMAIL_TOKEN_EXPIRATION']
        )
        app.logger.debug(
            "Email retrieved from activation link: {}.".format(email)
        )
    except:
        app.logger.debug("Activation link was too old.")
        return redirect(url_for('user_account_pages.activation_too_old'))

    # Try to find user in db and update it
    user = User.query.get(email)
    if user:
        user.confirmed = True
        db.session.commit()
        app.logger.debug("User to be activated found in db: {}.".format(user))
        create_user_folders(user)
        app.logger.debug("User folders created for {}.".format(user))
    else:
        app.logger.debug(
            "Could not activate user. Not found in db: {}.".format(email)
        )
        return redirect(url_for('user_account_pages.activation_no_user'))

    # Log user in and redirect him to his playground
    login_user(user, remember=True)
    flash('Your account has been successfully activated!')
    return redirect(url_for('user_account_pages.user_playground'))


def create_user_folders(user):
    """
    Create user folders.

    Each user has one folder whose name is the email hash.
    This folder contains 2 subfolders:
    - data
    - model
    Folder name is the user email in order to browse it easily.
    """
    base_path = app.config['USER_FOLDERS_PATH']
    folder_name = user.email
    # Create data folder
    pathlib.Path('{}/{}/data'.format(
        base_path,
        folder_name
    )).mkdir(parents=True, exist_ok=True)
    # Create model folder
    pathlib.Path('{}/{}/model'.format(
        base_path,
        folder_name
    )).mkdir(parents=True, exist_ok=True)


@user_account_pages.route(
    '/tmp-registration-ok',
    defaults={'page': 'tmp_registration_ok'}
)
@user_account_pages.route('/<page>')
def tmp_registration_ok(page):
    """Simple confirmation that first step of registration is ok."""
    try:
        return render_template('%s.html' % page)
    except TemplateNotFound:
        abort(404)


@user_account_pages.route(
    '/activation-error-too-old',
    defaults={'page': 'activation_too_old'}
)
@user_account_pages.route('/<page>')
def activation_too_old(page):
    """Simple error page if activation by email fails because to old."""
    try:
        return render_template('%s.html' % page)
    except TemplateNotFound:
        abort(404)


@user_account_pages.route(
    '/activation-no-user',
    defaults={'page': 'activation_no_user'}
)
@user_account_pages.route('/<page>')
def activation_no_user(page):
    """Simple error page if activation by email fails because no user found."""
    try:
        return render_template('%s.html' % page)
    except TemplateNotFound:
        abort(404)


@user_account_pages.route(
    '/register',
    methods=['GET', 'POST'],
    defaults={'page': 'register'}
)
@user_account_pages.route('/<page>')
def register(page):
    """
    Register a user.

    The following data are retrieved from user and saved to DB:
    - email
    - password
    - confirmation password (handled in forms.py)

    Data are saved to DB but user is flagged as inactive as long as
    the confirmation link has not been clicked.
    No user folder is created here.
    """
    form = RegistrationForm(request.form)

    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data
        user = User(
            email=email,
            registered_on=datetime.now(),
            confirmed=False
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        send_registration_email(user)
        app.logger.debug("{} successfully registered.".format(user))
        return redirect(url_for('user_account_pages.tmp_registration_ok'))

    try:
        return render_template('%s.html' % page, form=form)
    except TemplateNotFound:
        abort(404)


@user_account_pages.route(
    '/get-pwd-reset-email',
    methods=['GET', 'POST'],
    defaults={'page': 'get_pwd_reset_email'}
)
@user_account_pages.route('/<page>')
def get_pwd_reset_email(page):
    """
    Get email from user in order to change his password.

    Once email is retrieved, send an encoded link to user.
    """
    form = SendResetEmailForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        user = User.query.get(email)
        if user is None:
            # User not found for this email
            app.logger.debug("User not found for this email: {}".format(email))
            flash('No user found for this email.')
            return redirect(url_for('user_account_pages.register'))
        send_pwd_reset_email(email)
        app.logger.debug("Password reset link sent to: {}".format(email))
        flash("You are going to receive an email very soon. "
              "Please click the link inside in order to reset your password.")
    try:
        return render_template('%s.html' % page, form=form)
    except TemplateNotFound:
        abort(404)


def send_pwd_reset_email(email):
    """
    Send an email to user in order for him to complete registration.

    Email contains a unique id which is an encrypted email + an encrypted
    current time.
    """
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    reset_pwd_token = serializer.dumps(
        email,
        salt=app.config['SECURITY_PASSWORD_SALT']
    )
    confirm_url = url_for(
        'user_account_pages.reset_pwd',
        token=reset_pwd_token,
        _external=True
    )
    html = render_template(
        'emails/reset_pwd.html',
        confirm_url=confirm_url
    )
    subject = "Reset your password"
    msg = Message(
        subject,
        recipients=[email],
        html=html
    )
    mail.send(msg)
    app.logger.debug("Pwd reset email sent to {}.".format(email))


@user_account_pages.route(
    '/reset-pwd',
    methods=['GET', 'POST'],
    defaults={'page': 'reset_pwd'}
)
@user_account_pages.route('/<page>')
def reset_pwd(page):
    """
    Access a password modification page after clicking the email's link.

    Must decrypt email and time in order to find the matching user and make
    sure the link is not too old.
    If everything OK, display a password reset form containing:
    - password
    - password confirmation
    Then user is logged in automatically and redirected to user playground.
    """
    # Get token
    reset_pwd_token = request.args.get('token')
    if not reset_pwd_token:
        app.logger.debug("Reset pwd token not retrieved.")
        return redirect(url_for('user_account_pages.register'))

    # Decrypt email from url and check expiration
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            reset_pwd_token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=app.config['EMAIL_TOKEN_EXPIRATION']
        )
        app.logger.debug(
            "Email retrieved from reset pwd link: {}.".format(email)
        )
    except:
        app.logger.debug("Activation link was too old.")
        return redirect(url_for('user_account_pages.activation_too_old'))

    # Try to find user in db and show form for new password
    user = User.query.get(email)
    if user:
        form = ResetPwdForm(request.form)
        if request.method == 'POST' and form.validate():
            # Update password in db
            password = form.password.data
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            app.logger.debug(
                "{} successfully set a new email.".format(user)
            )
            flash("Your new password has been set. "
                  "Please log in with this new password now.")
            return redirect(url_for('user_account_pages.login'))
    else:
        app.logger.debug(
            "Could not find user db for pwd reset: {}.".format(email)
        )
        return redirect(url_for('user_account_pages.activation_no_user'))

    try:
        return render_template('%s.html' % page, form=form)
    except TemplateNotFound:
        abort(404)
