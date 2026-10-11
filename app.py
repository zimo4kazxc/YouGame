from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Разрешаем запросы с GitHub Pages на Render

# База данных с дефолтными аккаунтами
users_db = {
    "+000 000": {
        "phone": "+000 000",
        "first_name": "Поддержка",
        "last_name": "YouGram",
        "username": "support",
        "bio": "Поддержка YouGram",
        "avatar": "",
        "is_support": True
    },
    "AdminPanel": {
        "phone": "AdminPanel",
        "first_name": "AdminPanel",
        "last_name": "",
        "username": "admin_panel",
        "bio": "Бот управления YouGram",
        "avatar": "",
        "is_bot": True
    }
}
messages_db = {}

@app.route('/api/auth/send_code', methods=['POST'])
def send_code():
    data = request.json or {}
    phone = data.get('phone')
    if not phone:
        return jsonify({"success": False, "error": "Введите номер телефона"}), 400
    
    code = "1337"
    if phone == "+000 000":
        code = "2222"
    elif phone == "+999 999":
        code = "1111"
        
    return jsonify({"success": True, "code": code})

@app.route('/api/auth/verify', methods=['POST'])
def verify_code():
    data = request.json or {}
    phone = data.get('phone')
    
    if not phone:
        return jsonify({"success": False, "error": "Нет номера"}), 400
        
    exists = phone in users_db
    return jsonify({"success": True, "exists": exists})

@app.route('/api/users/profile', methods=['GET'])
def get_profile():
    phone = request.args.get('phone')
    user = users_db.get(phone)
    if not user:
        return jsonify({"success": False, "error": "Пользователь не найден"}), 404
    return jsonify(user)

@app.route('/api/users/register', methods=['POST'])
def register_user():
    data = request.json or {}
    phone = data.get('phone')
    if not phone:
        return jsonify({"success": False, "error": "Нет номера"}), 400
        
    user_obj = {
        "phone": phone,
        "first_name": data.get('first_name', 'Пользователь'),
        "last_name": data.get('last_name', ''),
        "username": data.get('username', f"user_{phone[-4:]}"),
        "bio": data.get('bio', ''),
        "avatar": data.get('avatar', '')
    }
    users_db[phone] = user_obj
    return jsonify({"success": True, "user": user_obj})

@app.route('/api/users/search', methods=['GET'])
def search_users():
    query = request.args.get('q', '').lower()
    result = []
    for phone, u in users_db.items():
        if not query or query in u['first_name'].lower() or query in u['username'].lower() or query in phone:
            result.append(u)
    return jsonify(result)

@app.route('/api/messages', methods=['GET', 'POST'])
def handle_messages():
    if request.method == 'GET':
        u1 = request.args.get('user1')
        u2 = request.args.get('user2')
        if not u1 or not u2:
            return jsonify([])
        
        chat_key = "_".join(sorted([u1, u2]))
        msgs = messages_db.get(chat_key, [])
        return jsonify(msgs)
        
    elif request.method == 'POST':
        data = request.json or {}
        sender = data.get('sender')
        recipient = data.get('recipient')
        text = data.get('text')
        
        if not sender or not recipient or not text:
            return jsonify({"success": False, "error": "Неполные данные"}), 400
            
        chat_key = "_".join(sorted([sender, recipient]))
        if chat_key not in messages_db:
            messages_db[chat_key] = []
            
        msg_obj = {
            "sender": sender,
            "recipient": recipient,
            "text": text,
            "timestamp": data.get('timestamp')
        }
        messages_db[chat_key].append(msg_obj)
        return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)