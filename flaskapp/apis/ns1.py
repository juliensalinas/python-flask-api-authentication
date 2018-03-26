"""Upload raw data file."""

from flask import request
from flask_restplus import Namespace, Resource
from werkzeug.datastructures import FileStorage

from setup import app
from .auth import token_required, premium_required
from user_account.models import User

api = Namespace('Build', description='Description')

parser1 = api.parser()
parser1.add_argument(
    'file',
    type=FileStorage,
    required=True,
    location='files',
    help='Data file'
)


@api.route('/1_upload')
class Upload(Resource):
    """Upload the raw data file."""

    @api.doc(security='apikey')
    @premium_required
    @token_required
    @api.expect(parser1)
    def post(self):
        """Post data."""
        # Get user from JWT token.
        # We know that token and user exist because already checked in
        # decorator.
        token = request.headers["X-API-KEY"]
        user = User.verify_auth_token(token)
        app.logger.debug("API user is {}".format(user))

        # Save file to user folder
        args = parser1.parse_args()
        uploaded_file = args['file']
        fname = uploaded_file.filename
        uploaded_file.save('{}/{}/data/data0.csv'.format(
            app.config['USER_FOLDERS_PATH'],
            user.email)
        )
        return {
            "Status": "Your file===" + fname + "===was Successfully Uploaded"
        }
