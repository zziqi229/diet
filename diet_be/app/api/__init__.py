from .views.auth import auth_bp
from .views.weight import weight_bp
from .views.exercise import exercise_bp
from .views.fast import fast_bp

__all__ = ["auth_bp", "weight_bp", "exercise_bp", "fast_bp"]
