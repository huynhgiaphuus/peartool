import json
import time
import os
import sys
import win32com.client
import pygetwindow as gw
import psutil
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from colorama import init, Fore, Style
import datetime
import requests

init(autoreset=True)
start_time = time.time()
ctrl_r_count = 0

REAL_CONFIG_PATH = r"C:\LDPlayer\LDPlayer9\vms\config\leidians.config"
CONFIG_GOC_PATH = "config_ldmulti.json"
SERVER_URL = "https://peartool-production.up.railway.app/command"
SERVER_URL_CLEAR = "https://peartool-production.up.railway.app/clear"
last_checksum = None

def log(msg, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    color = Fore.GREEN if level == "INFO" else Fore.RED if level == "ERROR" else Fore.YELLOW
    print(f"{timestamp} - {color}{level}{Style.RESET_ALL} - {msg}")

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def calculate_checksum(path):
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def compare_and_fix(force=False):
    global last_checksum
    if not os.path.exists(REAL_CONFIG_PATH) or not os.path.exists(CONFIG_GOC_PATH):
        return
    new_checksum = calculate_checksum(REAL_CONFIG_PATH)
    if not force and new_checksum == last_checksum:
        return
    try:
        current = load_json(REAL_CONFIG_PATH)
        original = load_json(CONFIG_GOC_PATH)
        if current != original:
            log("⚠️ This message send from config", "ERROR")
            save_json(REAL_CONFIG_PATH, original)
        else:
            log("ℹ️ Config not change yet.")
    except Exception as e:
        log(f"❌ Failed when check config: {e}", "ERROR")
    finally:
        last_checksum = calculate_checksum(REAL_CONFIG_PATH)

def add_to_startup():
    startup_folder = os.path.join(os.environ["APPDATA"], "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    run_bat_path = os.path.join(base_dir, "run_all.bat")
    if os.path.exists(run_bat_path):
        target = run_bat_path
        shortcut_name = "Run Pear Tool.lnk"
    else:
        log("❌ Not found run_all.bat.", "ERROR")
        return
    shortcut_path = os.path.join(startup_folder, shortcut_name)
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = base_dir
    shortcut.IconLocation = target
    shortcut.save()
    log(f"✅ Added {os.path.basename(target)} success.")

def kill_ldplayer_tabs():
    found = False
    for w in gw.getWindowsWithTitle('LDPlayer'):
        try:
            w.close()
            found = True
            log("✅ Closed tab.")
        except Exception as e:
            log(f"❌ Eroor when kill tab: {e}", "ERROR")
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'dnplayer' in proc.info['name'].lower():
                proc.terminate()
                found = True
                log("🛑 Đã kill tiến trình LDPlayer.")
        except Exception as e:
            log(f"❌ Error kill tab: {e}", "ERROR")
    if not found:
        log("⚠️ Not found ldplayer.")

def poll_server():
    global ctrl_r_count
    try:
        res = requests.get(SERVER_URL, timeout=5)
        if res.status_code == 200:
            command = res.text.strip().lower()
            if command == "ctrl_r":
                ctrl_r_count += 1
                enough_time = time.time() - start_time > 300  # 5 phút
                if ctrl_r_count >= 2 or enough_time:
                    log("👉 This message send from pear server: Kill LDPlayer", "INFO")
                    kill_ldplayer_tabs()
                    requests.get(SERVER_URL_CLEAR)
                else:
                    log("⏳ Waitting server reponse...", "INFO")
    except Exception:
        log("⚠️ Connect to server...", "INFO")

class ConfigChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if os.path.abspath(event.src_path) == os.path.abspath(REAL_CONFIG_PATH):
            compare_and_fix()

if __name__ == "__main__":
    log("🚀 Tool start checking server...", "INFO")
    add_to_startup()
    compare_and_fix(force=True)
    observer = Observer()
    observer.schedule(ConfigChangeHandler(), path=os.path.dirname(REAL_CONFIG_PATH), recursive=False)
    observer.start()

    try:
        while True:
            poll_server()
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
