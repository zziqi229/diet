from datetime import datetime, timezone
from ..extensions import db


class WeightRecord(db.Model):
    __tablename__ = "weight_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    weight_kg = db.Column(db.Numeric(5, 2), nullable=False)
    recorded_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        comment="User-supplied timestamp of the measurement",
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    deleted_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Soft-delete timestamp; NULL means not deleted",
    )

    user = db.relationship("User", back_populates="weight_records")

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "weight_kg": float(self.weight_kg),
            "recorded_at": self.recorded_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
