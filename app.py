"""Main Flask application for Adik Tiri yang Nakal visual novel."""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import eventlet
from flask import Flask, jsonify, redirect, render_template, request, send_file, session, url_for
from flask_caching import Cache
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_socketio import SocketIO, emit, join_room
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from story_engine.achievement_system import AchievementSystem
from story_engine.flag_manager import FlagManager
from story_engine.inventory_system import InventorySystem
from story_engine.relationship_system import RelationshipSystem
from story_engine.save_manager import SaveManager
from story_engine.story_loader import StoryLoader

eventlet.monkey_patch()

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"

app = Flask(__name__)
with CONFIG_PATH.open("r", encoding="utf-8") as f:
    config: dict[str, Any] = json.load(f)

app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY", config.get("secret_key", "dev-secret")),
    SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", config.get("database_url", "sqlite:///data/game.db")),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,
)

Path(BASE_DIR / "data").mkdir(exist_ok=True)
Path(BASE_DIR / "logs").mkdir(exist_ok=True)

logging.basicConfig(
    filename=BASE_DIR / "logs" / "app.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
cache = Cache(app, config={"CACHE_TYPE": "SimpleCache"})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SaveSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    slot = db.Column(db.Integer, nullable=False)
    chapter = db.Column(db.Integer, default=1)
    scene_id = db.Column(db.String(120), default="ch1_scene_1")
    payload = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    music_volume = db.Column(db.Float, default=0.8)
    sfx_volume = db.Column(db.Float, default=0.8)
    text_speed = db.Column(db.Integer, default=40)
    language = db.Column(db.String(10), default="id")


class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    key = db.Column(db.String(120), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    item_id = db.Column(db.String(120), nullable=False)
    qty = db.Column(db.Integer, default=1)


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.get(User, int(user_id))


story_loader = StoryLoader(BASE_DIR / "story_data")
flag_manager = FlagManager()
relationship_system = RelationshipSystem()
inventory_system = InventorySystem(BASE_DIR / "story_data" / "items" / "items.json")
achievement_system = AchievementSystem(BASE_DIR / "story_data" / "events" / "achievements.json")
save_manager = SaveManager()


@app.context_processor
def inject_config() -> dict[str, Any]:
    return {"game_config": config}


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register() -> str:
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        if User.query.filter((User.username == username) | (User.email == email)).first():
            return render_template("register.html", error="Username/email sudah dipakai")

        user = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        logger.info("User registered: %s", username)
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login() -> str:
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return render_template("login.html", error="Login gagal")

        login_user(user)
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.get("/logout")
@login_required
def logout() -> Any:
    logout_user()
    return redirect(url_for("index"))


@app.get("/dashboard")
@login_required
def dashboard() -> str:
    saves = SaveSlot.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", saves=saves)


@app.get("/game")
@login_required
def game() -> str:
    return render_template("game.html")


@app.get("/gallery")
@login_required
def gallery() -> str:
    return render_template("gallery.html")


@app.get("/achievements")
@login_required
def achievements_page() -> str:
    return render_template("achievements.html")


@app.get("/settings")
@login_required
def settings_page() -> str:
    return render_template("settings.html")


@app.get("/api/scene/<scene_id>")
@login_required
def get_scene(scene_id: str):
    scene = story_loader.get_scene(scene_id)
    if scene is None:
        return jsonify({"error": "Scene tidak ditemukan"}), 404
    return jsonify(scene)


@app.post("/api/choice")
@login_required
def process_choice():
    data = request.get_json(force=True)
    current_scene = data.get("scene_id")
    choice_id = data.get("choice_id")
    game_state = data.get("state", {})

    result = story_loader.process_choice(current_scene, choice_id, game_state)
    if "error" in result:
        return jsonify(result), 400

    achievements = achievement_system.evaluate(game_state)
    for ach_key in achievements:
        if not UserAchievement.query.filter_by(user_id=current_user.id, key=ach_key).first():
            db.session.add(UserAchievement(user_id=current_user.id, key=ach_key))
            socketio.emit("achievement_unlocked", {"achievement": ach_key}, room=f"user-{current_user.id}")

    db.session.commit()
    return jsonify(result)


@app.post("/api/save")
@login_required
def save_game():
    data = request.get_json(force=True)
    slot = int(data.get("slot", 1))
    payload = save_manager.pack_state(data.get("state", {}))

    save = SaveSlot.query.filter_by(user_id=current_user.id, slot=slot).first()
    if save is None:
        save = SaveSlot(user_id=current_user.id, slot=slot, payload=payload)
        db.session.add(save)
    else:
        save.payload = payload

    save.scene_id = data.get("scene_id", "ch1_scene_1")
    save.chapter = int(data.get("chapter", 1))
    db.session.commit()
    return jsonify({"status": "ok", "slot": slot})


@app.get("/api/load/<int:slot>")
@login_required
def load_game(slot: int):
    save = SaveSlot.query.filter_by(user_id=current_user.id, slot=slot).first()
    if not save:
        return jsonify({"error": "Slot kosong"}), 404
    state = save_manager.unpack_state(save.payload)
    return jsonify({"slot": slot, "chapter": save.chapter, "scene_id": save.scene_id, "state": state})


@app.get("/api/inventory")
@login_required
def get_inventory():
    rows = UserInventory.query.filter_by(user_id=current_user.id).all()
    payload = [{"item_id": row.item_id, "qty": row.qty} for row in rows]
    return jsonify(inventory_system.enrich_inventory(payload))


@app.post("/api/inventory/use")
@login_required
def use_inventory_item():
    data = request.get_json(force=True)
    item_id = data.get("item_id")
    row = UserInventory.query.filter_by(user_id=current_user.id, item_id=item_id).first()
    if not row or row.qty <= 0:
        return jsonify({"error": "Item tidak tersedia"}), 404

    row.qty -= 1
    if row.qty == 0:
        db.session.delete(row)
    db.session.commit()
    return jsonify({"status": "used", "item_id": item_id})


@app.get("/api/achievements")
@login_required
def get_achievements():
    unlocked = {x.key for x in UserAchievement.query.filter_by(user_id=current_user.id).all()}
    all_ach = achievement_system.list_all()
    return jsonify([{"id": k, **v, "unlocked": k in unlocked} for k, v in all_ach.items()])


@app.get("/api/gallery")
@login_required
def get_gallery():
    return jsonify(story_loader.get_gallery_data())


@app.get("/api/characters")
@login_required
def get_characters():
    return jsonify(story_loader.characters)


@app.post("/api/settings")
@login_required
def update_settings():
    data = request.get_json(force=True)
    settings = UserSetting.query.filter_by(user_id=current_user.id).first()
    if settings is None:
        settings = UserSetting(user_id=current_user.id)
        db.session.add(settings)

    settings.music_volume = float(data.get("music_volume", settings.music_volume))
    settings.sfx_volume = float(data.get("sfx_volume", settings.sfx_volume))
    settings.text_speed = int(data.get("text_speed", settings.text_speed))
    settings.language = data.get("language", settings.language)
    db.session.commit()
    return jsonify({"status": "updated"})


@app.post("/api/export-save/<int:slot>")
@login_required
def export_save(slot: int):
    save = SaveSlot.query.filter_by(user_id=current_user.id, slot=slot).first()
    if not save:
        return jsonify({"error": "Slot kosong"}), 404

    out_path = BASE_DIR / "temp" / f"save_{current_user.id}_{slot}.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps({"slot": slot, "payload": save.payload}, ensure_ascii=False), encoding="utf-8")
    return send_file(out_path, as_attachment=True)


@app.post("/api/import-save")
@login_required
def import_save():
    uploaded = request.files.get("file")
    if uploaded is None:
        return jsonify({"error": "File tidak ditemukan"}), 400

    data = json.loads(uploaded.read().decode("utf-8"))
    slot = int(data["slot"])
    save = SaveSlot.query.filter_by(user_id=current_user.id, slot=slot).first()
    if save is None:
        save = SaveSlot(user_id=current_user.id, slot=slot, payload=data["payload"])
        db.session.add(save)
    else:
        save.payload = data["payload"]

    db.session.commit()
    return jsonify({"status": "imported", "slot": slot})


@socketio.on("join_game")
def ws_join_game(data: dict[str, Any]):
    if not current_user.is_authenticated:
        return
    room = f"user-{current_user.id}"
    join_room(room)
    emit("scene_update", {"message": "connected", "session_id": data.get("session_id")})


@socketio.on("player_action")
def ws_player_action(data: dict[str, Any]):
    emit("expression_change", {"character": "rina", "expression": "teasing"}, room=f"user-{current_user.id}")


@socketio.on("save_game")
def ws_save_game(data: dict[str, Any]):
    emit("background_change", {"background": "living_room_day.png", "slot": data.get("slot", 1)})


@app.cli.command("init-db")
def init_db_command() -> None:
    db.create_all()
    print("Database initialized")


def bootstrap() -> None:
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    bootstrap()
    socketio.run(app, host="0.0.0.0", port=5000, debug=config.get("debug", True))
