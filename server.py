from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Flask-сервер работает на Railway!"

@app.route('/upload_link', methods=['POST'])
def receive_link():
    data = request.json
    file_link = data.get("file_link")

    if not file_link:
        return jsonify({"status": "error", "message": "No file link received"}), 400

    print(f"📥 Получена ссылка на файл: {file_link}")

    return jsonify({"status": "success", "message": "Link received"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))  # Railway автоматически задаёт порт
    app.run(host='0.0.0.0', port=port)