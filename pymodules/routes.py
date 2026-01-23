# pymodules/routes.py
# Copyright (c) 2026 Banshee (https://www.banshee.pro)
# License: AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

import json
import base64

from pathlib import Path
from flask import render_template, request, jsonify, send_file, g, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from config import Config, update_auth_config, CONF
from disavow_service import DisavowService
from auth import User, generate_password_hash


def b64encode(data):
    return base64.b64encode(json.dumps(data).encode()).decode()


def register_routes(app):

    service = DisavowService()

    app.jinja_env.filters["b64encode"] = b64encode

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("index"))

        error = None
        if request.method == "POST":
            username = request.form.get("username", "")
            password = request.form.get("password", "")

            user = User.authenticate(username, password)
            if user:
                login_user(user)
                next_page = request.args.get("next")
                return redirect(next_page or url_for("index"))
            else:
                error = "Invalid username or password"

        return render_template("login.html", error=error, nonce=g.get("nonce", ""))

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    @app.route("/")
    @login_required
    def index():
        stats = service.get_stats()

        return render_template(
            "index.html",
            nonce=g.get("nonce", ""),
            stats=b64encode(stats),
            whitelist=b64encode(service.get_whitelist()),
            username=current_user.username
        )

    def api_login_required(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"error": "Unauthorized"}), 401
            return f(*args, **kwargs)
        return decorated_function

    @app.route("/api/upload", methods=["POST"])
    @api_login_required
    def upload_file():
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Allowed: xlsx, xls, csv, txt"}), 400

        filename = secure_filename(file.filename)
        filepath = Config.INPUT_FOLDER / filename
        file.save(str(filepath))

        return jsonify({
            "success": True,
            "filename": filename,
            "message": f"File {filename} uploaded successfully"
        })

    @app.route("/api/process", methods=["POST"])
    @api_login_required
    def process_files():
        result = service.process_files()
        return jsonify(result)

    @app.route("/api/stats")
    @api_login_required
    def get_stats():
        return jsonify(service.get_stats())

    @app.route("/api/whitelist", methods=["GET"])
    @api_login_required
    def get_whitelist():
        return jsonify(service.get_whitelist())

    @app.route("/api/whitelist", methods=["POST"])
    @api_login_required
    def update_whitelist():
        data = request.get_json()
        domains = data.get("domains", [])
        service.save_whitelist(domains)
        return jsonify({"success": True})

    @app.route("/api/whitelist/add", methods=["POST"])
    @api_login_required
    def add_to_whitelist():
        data = request.get_json()
        domain = data.get("domain", "").strip().lower()
        if domain:
            service.add_to_whitelist(domain)
            return jsonify({"success": True, "domain": domain})
        return jsonify({"error": "No domain provided"}), 400

    @app.route("/api/files")
    @api_login_required
    def list_files():
        files = service.list_input_files()
        return jsonify(files)

    @app.route("/api/files/<filename>", methods=["DELETE"])
    @api_login_required
    def delete_file(filename):
        filepath = Config.INPUT_FOLDER / secure_filename(filename)
        if filepath.exists():
            filepath.unlink()
            return jsonify({"success": True})
        return jsonify({"error": "File not found"}), 404

    @app.route("/api/outputs")
    @api_login_required
    def list_outputs():
        outputs = service.list_output_files()
        return jsonify(outputs)

    @app.route("/api/download/<filename>")
    @api_login_required
    def download_file(filename):
        filepath = Config.OUTPUT_FOLDER / secure_filename(filename)
        if filepath.exists():
            return send_file(filepath, as_attachment=True)
        return jsonify({"error": "File not found"}), 404

    @app.route("/api/preview/<filename>")
    @api_login_required
    def preview_file(filename):
        filepath = Config.OUTPUT_FOLDER / secure_filename(filename)
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return jsonify({"content": content})
        return jsonify({"error": "File not found"}), 404

    @app.route("/api/outputs/<filename>", methods=["DELETE"])
    @api_login_required
    def delete_output(filename):
        filepath = Config.OUTPUT_FOLDER / secure_filename(filename)
        if filepath.exists():
            filepath.unlink()
            return jsonify({"success": True})
        return jsonify({"error": "File not found"}), 404

    @app.route("/api/settings/credentials", methods=["POST"])
    @api_login_required
    def change_credentials():
        import bcrypt
        from config import load_conf

        data = request.get_json()
        current_password = data.get("current_password", "")
        new_username = data.get("new_username", "").strip()
        new_password = data.get("new_password")  # Can be None to keep current

        if not current_password:
            return jsonify({"error": "Current password is required"}), 400

        conf = load_conf()
        stored_hash = conf.get("auth_password_hash", "")
        try:
            if not bcrypt.checkpw(current_password.encode("utf-8"), stored_hash.encode("utf-8")):
                return jsonify({"error": "Current password is incorrect"}), 400
        except Exception:
            return jsonify({"error": "Current password is incorrect"}), 400

        if not new_username:
            return jsonify({"error": "Username cannot be empty"}), 400
        if len(new_username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400

        if new_password and len(new_password) < 4:
            return jsonify({"error": "New password must be at least 4 characters"}), 400

        update_auth_config(username=new_username)

        if new_password:
            new_hash = generate_password_hash(new_password)
            update_auth_config(password_hash=new_hash)

        # Logout user
        logout_user()

        return jsonify({"success": True})

    @app.route("/ui/vue3/dist/<path:filename>")
    def serve_dist(filename):
        dist_path = Path(__file__).parent.parent / "ui" / "vue3" / "dist"
        return send_file(dist_path / filename)

    @app.route("/ui/static/<path:filename>")
    def serve_static(filename):
        static_path = Path(__file__).parent.parent / "ui" / "static"
        return send_file(static_path / filename)


def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS
