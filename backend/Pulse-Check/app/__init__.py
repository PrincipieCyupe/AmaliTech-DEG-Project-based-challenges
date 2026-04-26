import os

from flask import Flask

from app.config import Config
from app.models import db
from app.routes.monitors import monitors_bp
from app.scheduler import init_scheduler


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(monitors_bp)

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    # only start scheduler in the reloader child (or when reloader is off)
    # to avoid duplicate jobs
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        init_scheduler(app)

    return app
