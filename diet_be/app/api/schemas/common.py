from marshmallow import Schema, fields


class ErrorResponseSchema(Schema):
    success = fields.Boolean(required=True, dump_default=False)
    message = fields.String(required=True)


class MessageResponseSchema(Schema):
    success = fields.Boolean(required=True)
    message = fields.String(required=True)
