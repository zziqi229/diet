from marshmallow import Schema, fields, validate, validates_schema
from marshmallow import ValidationError


class ExerciseRecordSchema(Schema):
    id = fields.Integer(required=True)
    user_id = fields.Integer(required=True)
    content = fields.String(required=True)
    exercised_at = fields.String(required=True)
    duration_minutes = fields.Integer(required=True)
    created_at = fields.String(required=True)
    updated_at = fields.String(required=True)


class ExerciseCreateRequestSchema(Schema):
    content = fields.String(required=True, validate=validate.Length(min=1, max=2000))
    exercised_at = fields.DateTime(required=True)
    duration_minutes = fields.Integer(required=True, validate=validate.Range(min=1))


class ExerciseUpdateRequestSchema(Schema):
    content = fields.String(required=False, validate=validate.Length(min=1, max=2000))
    exercised_at = fields.DateTime(required=False)
    duration_minutes = fields.Integer(required=False, validate=validate.Range(min=1))

    @validates_schema
    def validate_non_empty(self, data, **kwargs):
        if not data:
            raise ValidationError("no updatable fields provided (content, exercised_at, duration_minutes)")


class ExerciseRecordResponseSchema(Schema):
    success = fields.Boolean(required=True)
    data = fields.Nested(ExerciseRecordSchema, required=True)


class ExerciseListQuerySchema(Schema):
    start = fields.DateTime(required=False)
    end = fields.DateTime(required=False)


class ExerciseListResponseSchema(Schema):
    success = fields.Boolean(required=True)
    data = fields.List(fields.Nested(ExerciseRecordSchema), required=True)
    total = fields.Integer(required=True)
