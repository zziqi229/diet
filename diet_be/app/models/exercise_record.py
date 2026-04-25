from datetime import datetime, timezone
from ..extensions import db


class ExerciseRecord(db.Model):
    __tablename__ = "exercise_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content = db.Column(
        db.Text,
        nullable=False,
        comment="Description of the exercise activity",
    )
    exercised_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        comment="User-supplied timestamp when exercise took place",
    )
    duration_minutes = db.Column(
        db.Integer,
        nullable=False,
        comment="Duration of exercise in minutes",
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

    user = db.relationship("User", back_populates="exercise_records")

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "exercised_at": self.exercised_at.isoformat(),
            "duration_minutes": self.duration_minutes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
