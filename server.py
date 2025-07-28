from flask import Flask, send_file
import os

app = Flask(__name__)

current_command = ""

@app.route("/raw/pear.py")
def serve_pear_code():
    path = os.path.join(os.path.dirname(__file__), "pear.py")
    return send_file(path, mimetype="text/plain")

@app.route("/")
def home():
    return "✅ Server đang hoạt động!"

@app.route("/command")
def get_command():
    return current_command

@app.route("/send/ctrlr")
def send_ctrlr():
    global current_command
    current_command = "ctrl_r"
    return "📤 Gửi lệnh Ctrl+R thành công"

@app.route("/clear")
def clear_command():
    global current_command
    current_command = ""
    return "🧹 Đã xóa lệnh"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
