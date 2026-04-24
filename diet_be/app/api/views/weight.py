from datetime import datetime, timezone

from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint

from ...extensions import db
from ...models import WeightRecord
from ..schemas import (
    ErrorResponseSchema,
    MessageResponseSchema,
    WeightCreateRequestSchema,
    WeightListQuerySchema,
    WeightListResponseSchema,
    WeightRecordResponseSchema,
    WeightUpdateRequestSchema,
)


weight_bp = Blueprint(
    "weight",
    __name__,
    url_prefix="/api/weight",
    description="Weight record APIs",
)


def _normalize_dt(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


@weight_bp.route("/")
class WeightCollectionResource(MethodView):
    @jwt_required()
    @weight_bp.doc(security=[{"BearerAuth": []}])
    @weight_bp.arguments(WeightCreateRequestSchema)
    @weight_bp.response(201, WeightRecordResponseSchema)
    @weight_bp.alt_response(400, schema=ErrorResponseSchema)
    def post(self, data):
        user_id = int(get_jwt_identity())

        record = WeightRecord(
            user_id=user_id,
            weight_kg=data["weight_kg"],
            recorded_at=_normalize_dt(data["recorded_at"]),
        )
        db.session.add(record)
        db.session.commit()

        return {"success": True, "data": record.to_dict()}

    @jwt_required()
    @weight_bp.doc(security=[{"BearerAuth": []}])
    @weight_bp.arguments(WeightListQuerySchema, location="query")
    @weight_bp.response(200, WeightListResponseSchema)
    @weight_bp.alt_response(400, schema=ErrorResponseSchema)
    def get(self, query_args):
        user_id = int(get_jwt_identity())

        query = WeightRecord.query.filter_by(user_id=user_id).filter(
            WeightRecord.deleted_at.is_(None)
        )

        start = query_args.get("start")
        end = query_args.get("end")
        if start is not None:
            query = query.filter(WeightRecord.recorded_at >= _normalize_dt(start))
        if end is not None:
            query = query.filter(WeightRecord.recorded_at <= _normalize_dt(end))

        records = query.order_by(WeightRecord.recorded_at.asc()).all()
        return {
            "success": True,
            "data": [r.to_dict() for r in records],
            "total": len(records),
        }


@weight_bp.route("/<int:record_id>")
class WeightItemResource(MethodView):
    @jwt_required()
    @weight_bp.doc(security=[{"BearerAuth": []}])
    @weight_bp.arguments(WeightUpdateRequestSchema)
    @weight_bp.response(200, WeightRecordResponseSchema)
    @weight_bp.alt_response(400, schema=ErrorResponseSchema)
    @weight_bp.alt_response(404, schema=ErrorResponseSchema)
    def put(self, data, record_id: int):
        user_id = int(get_jwt_identity())

        record = (
            WeightRecord.query.filter_by(id=record_id, user_id=user_id)
            .filter(WeightRecord.deleted_at.is_(None))
            .first()
        )
        if record is None:
            return {"success": False, "message": "record not found"}, 404

        if "weight_kg" in data:
            record.weight_kg = data["weight_kg"]
        if "recorded_at" in data:
            record.recorded_at = _normalize_dt(data["recorded_at"])

        record.updated_at = datetime.now(timezone.utc)
        db.session.commit()

        return {"success": True, "data": record.to_dict()}

    @jwt_required()
    @weight_bp.doc(security=[{"BearerAuth": []}])
    @weight_bp.response(200, MessageResponseSchema)
    @weight_bp.alt_response(404, schema=ErrorResponseSchema)
    def delete(self, record_id: int):
        user_id = int(get_jwt_identity())

        record = (
            WeightRecord.query.filter_by(id=record_id, user_id=user_id)
            .filter(WeightRecord.deleted_at.is_(None))
            .first()
        )
        if record is None:
            return {"success": False, "message": "record not found"}, 404

        record.soft_delete()
        db.session.commit()

        return {"success": True, "message": "Record deleted successfully"}
