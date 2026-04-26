from datetime import datetime, timezone

from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint

from ...extensions import db
from ...models import MealRecord
from ..schemas import (
    ErrorResponseSchema,
    MealCreateRequestSchema,
    MealListQuerySchema,
    MealListResponseSchema,
    MealRecordResponseSchema,
    MealUpdateRequestSchema,
    MessageResponseSchema,
)

meal_bp = Blueprint(
    "meal",
    __name__,
    url_prefix="/api/meal",
    description="Meal record APIs",
)


@meal_bp.route("/")
class MealCollectionResource(MethodView):
    @jwt_required()
    @meal_bp.doc(security=[{"BearerAuth": []}])
    @meal_bp.arguments(MealCreateRequestSchema)
    @meal_bp.response(201, MealRecordResponseSchema)
    @meal_bp.alt_response(400, schema=ErrorResponseSchema)
    @meal_bp.alt_response(409, schema=ErrorResponseSchema)
    def post(self, data):
        user_id = int(get_jwt_identity())

        existing = (
            MealRecord.query.filter_by(
                user_id=user_id,
                date=data["date"],
                meal_type=data["meal_type"],
            )
            .filter(MealRecord.deleted_at.is_(None))
            .first()
        )
        if existing:
            return {
                "success": False,
                "message": "record already exists for this date and meal_type",
            }, 409

        record = MealRecord(
            user_id=user_id,
            date=data["date"],
            meal_type=data["meal_type"],
            intake_level=data["intake_level"],
            note=data.get("note"),
        )
        db.session.add(record)
        db.session.commit()

        return {"success": True, "data": record.to_dict()}

    @jwt_required()
    @meal_bp.doc(security=[{"BearerAuth": []}])
    @meal_bp.arguments(MealListQuerySchema, location="query")
    @meal_bp.response(200, MealListResponseSchema)
    @meal_bp.alt_response(400, schema=ErrorResponseSchema)
    def get(self, query_args):
        user_id = int(get_jwt_identity())

        query = MealRecord.query.filter_by(user_id=user_id).filter(
            MealRecord.deleted_at.is_(None)
        )

        start = query_args.get("start")
        end = query_args.get("end")
        if start is not None:
            query = query.filter(MealRecord.date >= start)
        if end is not None:
            query = query.filter(MealRecord.date <= end)

        records = query.order_by(MealRecord.date.asc(), MealRecord.meal_type.asc()).all()
        return {
            "success": True,
            "data": [r.to_dict() for r in records],
            "total": len(records),
        }


@meal_bp.route("/<int:record_id>")
class MealItemResource(MethodView):
    @jwt_required()
    @meal_bp.doc(security=[{"BearerAuth": []}])
    @meal_bp.arguments(MealUpdateRequestSchema)
    @meal_bp.response(200, MealRecordResponseSchema)
    @meal_bp.alt_response(400, schema=ErrorResponseSchema)
    @meal_bp.alt_response(404, schema=ErrorResponseSchema)
    def put(self, data, record_id: int):
        user_id = int(get_jwt_identity())

        record = (
            MealRecord.query.filter_by(id=record_id, user_id=user_id)
            .filter(MealRecord.deleted_at.is_(None))
            .first()
        )
        if record is None:
            return {"success": False, "message": "record not found"}, 404

        if "intake_level" in data:
            record.intake_level = data["intake_level"]
        if "note" in data:
            record.note = data["note"]

        record.updated_at = datetime.now(timezone.utc)
        db.session.commit()

        return {"success": True, "data": record.to_dict()}

    @jwt_required()
    @meal_bp.doc(security=[{"BearerAuth": []}])
    @meal_bp.response(200, MessageResponseSchema)
    @meal_bp.alt_response(404, schema=ErrorResponseSchema)
    def delete(self, record_id: int):
        user_id = int(get_jwt_identity())

        record = (
            MealRecord.query.filter_by(id=record_id, user_id=user_id)
            .filter(MealRecord.deleted_at.is_(None))
            .first()
        )
        if record is None:
            return {"success": False, "message": "record not found"}, 404

        record.soft_delete()
        db.session.commit()

        return {"success": True, "message": "record deleted"}
