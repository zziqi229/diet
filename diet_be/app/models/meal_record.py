import enum
from datetime import datetime, timezone
from ..extensions import db


class MealType(enum.Enum):
    breakfast = "breakfast"   # 早饭
    lunch = "lunch"           # 午饭
    dinner = "dinner"         # 晚饭
    late_night = "late_night" # 夜宵
    snack = "snack"           # 零食


class MealRecord(db.Model):
    __tablename__ = "meal_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content = db.Column(
        db.Text,
        nullable=False,
        comment="Description of what was eaten",
    )
    satiety = db.Column(
        db.SmallInteger,
        nullable=False,
        comment="Fullness level from 0 (empty) to 15 (stuffed)",
    )
    meal_type = db.Column(
        db.Enum(MealType),
        nullable=False,
        comment="Which meal of the day: breakfast/lunch/dinner/late_night/snack",
    )
    eaten_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        comment="User-supplied timestamp of the meal",
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
            "content": self.content,
            "satiety": self.satiety,
            "meal_type": self.meal_type.value,
            "eaten_at": self.eaten_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
