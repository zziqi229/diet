from marshmallow import Schema, fields, validate, validates_schema
from marshmallow import ValidationError


class WeightRecordSchema(Schema):
    id = fields.Integer(required=True)
    user_id = fields.Integer(required=True)
    weight_kg = fields.Float(required=True)
    recorded_at = fields.String(required=True)
    created_at = fields.String(required=True)
    updated_at = fields.String(required=True)


class WeightCreateRequestSchema(Schema):
    weight_kg = fields.Float(required=True, validate=validate.Range(min=0.01, max=999.99))
    recorded_at = fields.DateTime(required=True)


class WeightUpdateRequestSchema(Schema):
    weight_kg = fields.Float(required=False, validate=validate.Range(min=0.01, max=999.99))
    recorded_at = fields.DateTime(required=False)

    @validates_schema
    def validate_non_empty(self, data, **kwargs):
        if not data:
            raise ValidationError("no updatable fields provided (weight_kg, recorded_at)")


class WeightRecordResponseSchema(Schema):
    success = fields.Boolean(required=True)
    data = fields.Nested(WeightRecordSchema, required=True)


class WeightListQuerySchema(Schema):
    start = fields.DateTime(required=False)
    end = fields.DateTime(required=False)


class WeightListResponseSchema(Schema):
    success = fields.Boolean(required=True)
    data = fields.List(fields.Nested(WeightRecordSchema), required=True)
    total = fields.Integer(required=True)
