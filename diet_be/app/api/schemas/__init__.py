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
]
