"""Initialize API."""

from flask import Blueprint
from flask_restplus import Api

from .ns1 import api as ns1
from .ns2 import api as ns2
from .auth import authorizations

blueprint = Blueprint('api', __name__)
api = Api(
    blueprint,
    title='API title',
    version='1.0',
    description='API description',
    authorizations=authorizations,
)

api.add_namespace(ns1, path='/build')
api.add_namespace(ns2, path='/deploy')
