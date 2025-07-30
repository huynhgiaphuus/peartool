from flask import Flask, request
import threading
import time
import os
from datetime import datetime

app = Flask(__name__)

# Global variables
current_command = ""
current_version = "1.0.0"
LATEST_CODE_FILE = "pear_tool_latest.py"
VERSION_FILE = "current_version.txt"

def load_version():
    """Load version from file"""
    global current_version
    try:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, 'r', encoding='utf-8') as f:
                current_version = f.read().strip()
    except:
        current_version = "1.0.0"
    return current_version

def save_version(version):
    """Save version to file"""
    try:
        with open(VERSION_FILE, 'w', encoding='utf-8') as f:
            f.write(version)
        return True
    except:
        return False

def increment_version():
    """Increment version number"""
    global current_version
    try:
        parts = current_version.split('.')
        parts[-1] = str(int(parts[-1]) + 1)
        current_version = '.'.join(parts)
        save_version(current_version)
        return current_version
    except:
        current_version = "1.0.1"
        save_version(current_version)
        return current_version

# Load version on startup
load_version()

@app.route("/")
def home():
    return f"""
    <h1>🍐 Pear Tool Server</h1>
    <p>✅ Server đang hoạt động!</p>
    <p>📋 Version hiện tại: <strong>{current_version}</strong></p>
    <p>📡 Lệnh hiện tại: <strong>"{current_command}"</strong></p>  
    <p>⏰ Thời gian: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    
    <hr>
    <h3>📊 API Endpoints:</h3>
    <ul>
        <li><strong>GET /command</strong> - Lấy lệnh hiện tại</li>
        <li><strong>GET /pear</strong> - Gửi lệnh Ctrl+R (tự xóa sau 20s)</li>
        <li><strong>GET /version</strong> - Lấy phiên bản hiện tại</li>
        <li><strong>GET /update</strong> - Tải code mới nhất</li>
        <li><strong>POST /push_update</strong> - Push code mới</li>
        <li><strong>POST /force_update</strong> - Bắt buộc tất cả client update</li>
    </ul>
    
    <hr>
    <h3>🔧 Quick Actions:</h3>
    <p><a href="/pear" style="background:orange;color:white;padding:5px 10px;text-decoration:none;border-radius:3px;">📤 Send Ctrl+R</a></p>
    <p><a href="/force_update" style="background:blue;color:white;padding:5px 10px;text-decoration:none;border-radius:3px;">🔄 Force Update All</a></p>
    """

@app.route("/command")
def get_command():
    """Lấy lệnh hiện tại cho client"""
    return current_command

@app.route("/pear")
def send_pear():
    """Gửi lệnh Ctrl+R và tự xóa sau 20 giây"""
    global current_command
    current_command = "ctrl_r"
    
    # Bắt đầu thread tự xóa sau 20 giây
    threading.Thread(target=auto_clear_command, daemon=True).start()
    
    print(f"📤 [{datetime.now().strftime('%H:%M:%S')}] Gửi lệnh ctrl_r")
    return "📤 Gửi lệnh Ctrl+R thành công (tự xóa sau 20s)"

def auto_clear_command():
    """Hàm xóa lệnh sau 20 giây"""
    time.sleep(20)
    global current_command
    current_command = ""
    print(f"🧹 [{datetime.now().strftime('%H:%M:%S')}] Đã tự động xóa lệnh sau 20s")

# ========== AUTO-UPDATE ENDPOINTS ==========

@app.route("/version")
def get_version():
    """Lấy phiên bản hiện tại"""
    return current_version

@app.route("/update")
def get_update():
    """Tải code mới nhất"""
    try:
        if os.path.exists(LATEST_CODE_FILE):
            with open(LATEST_CODE_FILE, 'r', encoding='utf-8') as f:
                latest_code = f.read()
            print(f"📤 [{datetime.now().strftime('%H:%M:%S')}] Client đã tải update")
            return latest_code
        else:
            return "No update available", 404
    except Exception as e:
        print(f"❌ Error reading update: {e}")
        return f"Error reading update: {str(e)}", 500

@app.route("/push_update", methods=['POST'])
def push_update():
    """Push code mới từ developer"""
    try:
        # Lấy code từ request body
        new_code = request.get_data(as_text=True)
        
        if not new_code:
            return "❌ Không có code được gửi", 400
        
        if len(new_code) < 100:
            return "❌ Code quá ngắn, không hợp lệ", 400
        
        # Validation cơ bản
        if "def main(" not in new_code:
            return "❌ Code phải có function main()", 400
        
        # Kiểm tra syntax Python
        try:
            compile(new_code, '<string>', 'exec')
        except SyntaxError as e:
            return f"❌ Lỗi syntax Python: {str(e)}", 400
        
        # Lưu code mới
        with open(LATEST_CODE_FILE, 'w', encoding='utf-8') as f:
            f.write(new_code)
        
        # Tăng version
        new_version = increment_version()
        
        print(f"🚀 [{datetime.now().strftime('%H:%M:%S')}] Code mới được push! Version: {new_version}")
        print(f"📏 Code size: {len(new_code)} characters")
        
        return f"✅ Push thành công! Version mới: {new_version}"
        
    except Exception as e:
        print(f"❌ Push error: {e}")
        return f"❌ Lỗi: {str(e)}", 500

@app.route("/force_update", methods=['GET', 'POST'])
def force_update():
    """Bắt buộc tất cả client update ngay lập tức"""
    global current_command
    current_command = "update"
    
    print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Force update command sent to all clients")
    
    # Tự động clear sau 60 giây để không block các lệnh khác
    threading.Thread(target=lambda: (time.sleep(60), setattr(__import__('__main__'), 'current_command', "")), daemon=True).start()
    
    return "🔄 Lệnh force update đã được gửi tới tất cả client!"

# ========== ADMIN/DEBUG ENDPOINTS ==========

@app.route("/clear")
def manual_clear():
    """Manual clear command (for debugging)"""
    global current_command
    old_command = current_command
    current_command = ""
    
    print(f"🧹 [{datetime.now().strftime('%H:%M:%S')}] Manual clear: '{old_command}' -> ''")
    return f"🧹 Đã xóa lệnh: '{old_command}'"

@app.route("/set_command", methods=['POST'])
def set_command():
    """Set command manually (for testing)"""
    global current_command
    try:
        # Try JSON first
        data = request.get_json()
        if data and 'command' in data:
            current_command = data['command']
        else:
            # Try form data
            current_command = request.form.get('command', '')
        
        print(f"🎮 [{datetime.now().strftime('%H:%M:%S')}] Manual command set: '{current_command}'")
        return f"✅ Lệnh được set: '{current_command}'"
        
    except Exception as e:
        return f"❌ Lỗi set command: {str(e)}", 400

@app.route("/status")
def get_status():
    """Get detailed server status"""
    status_info = {
        "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "current_command": current_command,
        "current_version": current_version,
        "update_file_exists": os.path.exists(LATEST_CODE_FILE),
        "update_file_size": os.path.getsize(LATEST_CODE_FILE) if os.path.exists(LATEST_CODE_FILE) else 0
    }
    
    return f"""
    <h2>📊 Server Status</h2>
    <pre>{chr(10).join([f"{k}: {v}" for k, v in status_info.items()])}</pre>
    <p><a href="/">← Back to Home</a></p>
    """

if __name__ == "__main__":
    print("🍐 Pear Tool Server Starting...")
    print(f"📋 Initial version: {current_version}")
    print(f"🌐 Server will run on http://0.0.0.0:5000")
    print("=" * 50)
    
    app.run(host="0.0.0.0", port=5000, debug=True)
