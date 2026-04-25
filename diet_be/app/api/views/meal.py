from datetime import datetime, timezone

from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint

from ...extensions import db
from ...models import MealRecord
from ..schemas import (
    ErrorResponseSchema,
    MessageResponseSchema,
    MealCreateRequestSchema,
    MealListQuerySchema,
    MealListResponseSchema,
    MealRecordResponseSchema,
    MealUpdateRequestSchema,
)


meal_bp = Blueprint(
    "meal",
    __name__,
    url_prefix="/api/meal",
    description="Meal record APIs",
)


def _normalize_dt(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


@meal_bp.route("/")
class MealCollectionResource(MethodView):
    @jwt_required()
    @meal_bp.doc(security=[{"BearerAuth": []}])
    @meal_bp.arguments(MealCreateRequestSchema)
    @meal_bp.response(201, MealRecordResponseSchema)
    @meal_bp.alt_response(400, schema=ErrorResponseSchema)
    def post(self, data):
        user_id = int(get_jwt_identity())

        record = MealRecord(
            user_id=user_id,
            content=data["content"],
            satiety=data["satiety"],
            meal_type=data["meal_type"],
            eaten_at=_normalize_dt(data["eaten_at"]),
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
            query = query.filter(MealRecord.eaten_at >= _normalize_dt(start))
        if end is not None:
            query = query.filter(MealRecord.eaten_at <= _normalize_dt(end))

        records = query.order_by(MealRecord.eaten_at.asc()).all()
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

        if "content" in data:
            record.content = data["content"]
        if "satiety" in data:
            record.satiety = data["satiety"]
        if "meal_type" in data:
            record.meal_type = data["meal_type"]
        if "eaten_at" in data:
            record.eaten_at = _normalize_dt(data["eaten_at"])

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
