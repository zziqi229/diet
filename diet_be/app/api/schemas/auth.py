from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    id = fields.Integer(required=True)
    username = fields.String(required=True)
    created_at = fields.String(required=True)


class RegisterRequestSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))


class LoginRequestSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


class AuthDataSchema(Schema):
    user = fields.Nested(UserSchema, required=True)
    access_token = fields.String(required=True)


class AuthResponseSchema(Schema):
    success = fields.Boolean(required=True)
    message = fields.String(required=True)
    data = fields.Nested(AuthDataSchema, required=True)
