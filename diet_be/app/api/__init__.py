from .views.auth import auth_bp
from .views.weight import weight_bp
from .views.exercise import exercise_bp
from .views.meal import meal_bp

__all__ = ["auth_bp", "weight_bp", "exercise_bp", "meal_bp"]
