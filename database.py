users = {}

def get_user(user_id, name):
    if user_id not in users:
        users[user_id] = {
            "name": name,
            "xp": 0,
            "level": 1,
            "quiz_score": 0
        }
    return users[user_id]

def add_xp(user_id, name, amount):
    user = get_user(user_id, name)
    user["xp"] += amount
    user["level"] = user["xp"] // 50 + 1

def add_quiz_score(user_id, score):
    users[user_id]["quiz_score"] += score

def leaderboard():
    return sorted(users.values(), key=lambda x: x["level"], reverse=True)[:10]

def get_rank(level):
    if level < 5:
        return "Beginner"
    elif level < 10:
        return "Intermediate"
    else:
        return "Pro"
