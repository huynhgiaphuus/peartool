from flask import Flask
import threading
import time

app = Flask(__name__)
current_command = ""

@app.route("/")
def home():
    return "✅ Server đang hoạt động!"

@app.route("/command")
def get_command():
    return current_command

@app.route("/pear")
def send_pear():
    global current_command
    current_command = "ctrl_r"
    # Bắt đầu thread tự xoá sau 20 giây
    threading.Thread(target=auto_clear_command).start()
    return "📤 Gửi lệnh Ctrl+R thành công (tự xoá sau 20s)"

# Hàm xoá lệnh sau 20 giây
def auto_clear_command():
    time.sleep(20)
    global current_command
    current_command = ""
    print("🧹 Đã tự động xoá lệnh sau 20s")

# ❌ KHÔNG có route /clear nữa

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
