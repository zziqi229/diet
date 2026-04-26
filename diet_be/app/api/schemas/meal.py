from marshmallow import Schema, ValidationError, fields, validate, validates_schema

MEAL_TYPES = ("breakfast", "lunch", "dinner")
INTAKE_LEVELS = ("fast", "normal", "feast")


class MealRecordSchema(Schema):
    id = fields.Integer(required=True)
    user_id = fields.Integer(required=True)
    date = fields.String(required=True)
    meal_type = fields.String(required=True)
    intake_level = fields.String(required=True)
    note = fields.String(allow_none=True)
    created_at = fields.String(required=True)
    updated_at = fields.String(required=True)


class MealCreateRequestSchema(Schema):
    date = fields.Date(required=True)
    meal_type = fields.String(required=True, validate=validate.OneOf(MEAL_TYPES))
    intake_level = fields.String(required=True, validate=validate.OneOf(INTAKE_LEVELS))
    note = fields.String(required=False, allow_none=True)


class MealUpdateRequestSchema(Schema):
    intake_level = fields.String(required=False, validate=validate.OneOf(INTAKE_LEVELS))
    note = fields.String(required=False, allow_none=True)

    @validates_schema
    def validate_non_empty(self, data, **kwargs):
        if not data:
            raise ValidationError("no updatable fields provided (intake_level, note)")


class MealRecordResponseSchema(Schema):
    success = fields.Boolean(required=True)
    data = fields.Nested(MealRecordSchema, required=True)


class MealListQuerySchema(Schema):
    start = fields.Date(required=False)
    end = fields.Date(required=False)


class MealListResponseSchema(Schema):
    success = fields.Boolean(required=True)
    data = fields.List(fields.Nested(MealRecordSchema), required=True)
    total = fields.Integer(required=True)
