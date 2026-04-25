from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    weight_records = db.relationship(
        "WeightRecord", back_populates="user", lazy="dynamic"
    )
    meal_records = db.relationship(
        "MealRecord", back_populates="user", lazy="dynamic"
    )
    exercise_records = db.relationship(
        "ExerciseRecord", back_populates="user", lazy="dynamic"
    )
    fast_records = db.relationship(
        "FastRecord", back_populates="user", lazy="dynamic"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at.isoformat(),
        }
