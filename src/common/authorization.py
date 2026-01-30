#Repositories
#Services
import os
from functools import lru_cache

from common.conexao_banco import session
from common.custom_exception import CustomException
from common.error_messages import *

#Tables
from models.schema_public import User

#Libs
from sqlalchemy import and_
from flask import request, g
from flask_babel import _
import jwt
from jwt import PyJWKClient


def _get_bearer_token() -> str:
    auth = request.headers.get("Authorization", "").strip()
    if not auth:
        raise CustomException(_("Missing Authorization header"))
    if not auth.lower().startswith("bearer "):
        raise CustomException(_("Authorization must be: Bearer <token>"))
    return auth.split(" ", 1)[1].strip()


def _claims_from_apigw_context() -> dict | None:
    """
    When using serverless-wsgi with HTTP API, the raw APIGW event is often stored here.
    JWT authorizer claims are in:
      event.requestContext.authorizer.jwt.claims
    """
    event = request.environ.get("apig_wsgi.event")
    if not isinstance(event, dict):
        return None
    try:
        return event["requestContext"]["authorizer"]["jwt"]["claims"]
    except Exception:
        return None


@lru_cache(maxsize=2)
def _jwks_client(issuer: str) -> PyJWKClient:
    jwks_url = issuer.rstrip("/") + "/.well-known/jwks.json"
    return PyJWKClient(jwks_url)


def _verify_and_decode(token: str) -> dict:
    issuer = os.getenv("COGNITO_ISSUER") or os.getenv("ISSUERURL")
    audience = os.getenv("COGNITO_AUDIENCE") or os.getenv("AUDIENCE")

    if not issuer or not audience:
        raise CustomException(_("Missing COGNITO_ISSUER/COGNITO_AUDIENCE env vars"))

    try:
        key = _jwks_client(issuer).get_signing_key_from_jwt(token).key
        return jwt.decode(
            token,
            key=key,
            algorithms=["RS256"],
            audience=audience,
            issuer=issuer,
            options={"require": ["exp", "iat"]},
        )
    except Exception as exc:
        raise CustomException(_("Invalid or expired token")) from exc


def _extract_username(claims: dict) -> str:
    if not isinstance(claims, dict):
        return ""
    for k in ("cognito:username", "username", "sub"):
        v = claims.get(k)
        if v:
            return str(v)
    return ""


def get_current_user():
    # 1) Preferred: claims already validated by API Gateway
    claims = _claims_from_apigw_context()

    # 2) Fallback: verify JWT in-app (defense in depth)
    if not claims:
        token = _get_bearer_token()
        claims = _verify_and_decode(token)

    username = _extract_username(claims)
    if not username:
        raise CustomException(_("Username not found in token claims"))

    user = (
        session.query(User)
        .filter(and_(User.Ativo == True, User.Excluido == False, User.Username == username))
        .first()
    )

    if not user:
        raise CustomException(_(X_NOT_FOUND).format(_(USER) + ': ' + username))

    if user.Cliente.Ativo == False or user.Cliente.Excluido == True:
        raise CustomException(_(USER_BELONGS_TO_DEACTIVATED_CUSTOMER))

    g.user = user
    return user


def authenticate(app):
    """
    Call authenticate(app) once when creating the Flask app.
    This will enforce authentication on every request.
    """

    @app.before_request
    def _auth_before_request():
        if request.path.endswith("/health"):
            return
        get_current_user()

    return app
