from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint

from ...extensions import db
from ...models import FastRecord
from ..schemas import (
    ErrorResponseSchema,
    MessageResponseSchema,
    FastCreateRequestSchema,
    FastListQuerySchema,
    FastListResponseSchema,
    FastRecordResponseSchema,
)


fast_bp = Blueprint(
    "fast",
    __name__,
    url_prefix="/api/fast",
    description="Fasting record APIs",
)


@fast_bp.route("/")
class FastCollectionResource(MethodView):
    @jwt_required()
    @fast_bp.doc(security=[{"BearerAuth": []}])
    @fast_bp.arguments(FastCreateRequestSchema)
    @fast_bp.response(201, FastRecordResponseSchema)
    @fast_bp.alt_response(400, schema=ErrorResponseSchema)
    def post(self, data):
        user_id = int(get_jwt_identity())

        record = FastRecord(
            user_id=user_id,
            date=data["date"],
            meal_type=data["meal_type"],
            note=data.get("note"),
        )
        db.session.add(record)
        db.session.commit()

        return {"success": True, "data": record.to_dict()}

    @jwt_required()
    @fast_bp.doc(security=[{"BearerAuth": []}])
    @fast_bp.arguments(FastListQuerySchema, location="query")
    @fast_bp.response(200, FastListResponseSchema)
    @fast_bp.alt_response(400, schema=ErrorResponseSchema)
    def get(self, query_args):
        user_id = int(get_jwt_identity())

        query = FastRecord.query.filter_by(user_id=user_id).filter(
            FastRecord.deleted_at.is_(None)
        )

        start = query_args.get("start")
        end = query_args.get("end")
        if start is not None:
            query = query.filter(FastRecord.date >= start)
        if end is not None:
            query = query.filter(FastRecord.date <= end)

        records = query.order_by(FastRecord.date.asc()).all()
        return {
            "success": True,
            "data": [r.to_dict() for r in records],
            "total": len(records),
        }


@fast_bp.route("/<int:record_id>")
class FastItemResource(MethodView):
    @jwt_required()
    @fast_bp.doc(security=[{"BearerAuth": []}])
    @fast_bp.response(200, MessageResponseSchema)
    @fast_bp.alt_response(404, schema=ErrorResponseSchema)
    def delete(self, record_id: int):
        user_id = int(get_jwt_identity())

        record = (
            FastRecord.query.filter_by(id=record_id, user_id=user_id)
            .filter(FastRecord.deleted_at.is_(None))
            .first()
        )
        if record is None:
            return {"success": False, "message": "record not found"}, 404

        record.soft_delete()
        db.session.commit()
        return {"success": True, "message": "record deleted"}
