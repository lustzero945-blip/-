import json
from config import LEVEL_MULTIPLIER

FILE = "users.json"

def load():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_user(user_id, name="User"):
    data = load()

    if str(user_id) not in data:
        data[str(user_id)] = {
            "name": name,
            "xp": 0,
            "level": 1,
            "quiz_score": 0,
            "badges": []
        }
        save(data)

    return data[str(user_id)]

def add_xp(user_id, name, amount):
    data = load()
    user = get_user(user_id, name)

    user["xp"] += amount

    if user["xp"] >= user["level"] * LEVEL_MULTIPLIER:
        user["xp"] = 0
        user["level"] += 1

    data[str(user_id)] = user
    save(data)
    return user

def add_quiz_score(user_id, score):
    data = load()
    user = data.get(str(user_id))
    user["quiz_score"] += score
    save(data)

def leaderboard():
    data = load()
    users = list(data.values())
    users.sort(key=lambda x: (x["level"], x["xp"]), reverse=True)
    return users[:10]

def get_rank(level):
    if level < 5:
        return "🥉 Bronze"
    elif level < 10:
        return "🥈 Silver"
    elif level < 20:
        return "🥇 Gold"
    else:
        return "👑 Elite"