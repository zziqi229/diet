from datetime import datetime, timezone

from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint

from ...extensions import db
from ...models import ExerciseRecord
from ..schemas import (
    ErrorResponseSchema,
    MessageResponseSchema,
    ExerciseCreateRequestSchema,
    ExerciseListQuerySchema,
    ExerciseListResponseSchema,
    ExerciseRecordResponseSchema,
    ExerciseUpdateRequestSchema,
)


exercise_bp = Blueprint(
    "exercise",
    __name__,
    url_prefix="/api/exercise",
    description="Exercise record APIs",
)


def _normalize_dt(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


@exercise_bp.route("/")
class ExerciseCollectionResource(MethodView):
    @jwt_required()
    @exercise_bp.doc(security=[{"BearerAuth": []}])
    @exercise_bp.arguments(ExerciseCreateRequestSchema)
    @exercise_bp.response(201, ExerciseRecordResponseSchema)
    @exercise_bp.alt_response(400, schema=ErrorResponseSchema)
    def post(self, data):
        user_id = int(get_jwt_identity())

        record = ExerciseRecord(
            user_id=user_id,
            content=data["content"],
            exercised_at=_normalize_dt(data["exercised_at"]),
            duration_minutes=data["duration_minutes"],
        )
        db.session.add(record)
        db.session.commit()

        return {"success": True, "data": record.to_dict()}

    @jwt_required()
    @exercise_bp.doc(security=[{"BearerAuth": []}])
    @exercise_bp.arguments(ExerciseListQuerySchema, location="query")
    @exercise_bp.response(200, ExerciseListResponseSchema)
    @exercise_bp.alt_response(400, schema=ErrorResponseSchema)
    def get(self, query_args):
        user_id = int(get_jwt_identity())

        query = ExerciseRecord.query.filter_by(user_id=user_id).filter(
            ExerciseRecord.deleted_at.is_(None)
        )

        start = query_args.get("start")
        end = query_args.get("end")
        if start is not None:
            query = query.filter(ExerciseRecord.exercised_at >= _normalize_dt(start))
        if end is not None:
            query = query.filter(ExerciseRecord.exercised_at <= _normalize_dt(end))

        records = query.order_by(ExerciseRecord.exercised_at.asc()).all()
        return {
            "success": True,
            "data": [r.to_dict() for r in records],
            "total": len(records),
        }


@exercise_bp.route("/<int:record_id>")
class ExerciseItemResource(MethodView):
    @jwt_required()
    @exercise_bp.doc(security=[{"BearerAuth": []}])
    @exercise_bp.arguments(ExerciseUpdateRequestSchema)
    @exercise_bp.response(200, ExerciseRecordResponseSchema)
    @exercise_bp.alt_response(400, schema=ErrorResponseSchema)
    @exercise_bp.alt_response(404, schema=ErrorResponseSchema)
    def put(self, data, record_id: int):
        user_id = int(get_jwt_identity())

        record = (
            ExerciseRecord.query.filter_by(id=record_id, user_id=user_id)
            .filter(ExerciseRecord.deleted_at.is_(None))
            .first()
        )
        if record is None:
            return {"success": False, "message": "record not found"}, 404

        if "content" in data:
            record.content = data["content"]
        if "exercised_at" in data:
            record.exercised_at = _normalize_dt(data["exercised_at"])
        if "duration_minutes" in data:
            record.duration_minutes = data["duration_minutes"]

        db.session.commit()
        return {"success": True, "data": record.to_dict()}

    @jwt_required()
    @exercise_bp.doc(security=[{"BearerAuth": []}])
    @exercise_bp.response(200, MessageResponseSchema)
    @exercise_bp.alt_response(404, schema=ErrorResponseSchema)
    def delete(self, record_id: int):
        user_id = int(get_jwt_identity())

        record = (
            ExerciseRecord.query.filter_by(id=record_id, user_id=user_id)
            .filter(ExerciseRecord.deleted_at.is_(None))
            .first()
        )
        if record is None:
            return {"success": False, "message": "record not found"}, 404

        record.soft_delete()
        db.session.commit()
        return {"success": True, "message": "deleted"}
