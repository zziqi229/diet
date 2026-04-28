import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    API_TITLE = "Diet Backend API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    API_SPEC_OPTIONS = {
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        }
    }

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_TIMEZONE = os.getenv("LOG_TIMEZONE", "Asia/Shanghai")
    LOG_DIR = os.getenv("LOG_DIR", "/var/log/diet")
    LOG_TO_FILE = os.getenv("LOG_TO_FILE", "true")
    LOG_FILE_BASENAME = os.getenv("LOG_FILE_BASENAME", "diet-be")
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "14"))


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False


config_map = {
    "dev": DevConfig,
    "prod": ProdConfig,
}
