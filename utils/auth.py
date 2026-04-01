# utils/auth.py
import json, bcrypt, base64
from datetime import datetime
from pathlib import Path

_BASE      = Path(__file__).parent.parent / "data"
USERS_FILE = _BASE / "users.json"

def _load() -> dict:
    if not USERS_FILE.exists():
        USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        return {}
    try:    return json.loads(USERS_FILE.read_text(encoding="utf-8"))
    except: return {}

def _save(u: dict):
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps(u, indent=2), encoding="utf-8")

def register_user(name, email, password, role="Student"):
    users = _load()
    if email in users:
        return False, "Account already exists."
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[email] = {
        "name": name, "email": email, "password": hashed, "role": role,
        "avatar": "".join(w[0].upper() for w in name.split()[:2]),
        "photo": None, "bio": "",
        "created_at": datetime.now().isoformat(),
    }
    _save(users)
    return True, "Account created!"

def login_user(email, password):
    users = _load()
    if email not in users:
        return False, "No account found."
    u = users[email]
    if not bcrypt.checkpw(password.encode(), u["password"].encode()):
        return False, "Incorrect password."
    profile = {k: v for k, v in u.items() if k != "password"}
    profile["login_at"] = datetime.now().isoformat()
    return True, profile

def update_profile(email, name=None, bio=None, photo_bytes=None, role=None):
    users = _load()
    if email not in users:
        return False, "User not found."
    u = users[email]
    if name:  u["name"] = name; u["avatar"] = "".join(w[0].upper() for w in name.split()[:2])
    if bio is not None: u["bio"] = bio
    if role:  u["role"] = role
    if photo_bytes: u["photo"] = base64.b64encode(photo_bytes).decode()
    _save(users)
    profile = {k: v for k, v in u.items() if k != "password"}
    return True, profile

def get_user(email):
    users = _load()
    if email not in users: return None
    return {k: v for k, v in users[email].items() if k != "password"}

def seed_demo():
    for name, email, pw, role in [
        ("Alex Johnson",    "student@studyai.com", "demo123",  "Student"),
        ("Dr. Priya Menon", "admin@studyai.com",   "admin123", "Educator"),
    ]:
        if email not in _load():
            register_user(name, email, pw, role)
