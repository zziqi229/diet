from datetime import datetime, timezone

from ..extensions import db


class MealRecord(db.Model):
    __tablename__ = "meal_records"

    MEAL_TYPES = ("breakfast", "lunch", "dinner")
    INTAKE_LEVELS = ("fast", "normal", "feast")

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(16), nullable=False)
    intake_level = db.Column(db.String(16), nullable=False)
    note = db.Column(db.Text, nullable=True, default=None)
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
    )

    user = db.relationship("User", back_populates="meal_records")

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date.isoformat(),
            "meal_type": self.meal_type,
            "intake_level": self.intake_level,
            "note": self.note,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
