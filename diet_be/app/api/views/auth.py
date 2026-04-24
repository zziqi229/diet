from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import create_access_token

from ...extensions import db
from ...models import User
from ..schemas import (
    AuthResponseSchema,
    ErrorResponseSchema,
    LoginRequestSchema,
    RegisterRequestSchema,
)


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth", description="Auth APIs")


@auth_bp.route("/register")
class RegisterResource(MethodView):
    @auth_bp.arguments(RegisterRequestSchema)
    @auth_bp.response(201, AuthResponseSchema)
    @auth_bp.alt_response(400, schema=ErrorResponseSchema)
    @auth_bp.alt_response(409, schema=ErrorResponseSchema)
    def post(self, data):
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        if not username or not password:
            return {"success": False, "message": "username and password are required"}, 400

        if User.query.filter_by(username=username).first():
            return {"success": False, "message": "username already exists"}, 409

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        token = create_access_token(identity=str(user.id))
        return {
            "success": True,
            "message": "User registered successfully",
            "data": {"user": user.to_dict(), "access_token": token},
        }


@auth_bp.route("/login")
class LoginResource(MethodView):
    @auth_bp.arguments(LoginRequestSchema)
    @auth_bp.response(200, AuthResponseSchema)
    @auth_bp.alt_response(400, schema=ErrorResponseSchema)
    @auth_bp.alt_response(401, schema=ErrorResponseSchema)
    def post(self, data):
        identifier = (data.get("username") or "").strip()
        password = data.get("password") or ""

        if not identifier or not password:
            return {"success": False, "message": "username and password are required"}, 400

        user = User.query.filter_by(username=identifier).first()
        if not user or not user.check_password(password):
            return {"success": False, "message": "invalid credentials"}, 401

        token = create_access_token(identity=str(user.id))
        return {
            "success": True,
            "message": "Login successful",
            "data": {"user": user.to_dict(), "access_token": token},
        }
