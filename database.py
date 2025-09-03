import json
import os

DB_FILE = "users.json"

def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

def get_user(user_id):
    users = load_users()
    return users.get(str(user_id), {"credits": 0, "plan": "free"})

def update_user(user_id, credits=None, plan=None):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        users[uid] = {"credits": 0, "plan": "free"}
    if credits is not None:
        users[uid]["credits"] = credits
    if plan is not None:
        users[uid]["plan"] = plan
    save_users(users)
