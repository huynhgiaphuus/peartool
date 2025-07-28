# server.py
from flask import Flask

app = Flask(__name__)

current_command = ""

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
