import os
import time
from flask import Flask
from flask import g, request
from dotenv import load_dotenv

load_dotenv()

from .config import config_map
from .logging_setup import configure_logging
from .extensions import db, jwt
from .extensions import api as smorest_api
from .api.views.auth import auth_bp
from .api.views.weight import weight_bp
from .api.views.exercise import exercise_bp
from .api.views.meal import meal_bp


def create_app():
    app = Flask(__name__)

    env = os.getenv("FLASK_ENV", "dev")
    app.config.from_object(config_map.get(env, config_map["dev"]))
    configure_logging(app)

    app.logger.info("app boot env=%s", env)

    db.init_app(app)
    jwt.init_app(app)
    smorest_api.init_app(app)

    smorest_api.register_blueprint(auth_bp)
    smorest_api.register_blueprint(weight_bp)
    smorest_api.register_blueprint(exercise_bp)
    smorest_api.register_blueprint(meal_bp)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.before_request
    def _before_request_log():
        g._request_start = time.perf_counter()

    @app.after_request
    def _after_request_log(response):
        start = getattr(g, "_request_start", None)
        duration_ms = None
        if start is not None:
            duration_ms = (time.perf_counter() - start) * 1000

        # Keep health endpoint low-noise
        if request.path == "/health":
            return response

        app.logger.info(
            "request method=%s path=%s status=%s ip=%s duration_ms=%.2f",
            request.method,
            request.path,
            response.status_code,
            request.headers.get("X-Forwarded-For", request.remote_addr),
            duration_ms or 0.0,
        )
        return response

    @app.teardown_request
    def _teardown_request_log(exc):
        if exc is not None:
            app.logger.exception(
                "request_exception method=%s path=%s ip=%s",
                request.method,
                request.path,
                request.headers.get("X-Forwarded-For", request.remote_addr),
            )

    return app
