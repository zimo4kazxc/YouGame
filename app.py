from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Временное хранилище в памяти
users_db = {
    "+000 000": {
        "phone": "+000 000",
        "first_name": "Поддержка",
        "last_name": "WebTest",
        "username": "support",
        "bio": "Официальная поддержка WebTest.",
        "avatar": "",
        "code": "2222",
        "is_support": True,
    }
}

messages_db = []  # Список всех сообщений: {id, sender, recipient, text, timestamp}


@app.route("/api/auth/send_code", methods=["POST"])
def send_code():
  data = request.json
  phone = data.get("phone")

  if not phone:
    return jsonify({"error": "Укажите номер телефона"}), 400

  # Определяем тестовые коды
  if phone == "+999 999":
    code = "1111"
  elif phone == "+000 000":
    code = "2222"
  else:
    code = "1488"  # Универсальный код для остальных

  return jsonify({"success": True, "code": code})


@app.route("/api/auth/verify", methods=["POST"])
def verify():
  data = request.json
  phone = data.get("phone")
  code = data.get("code")

  expected_code = (
      "1111"
      if phone == "+999 999"
      else ("2222" if phone == "+000 000" else "1488")
  )

  if code != expected_code:
    return jsonify({"error": "Неверный код подтверждения"}), 400

  user_exists = phone in users_db
  return jsonify({"success": True, "exists": user_exists, "phone": phone})


@app.route("/api/users/register", methods=["POST"])
def register():
  data = request.json
  phone = data.get("phone")

  users_db[phone] = {
      "phone": phone,
      "first_name": data.get("first_name", "Имя"),
      "last_name": data.get("last_name", ""),
      "username": data.get("username", f"user_{phone[-4:]}"),
      "bio": "",
      "avatar": data.get("avatar", ""),
      "is_support": False,
  }
  return jsonify({"success": True, "user": users_db[phone]})


@app.route("/api/users/profile", methods=["GET", "PUT"])
def profile():
  phone = request.args.get("phone")
  if phone not in users_db:
    return jsonify({"error": "Пользователь не найден"}), 404

  if request.method == "GET":
    return jsonify(users_db[phone])

  data = request.json
  user = users_db[phone]
  user["first_name"] = data.get("first_name", user["first_name"])
  user["last_name"] = data.get("last_name", user["last_name"])
  user["bio"] = data.get("bio", user["bio"])
  user["avatar"] = data.get("avatar", user["avatar"])
  user["username"] = data.get("username", user["username"])

  return jsonify({"success": True, "user": user})


@app.route("/api/users/search", methods=["GET"])
def search_users():
  query = request.args.get("q", "").lower().strip("@")
  results = []
  for u in users_db.values():
    if query in u["username"].lower() or query in u["phone"].lower():
      results.append(u)
  return jsonify(results)


@app.route("/api/messages", methods=["GET", "POST"])
def handle_messages():
  if request.method == "GET":
    user1 = request.args.get("user1")
    user2 = request.args.get("user2")
    chat_msgs = [
        m
        for m in messages_db
        if (m["sender"] == user1 and m["recipient"] == user2)
        or (m["sender"] == user2 and m["recipient"] == user1)
    ]
    return jsonify(chat_msgs)

  data = request.json
  msg = {
      "id": len(messages_db) + 1,
      "sender": data.get("sender"),
      "recipient": data.get("recipient"),
      "text": data.get("text"),
      "timestamp": data.get("timestamp", ""),
  }
  messages_db.append(msg)
  return jsonify({"success": True, "message": msg})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)