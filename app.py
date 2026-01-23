#!/usr/bin/env python3

# app.py
# Copyright (c) 2026 Banshee (https://www.banshee.pro)
# License: AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "pymodules"))

from flask import Flask, g
from flask_compress import Compress
from flask_login import LoginManager
from vite_fusion import register_vite_assets

from routes import register_routes
from config import Config
from auth import User

app = Flask(
    __name__,
    static_folder=None,
    template_folder=os.path.join(os.path.dirname(__file__), "ui", "template")
)

app.config.from_object(Config)

Compress(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = None


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.before_request
def before_request():
    import secrets
    g.nonce = secrets.token_urlsafe(16)


register_vite_assets(
    app,
    dev_mode=app.config.get("DEV_MODE", True),
    dev_server_url="http://localhost:5173",
    dist_path="/ui/vue3/dist",
    manifest_path=os.path.join(os.path.dirname(__file__), "ui", "vue3", "dist", ".vite", "manifest.json"),
    nonce_provider=lambda: g.get("nonce"),
    logger=None
)

register_routes(app)


def run_development(port):
    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )


def run_production(port, workers):
    from hypercorn.config import Config as HypercornConfig
    from hypercorn.run import run

    config = HypercornConfig()
    config.bind = [f"0.0.0.0:{port}"]
    config.workers = workers
    config.accesslog = "-"
    config.application_path = "app:app"

    run(config)


if __name__ == "__main__":
    from config import Config as AppConfig, CONF
    from serverbanner import print_banner

    dev_mode = AppConfig.DEV_MODE
    port = AppConfig.PORT
    workers = AppConfig.WORKERS

    mode = "Development" if dev_mode else "Production"
    print_banner(port, mode, workers, CONF.get("using_default_credentials", False))

    if dev_mode:
        run_development(port)
    else:
        run_production(port, workers)
