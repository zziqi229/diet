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
from .meal import (
    MealRecordSchema,
    MealCreateRequestSchema,
    MealUpdateRequestSchema,
    MealRecordResponseSchema,
    MealListQuerySchema,
    MealListResponseSchema,
)
from .exercise import (
    ExerciseRecordSchema,
    ExerciseCreateRequestSchema,
    ExerciseUpdateRequestSchema,
    ExerciseRecordResponseSchema,
    ExerciseListQuerySchema,
    ExerciseListResponseSchema,
)
from .fast import (
    FastRecordSchema,
    FastCreateRequestSchema,
    FastRecordResponseSchema,
    FastListQuerySchema,
    FastListResponseSchema,
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
    "MealRecordSchema",
    "MealCreateRequestSchema",
    "MealUpdateRequestSchema",
    "MealRecordResponseSchema",
    "MealListQuerySchema",
    "MealListResponseSchema",
    "ExerciseRecordSchema",
    "ExerciseCreateRequestSchema",
    "ExerciseUpdateRequestSchema",
    "ExerciseRecordResponseSchema",
    "ExerciseListQuerySchema",
    "ExerciseListResponseSchema",
    "FastRecordSchema",
    "FastCreateRequestSchema",
    "FastRecordResponseSchema",
    "FastListQuerySchema",
    "FastListResponseSchema",
]
