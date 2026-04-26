from .common import ErrorResponseSchema, MessageResponseSchema
from .auth import (
    UserSchema,
    RegisterRequestSchema,
    LoginRequestSchema,
    AuthDataSchema,
    AuthResponseSchema,
)
from .weight import (
    WeightRecordSchema,
    WeightCreateRequestSchema,
    WeightUpdateRequestSchema,
    WeightRecordResponseSchema,
    WeightListQuerySchema,
    WeightListResponseSchema,
)
from .exercise import (
    ExerciseRecordSchema,
    ExerciseCreateRequestSchema,
    ExerciseUpdateRequestSchema,
    ExerciseRecordResponseSchema,
    ExerciseListQuerySchema,
    ExerciseListResponseSchema,
)
from .meal import (
    MealRecordSchema,
    MealCreateRequestSchema,
    MealUpdateRequestSchema,
    MealRecordResponseSchema,
    MealListQuerySchema,
    MealListResponseSchema,
)

__all__ = [
    "ErrorResponseSchema",
    "MessageResponseSchema",
    "UserSchema",
    "RegisterRequestSchema",
    "LoginRequestSchema",
    "AuthDataSchema",
    "AuthResponseSchema",
    "WeightRecordSchema",
    "WeightCreateRequestSchema",
    "WeightUpdateRequestSchema",
    "WeightRecordResponseSchema",
    "WeightListQuerySchema",
    "WeightListResponseSchema",
    "ExerciseRecordSchema",
    "ExerciseCreateRequestSchema",
    "ExerciseUpdateRequestSchema",
    "ExerciseRecordResponseSchema",
    "ExerciseListQuerySchema",
    "ExerciseListResponseSchema",
    "MealRecordSchema",
    "MealCreateRequestSchema",
    "MealUpdateRequestSchema",
    "MealRecordResponseSchema",
    "MealListQuerySchema",
    "MealListResponseSchema",
]
