import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

from .config import config_map
from .extensions import db, jwt
from .extensions import api as smorest_api
from .api.views.auth import auth_bp
from .api.views.weight import weight_bp


def create_app():
    app = Flask(__name__)

    env = os.getenv("FLASK_ENV", "dev")
    app.config.from_object(config_map.get(env, config_map["dev"]))

    db.init_app(app)
    jwt.init_app(app)
    smorest_api.init_app(app)

    smorest_api.register_blueprint(auth_bp)
    smorest_api.register_blueprint(weight_bp)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
