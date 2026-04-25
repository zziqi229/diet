from marshmallow import Schema, fields, validate, validates_schema
from marshmallow import ValidationError

MEAL_TYPES = ["breakfast", "lunch", "dinner", "late_night", "snack"]


class MealRecordSchema(Schema):
    id = fields.Integer(required=True)
    user_id = fields.Integer(required=True)
    content = fields.String(required=True)
    satiety = fields.Integer(required=True)
    meal_type = fields.String(required=True)
    eaten_at = fields.String(required=True)
    created_at = fields.String(required=True)
    updated_at = fields.String(required=True)


class MealCreateRequestSchema(Schema):
    content = fields.String(required=True, validate=validate.Length(min=1, max=2000))
    satiety = fields.Integer(required=True, validate=validate.Range(min=0, max=15))
    meal_type = fields.String(required=True, validate=validate.OneOf(MEAL_TYPES))
    eaten_at = fields.DateTime(required=True)


class MealUpdateRequestSchema(Schema):
    content = fields.String(required=False, validate=validate.Length(min=1, max=2000))
    satiety = fields.Integer(required=False, validate=validate.Range(min=0, max=15))
    meal_type = fields.String(required=False, validate=validate.OneOf(MEAL_TYPES))
    eaten_at = fields.DateTime(required=False)

    @validates_schema
    def validate_non_empty(self, data, **kwargs):
        if not data:
            raise ValidationError("no updatable fields provided (content, satiety, meal_type, eaten_at)")


class MealRecordResponseSchema(Schema):
    success = fields.Boolean(required=True)
    data = fields.Nested(MealRecordSchema, required=True)


class MealListQuerySchema(Schema):
    start = fields.DateTime(required=False)
    end = fields.DateTime(required=False)


class MealListResponseSchema(Schema):
    success = fields.Boolean(required=True)
    data = fields.List(fields.Nested(MealRecordSchema), required=True)
    total = fields.Integer(required=True)
