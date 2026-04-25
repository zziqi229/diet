from marshmallow import Schema, fields, validate

MEAL_TYPES = ["breakfast", "lunch", "dinner"]


class FastRecordSchema(Schema):
    id = fields.Integer(required=True)
    user_id = fields.Integer(required=True)
    date = fields.String(required=True)
    meal_type = fields.String(required=True)
    note = fields.String(allow_none=True)
    created_at = fields.String(required=True)


class FastCreateRequestSchema(Schema):
    date = fields.Date(required=True)
    meal_type = fields.String(required=True, validate=validate.OneOf(MEAL_TYPES))
    note = fields.String(required=False, load_default=None, validate=validate.Length(max=500))


class FastListQuerySchema(Schema):
    start = fields.Date(required=False)
    end = fields.Date(required=False)


class FastRecordResponseSchema(Schema):
    success = fields.Boolean(required=True)
    data = fields.Nested(FastRecordSchema, required=True)


class FastListResponseSchema(Schema):
    success = fields.Boolean(required=True)
    data = fields.List(fields.Nested(FastRecordSchema), required=True)
    total = fields.Integer(required=True)
