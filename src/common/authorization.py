#Repositories
#Services
from common.conexao_banco import session
from common.conexao_banco import get_session
from common.custom_exception import CustomException
from common.error_messages import *
#Tables
from models.schema_public import User
#Libs
from sqlalchemy import and_
from flask import request, g
from flask_babel import _
import jwt

def get_current_user():
    jwt_encoded = request.headers['Authorization']
    jwt_encoded = jwt_encoded.replace('Bearer ', '')
    jwt_decoded = jwt.decode(jwt_encoded, options={"verify_signature": False})
    username = ''
    if 'cognito:username' in jwt_decoded:
        username = jwt_decoded['cognito:username']
    elif 'username' in jwt_decoded:
        username = jwt_decoded['username']
    user = session.query(User).\
        filter(and_(User.Ativo == True, User.Excluido == False, User.Username == username)).\
        first()
    if not user:
        raise CustomException(_(X_NOT_FOUND).format(_(USER) + ': ' + username))
    if user.Cliente.Ativo == False or user.Cliente.Excluido == True:
        raise CustomException(_(USER_BELONGS_TO_DEACTIVATED_CUSTOMER))

    g.user = user
    return user

def authenticate(app):
    print(app)