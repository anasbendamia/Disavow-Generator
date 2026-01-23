# pymodules/config.py
# Copyright (c) 2026 Banshee (https://www.banshee.pro)
# License: AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

import os
import configparser

from pathlib import Path

import bcrypt

BASE_DIR = Path(__file__).parent.parent.resolve()
CONF_DIR = BASE_DIR / "conf"
CONF_DIR.mkdir(exist_ok=True)
CONF_FILE = CONF_DIR / "disavow.conf"

DEFAULT_USERNAME = "user"
DEFAULT_PASSWORD = "passwd"


def get_or_create_secret_key():
    import secrets as secrets_module

    config = configparser.ConfigParser()
    if CONF_FILE.exists():
        config.read(CONF_FILE)

    if config.has_option("server", "secret_key"):
        return config.get("server", "secret_key")

    secret_key = secrets_module.token_hex(32)

    if not config.has_section("server"):
        config.add_section("server")
    config.set("server", "secret_key", secret_key)

    with open(CONF_FILE, "w") as f:
        config.write(f)

    return secret_key


def generate_default_conf():
    import secrets as secrets_module

    config = configparser.ConfigParser()

    password_hash = bcrypt.hashpw(
        DEFAULT_PASSWORD.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    secret_key = secrets_module.token_hex(32)

    config.add_section("server")
    config.set("server", "port", "44444")
    config.set("server", "mode", "production")
    config.set("server", "workers", "4")
    config.set("server", "secret_key", secret_key)

    config.add_section("paths")
    config.set("paths", "input_dir", "__DISAVOW_DATA__/INGEST")
    config.set("paths", "output_dir", "__DISAVOW_DATA__/OUTPUT")
    config.set("paths", "whitelist_file", "__DISAVOW_DATA__/whitelist.txt")

    config.add_section("auth")
    config.set("auth", "username", DEFAULT_USERNAME)
    config.set("auth", "password_hash", password_hash)

    with open(CONF_FILE, "w") as f:
        f.write("# Disavow Generator Configuration\n")
        f.write("# https://www.banshee.pro\n\n")
        config.write(f)


def is_default_password(password_hash: str) -> bool:
    if not password_hash:
        return True
    try:
        return bcrypt.checkpw(
            DEFAULT_PASSWORD.encode("utf-8"),
            password_hash.encode("utf-8")
        )
    except Exception:
        return False


def load_conf():
    config = configparser.ConfigParser()

    conf = {
        "port": 44444,
        "mode": "production",
        "workers": 4,
        "input_dir": BASE_DIR / "__DISAVOW_DATA__" / "INGEST",
        "output_dir": BASE_DIR / "__DISAVOW_DATA__" / "OUTPUT",
        "whitelist_file": BASE_DIR / "__DISAVOW_DATA__" / "whitelist.txt",
        "auth_username": None,
        "auth_password_hash": None,
        "using_default_credentials": False,
    }

    if not CONF_FILE.exists():
        generate_default_conf()

    if CONF_FILE.exists():
        config.read(CONF_FILE)

        if config.has_section("server"):
            conf["port"] = config.getint("server", "port", fallback=44444)
            conf["mode"] = config.get("server", "mode", fallback="development")
            conf["workers"] = config.getint("server", "workers", fallback=4)

        if config.has_section("paths"):
            input_dir = config.get("paths", "input_dir", fallback=None)
            output_dir = config.get("paths", "output_dir", fallback=None)
            whitelist = config.get("paths", "whitelist_file", fallback=None)

            if input_dir:
                conf["input_dir"] = (BASE_DIR / input_dir).resolve()
            if output_dir:
                conf["output_dir"] = (BASE_DIR / output_dir).resolve()
            if whitelist:
                conf["whitelist_file"] = (BASE_DIR / whitelist).resolve()

        if config.has_section("auth"):
            conf["auth_username"] = config.get("auth", "username", fallback=None)
            conf["auth_password_hash"] = config.get("auth", "password_hash", fallback=None)

    # Check if using default credentials
    conf["using_default_credentials"] = (
        conf["auth_username"] == DEFAULT_USERNAME and
        is_default_password(conf["auth_password_hash"])
    )

    return conf


def update_auth_config(username=None, password_hash=None):
    config = configparser.ConfigParser()

    if CONF_FILE.exists():
        config.read(CONF_FILE)

    if not config.has_section("auth"):
        config.add_section("auth")

    if username is not None:
        config.set("auth", "username", username)
        CONF["auth_username"] = username

    if password_hash is not None:
        config.set("auth", "password_hash", password_hash)
        CONF["auth_password_hash"] = password_hash

    # Update default credentials flag
    CONF["using_default_credentials"] = (
        CONF["auth_username"] == DEFAULT_USERNAME and
        is_default_password(CONF["auth_password_hash"])
    )

    with open(CONF_FILE, "w") as f:
        config.write(f)


CONF = load_conf()


class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY") or get_or_create_secret_key()
    DEV_MODE = CONF["mode"] == "development"
    PORT = CONF["port"]
    WORKERS = CONF["workers"]

    OUTPUT_FOLDER = Path(CONF["output_dir"])
    INPUT_FOLDER = Path(CONF["input_dir"])
    WHITELIST_FILE = Path(CONF["whitelist_file"])

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    INPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max
    ALLOWED_EXTENSIONS = {"xlsx", "xls", "csv", "txt"}
