"""
// Author: stevo_ko , https://twitch.tv/stevo_ko , Discord: stevo_ko on the streamer.bot Server
// Contact: on the above mentioned social media, or per ping in the streamer.bot server in the Thread for this tool or per directmessage to username stefan571
//
// This code is licensed under the GNU General Public License Version 3 (GPLv3).
// 
// The GPLv3 is a free software license that ensures end users have the freedom to run,
// study, share, and modify the software. Key provisions include:
// 
// - Copyleft: Modified versions of the code must also be licensed under the GPLv3.
// - Source Code: You must provide access to the source code when distributing the software.
// - Credit: You must credit the original author of the software, by mentioning either contact e-mail or their social media.
// - No Warranty: The software is provided "as-is," without warranty of any kind.
// 
// For more details, see https://www.gnu.org/licenses/gpl-3.0.en.html.
"""

import time
import os
import json
import re
import sys
import ctypes
import subprocess
import logging
import threading
import queue
import math
import io
import contextlib
import asyncio

default_config = {
    "twitch": {
        "CLIENT_ID": "",
        "OAuth_token": ""
    },
    "kick": 
    {
        "OAuth_token": "",
    },
    "streamerbot": {
        "Get Actions ID": [
            {
                "Action_Name": "[STEVO] Get Action ID"
            }
        ],
        "Category": [
            {
                "Action_Name": "[STEVO] Category"
            }
        ],
        "Get Token": [
            {
                "Action_Name": "[STEVO] Get Token"
            }
        ],
        "Chat Message": [
            {
                "Action_Name": "[STEVO] Chat Message"
            }
        ],        
        "port": "2310",
        "url": "127.0.0.1"
    },
    "paths": {
        "allowed_paths": [
            "E:\\Spiele",
            "E:\\SteamLibrary",
            "C:\\Program Files (x86)\\Steam\\steamapps\\",
            "C:\\Program Files\\Steam\\steamapps\\",
            "C:\\Program Files (x86)\\Epic Games\\",
            "C:\\Program Files\\Epic Games\\",
            "C:\\Program Files (x86)\\Ubisoft\\Ubisoft Game Launcher\\games\\",
            "C:\\Program Files\\Ubisoft\\Ubisoft Game Launcher\\games\\",
            "C:\\Program Files\\Ubisoft\\Ubisoft Game Launcher\\installed\\",
            "C:\\Program Files (x86)\\Ubisoft\\Ubisoft Game Launcher\\installed\\",
            "C:\\Program Files (x86)\\Origin Games\\",
            "C:\\Program Files\\Origin Games\\",
            "C:\\Program Files (x86)\\Electronic Arts\\",
            "C:\\Program Files\\Electronic Arts\\",
            "C:\\Program Files (x86)\\Battle.net\\",
            "C:\\Program Files\\Battle.net\\",
            "C:\\Riot Games\\"   
        ],
        "excluded_names": [
            "Riot Client.exe",
            "RiotClientServices.exe",
            "tbs_browser.exe",
            "service.exe",
            "QtWebEngineProcess.exe",
            "dxsetup.exe",
            "vcredist_x86.exe",
            "WowVoiceProxy.exe",
            "BlizzardBrowser.exe",
            "BlizzardError.exe",
            "winrtutil64.exe",
            "wallpaper64.exe",
            "The Jackbox Megapicker.exe",
            "CrashMailer_64.exe"
        ],
        "excluded_folders": [
            "bin",
            "binaries",
            "win64",
            "win32",
            "system",
            "engine",
            "redist",
            "game",
            "x64",
            "x32",
            "boot",
            "launcher",
            "marvelgame",
            "utils",
            "_retail_",
            "Stream",
            "plugins",
            "live",
            "ThirdParty",
            "Bridge",
            "Win",
            "EGS"
        ]
    }, 
    "options": {
        "language": "english",
        "similarity": 94,
        "watch_streamerbot": True,
        "watch_obs": False,
        "only_local_db": False,
        "show_console": False,
        "Box_Art_Size": "285x380",
        "message": True,
        "AsAnnouncement": False,
        "censor_mode": False,
        "delay_programming": 60,
        "delay_general": 0,
        "kick_enabled": False
    }
}


if getattr(sys, 'frozen', False):
    # Wenn das Programm als .exe (z. B. via PyInstaller) läuft
    programm_ordner = os.path.dirname(sys.executable)
else:
    # Wenn es als .py-Skript läuft
    programm_ordner = os.path.dirname(os.path.abspath(__file__))

settingspath = programm_ordner + "\\"
config_path = os.path.join(programm_ordner, "config.json")

##print(settingspath)

# Funktion zum Speichern der Standardkonfiguration
# Function to create default config
def save_default_config():
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(default_config, f, indent=4)
##    print(f"{config_path} wurde mit Standardwerten erstellt.")


def merge_config(default, current):
    exclude_paths = ["E:\\Spiele", "E:\\SteamLibrary"]
    result = {}

    for key in default:
        default_value = default[key]
        current_value = current.get(key)

        if key not in current:
            result[key] = default_value
        else:
            if isinstance(default_value, dict) and isinstance(current_value, dict):
                result[key] = merge_config(default_value, current_value)
            elif isinstance(default_value, list) and isinstance(current_value, list):
                if key == "allowed_paths":
                    filtered_value = [item for item in default_value if item not in exclude_paths]
                else:
                    filtered_value = default_value

                combined = current_value + [item for item in filtered_value if item not in current_value]
                result[key] = combined
            else:
                result[key] = current_value

    # Falls current Keys enthält, die nicht in default sind (z. B. durch spätere Erweiterungen)
    for key in current:
        if key not in result:
            result[key] = current[key]

    return result

def remove_from_config():
    """Entfernt die Einträge aus config.json, die nicht in default_config vorhanden sind"""
    with open("config.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Prüfen, ob Key existiert
    if "api" in data:
        del data["api"]
        # Datei nur schreiben, wenn Key gelöscht wurde
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=False)



try:
    with open("config.json", "r", encoding="utf-8") as file:
        config = json.load(file)

except (FileNotFoundError, json.JSONDecodeError):
##    print(f"Error loading {config_path}. Create default config.")
    save_default_config()
    config = default_config

else:
    # Mische fehlende Keys aus default_config ein
    updated_config = merge_config(default_config, config)
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(updated_config, f, indent=4)
    config = updated_config
    remove_from_config()
    


show_console = bool(config["options"]["show_console"])
setting_language = config["options"]["language"]


# Variants for language options and a few games
german_variants = {"deutsch", "german", "de", "ger", "deu"}
english_variants = {"englisch", "english", "en", "eng"}

# Standardwert für language setzen
# Standart language
language = 0

# Prüfen, ob setting_language gültig ist
# Check if setting_language is valid
if isinstance(setting_language, str):
    setting_language = setting_language.strip().lower()
    
    if setting_language in german_variants:
##        print("Sprache ist Deutsch!")
        language = 1
    else:
        language = 0
##        print("Language set to English\n")
else:
    print("Non valid language set in json (none or false format). Default to English!")

##sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


## Prüfe ob module importiert werden können wenn nicht installiere sie
## Check if modules can be imported otherwise install them

modules = ["rapidfuzz", "requests", "psutil"]

for module in modules:
    try:
        __import__(module)
    except ImportError:
        if language == 1:
            print(f"📦 {module} fehlt. Installation wird gestartet...")
        if language == 0:
            print(f"📦 {module} missing. Installation started...")
        subprocess.run([sys.executable, "-m", "pip", "install", module], check=True)

# Jetzt die Module importieren (nach der Installation)
# After install import modules
from rapidfuzz import fuzz
import requests
import psutil
from pydantic import BaseModel
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QMessageBox, QLabel
from PyQt5.QtCore import QTimer, QMetaObject
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon

def get_resource_path_old(relative_path):
    """ Holt den absoluten Pfad zu Ressourcen, egal ob als .py oder .exe ausgeführt """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, "Assets", relative_path)
    return os.path.join("Assets", relative_path)

def get_resource_path(relative_path):
    """Pfad zu Ressourcen im _internal/Assets Ordner neben der exe/py"""
    if getattr(sys, 'frozen', False):
        # exe → basiert auf Ordner der exe
        base_path = os.path.dirname(sys.executable)
    else:
        # py → basiert auf Ordner des Skripts
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, "_internal", "Assets", relative_path)

# Logging-Queue
log_queue = queue.Queue()


# PyQt für GUI/Konsolen Window
# PyQt GUI for console window
class ConsoleRedirector:
    def __init__(self, queue):
        self.queue = queue

    def write(self, message):
        
        """Leitet die Nachricht an die Queue weiter"""
        """Sends print to queue"""
        if message.strip():  # Vermeidet leere Nachrichten | prevent empty messages
            self.queue.put(message)

    def flush(self):
        pass
    
class ConsoleApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Category Switcher")
        self.setStyleSheet("background-color: gray; color: white; font-size: 14px;")

        # Hauptlayout
        self.layout = QVBoxLayout(self)
        self.console_text = QTextEdit(self)
        self.console_text.setReadOnly(True)
        icon_path = get_resource_path("icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        
        # Konsolen-Style (Dunkelgrauer Hintergrund, weiße Schrift, Schriftgröße 20)
        self.console_text.setStyleSheet("background-color: #222222; color: white; font-size: 20px;")
        self.layout.addWidget(self.console_text)

        # Absolut positioniertes Label für den permanenten Text
        self.footer_label = QLabel("~made by stevo_ko", self)
        self.footer_label.setStyleSheet("color: white; font-size: 12px; background: transparent;")
        self.footer_label.resize(135, 30)  # Größe des Labels setzen
        self.footer_label.move(self.width() - 135, self.height() - 40)  # Position rechts unten setzen

        # Fenstergröße setzen
        self.resize(1100, 500)

        # Mindestgröße setzen
        self.setMinimumSize(700, 400)        

        # Timer für Updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_console)
        self.timer.start(100)

        # Event für Größenänderung
        self.resizeEvent = self.on_resize

    def on_resize(self, event):
        """ Passt die Position des Labels an, wenn das Fenster skaliert wird """
        self.footer_label.move(self.width() - self.footer_label.width() - 20, self.height() - self.footer_label.height() - 10)

    def update_console(self):

        """Liest Nachrichten aus der Queue und fügt sie in die Konsole ein"""
        """Reads messages in queue and inserts them into the console"""
        while not log_queue.empty():
            message = log_queue.get_nowait()
            self.console_text.append(message)
            self.console_text.verticalScrollBar().setValue(self.console_text.verticalScrollBar().maximum())
            
if show_console:
    
    # Umleitung der Standardausgabe auf die Queue
    # Send standartoutput to queue
    sys.stdout = ConsoleRedirector(log_queue)
    sys.stderr = ConsoleRedirector(log_queue)

  

restarted = "--restarted" in sys.argv
gui = False
   
def restart_program(with_console):

    """Startet das Programm neu mit oder ohne Konsole."""
    """Starts program new with or without console"""
    exe_path = sys.executable  # Falls als .exe läuft, bleibt sys.executable unverändert
    args = sys.argv[1:]  

    if "--restarted" not in args:
        args.append("--restarted")  # `--restarted`-Flag hinzufügen
    try:
        if not with_console:
##            print(with_console)
            pythonw_path = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
##            print(pythonw_path)
            # Falls pythonw.exe nicht existiert, normalen Python-Interpreter verwenden
            # if pythonw.exe does not exist use normal python
            if not os.path.exists(pythonw_path):
                pythonw_path = sys.executable  
            
            # Starte das neue Skript und schließe die Konsole sicher
            # Start script and close console safely
##            subprocess.Popen([pythonw_path, os.path.abspath(__file__), "--restarted"])
            subprocess.Popen([pythonw_path, os.path.abspath(__file__)] + args)
            os._exit(0)
            
    except Exception as e:
        if language == 1:
            print(f"Ein Fehler ist aufgetreten: {e}")
        if language == 0:
            print(f"Error occured: {e}")
        os.system('pause')

def restart_program_no_console():
    exe_path = sys.executable
    args = sys.argv[1:]
    if "--restarted" not in args:
        args.append("--restarted")

    CREATE_NO_WINDOW = 0x08000000  # Flag für kein Konsolenfenster

    subprocess.Popen(
        [exe_path, os.path.abspath(__file__)] + args,
        creationflags=CREATE_NO_WINDOW
    )
    os._exit(0)
    
##if not restarted:
####    print("✅ Das Programm wurde bereits neu gestartet.")
####else: 
##    if not getattr(sys, 'frozen', False):  
##        # Falls als .py ausgeführt, direkt ohne Konsole starten
##        restart_program(with_console=False)


def find_json_with_address(args):
    for arg in args:
        try:
            parsed = json.loads(arg)
            if isinstance(parsed, dict) and "address" in parsed:
                return parsed
        except json.JSONDecodeError:
            pass
    return None

args = sys.argv[1:]
json_obj = find_json_with_address(args)

if json_obj is not None:
    address = json_obj.get("address")
    port = json_obj.get("port")

    extracted_config = {
        "streamerbot": {
            "url": address,
            "port": port
        }
    }

    merged_config = merge_config(default_config, extracted_config)
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(merged_config, f, indent=4)
    config = merged_config
    ##print("✅ Ergebnis nach Merge:\n", json.dumps(merged_config, indent=2))

    
if not getattr(sys, 'frozen', False):  
    SCRIPT_NAME = os.path.abspath(__file__)
else:
    SCRIPT_NAME = os.path.basename(sys.argv[0])
    #SCRIPT_NAME = "Category Switch.exe"
CHECK_INTERVAL = 1
THRESHOLD = 0

DEBUG_MODE = os.environ.get("DEBUG_MODE") == "1"

"""Verhindere das, dass Programm mehr als 1 mal läuft"""
"""Prevent Programm to run simultanously more than 1 time"""
def monitor_instances():
    if DEBUG_MODE:
        print("DEBUG_MODE aktiv – Instanzüberwachung deaktiviert.")
        return
    
    start_time = None
    overall_start_time = time.time()  # Gesamtstartzeit

    while True:
        # Wenn 20 Sekunden vorbei sind: Abbrechen
        if time.time() - overall_start_time > 5:
            break
        instances = []
        for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
            try:
                if proc.info["cmdline"]:
                    if any(SCRIPT_NAME in part for part in proc.info["cmdline"]):
                        instances.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
##        print(f"Aktive Instanzen: {len(instances)} - {instances}")

        if len(instances) >= 2:
            if start_time is None:
                start_time = time.time()
##                print("Timer gestartet!")
            else:
                elapsed_time = int(time.time() - start_time)
##                print(f"Läuft seit {elapsed_time} Sekunden")

                if elapsed_time >= THRESHOLD:
                    instances.sort(key=lambda p: p.create_time(), reverse=True)  # Neueste zuerst / newest first
##                    print(f"2 Instanzen seit {THRESHOLD}s aktiv. Beende NEUESTE Instanz ({instances[0].pid})...")
                    instances[0].terminate()  
                    start_time = None
        else:
            start_time = None  

        time.sleep(CHECK_INTERVAL)

double_instance_thread = threading.Thread(target=monitor_instances, daemon=True)
double_instance_thread.start()


def terminate_current_instance():
    # Hole den PID der aktuellen Instanz (dieses Skript)
    current_pid = os.getpid()
    try:
        current_proc = psutil.Process(current_pid)
        current_proc.terminate()  # Beendet den aktuellen Prozess
        print(f"Die aktuelle Instanz (PID {current_pid}) wurde beendet.")
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        print("Fehler beim Beenden der aktuellen Instanz.")

token = None
CLIENT_ID = None
access_token = None
token_valid = False
kick_token = None
kick_client_id = ""
kick_client_secret = ""
kick_enabled = None
kick_missing = False
category_set_already = None
previous_saved_games = None
first_save = False
game_folder = "Nothing"
delay_programming = None
delay_general = 0
message = False
server = None
kick_failed = False
known_exe_names = ["blender.exe","UnrealEditor.exe","Unity Hub.exe","Code.exe","devenv.exe",
                    "Rider64.exe","Rider.exe","pycharm64.exe","pycharm.exe","idea64.exe","idea.exe",
                    "webstorm64.exe","webstorm.exe","phpstorm64.exe","phpstorm.exe","clion64.exe","clion.exe",
                    "goland64.exe","goland.exe","datagrip64.exe","datagrip.exe","rubymine64.exe","rubymine.exe",
                    "appcode64.exe","appcode.exe","idaq.exe","idaq64.exe","idaw.exe","idaw64.exe","windbg.exe",
                    "windbg64.exe","cdb.exe","cdb64.exe","windbgui.exe","windbgui64.exe","x64dbg.exe","x64dbg64.exe",
                    "x32dbg.exe","x32dbg64.exe","ollydbg.exe","ollydbg64.exe","ollydbg2.exe","ollydbg2_64.exe",
                    "ollydbg2_de.exe","ollydbg2_de64.exe","ollydbg2_en.exe","ollydbg2_en64.exe","ollydbg2_fr.exe",
                    "ollydbg2_fr64.exe","ollydbg2_ja.exe","ollydbg2_ja64.exe","ollydbg2_ko.exe","ollydbg2_ko64.exe",
                    "ollydbg2_ru.exe","ollydbg2_ru64.exe","ollydbg2_zh.exe","ollydbg2_zh64.exe","ollydbg2_zh_cn.exe",
                    "ollydbg2_zh_cn64.exe","ollydbg2_zh_tw.exe","ollydbg2_zh_tw64.exe","ollydbg2_de.exe",   
                    "cutter.exe","binaryninja.exe","x64dbg.exe","x32dbg.exe","ollydbg.exe","windbg.exe","cdb.exe",
                    "ntsd.exe","procexp.exe","procmon.exe","processhacker.exe","cl.exe","link.exe","msbuild.exe",
                    "nmake.exe","gcc.exe","g++.exe","cmake.exe","ninja.exe","python.exe","pythonw.exe","node.exe",
                    "npm.exe","dotnet.exe","java.exe","javac.exe","psql.exe","mysql.exe","dbeaver.exe","git.exe",
                    "tortoisegitproc.exe","vmware.exe","virtualbox.exe","qemu-system-x86_64.exe","adb.exe","docker.exe",
                    "dottrace.exe","dotmemory.exe","perfview.exe","choco.exe","scoop.exe","winget.exe","postman.exe",
                    "curl.exe","wget.exe"
                    ]
   
last_modified = None   
def main_logic():
    global token, CLIENT_ID, token_valid, category_set_already, language, previous_saved_games, first_save, game_folder, config_path, last_modified, delay_programming, delay_general, message, with_console, kick_token, kick_client_id, kick_client_secret, kick_enabled, kick_missing, kick_failed, known_exe_names
    
##    print(config_path)
##    print(last_modified)
    ctypes.windll.kernel32.SetConsoleTitleW("Category Switcher")
    sys.argv[0] = ("Category Switcher")

    # Config-Datei laden
    # load config file
    with open("config.json", "r", encoding="utf-8") as file:
        config = json.load(file)

    
    # Prüfung ob ein Wert nicht vorhanden oder leer ist
    # Check if Value not exist or is empty
    def get_key_value(data, key):
        """ Holt den Wert aus der JSON-Struktur, falls vorhanden und nicht leer """
        if data:  # Überprüft, ob die Kategorie im Dictionary existiert
            return data.get(key) or None  # Holt den Wert des Schlüssels und gibt None zurück, wenn er leer ist
        return None

    # Werte aus der Config extrahieren
    # Extract Values out of Conifg file
    CLIENT_ID = get_key_value(config["twitch"], "CLIENT_ID")
    token = get_key_value(config["twitch"], "OAuth_token")
    kick_token = get_key_value(config["kick"], "OAuth_token")
    
    streamerbot_url= config["streamerbot"]["url"]
    streamerbot_port = config["streamerbot"]["port"]
    streamerbot_get_actions_name = config['streamerbot']['Get Actions ID'][0]['Action_Name']
    streamerbot_get_token_name = config['streamerbot']['Get Token'][0]['Action_Name']
    streamerbot_category_name = config['streamerbot']['Category'][0]['Action_Name']
    streamerbot_send_message_name = config['streamerbot']['Chat Message'][0]['Action_Name']
    
    allowed_paths = config["paths"]["allowed_paths"]
    excluded_names = set(config["paths"]["excluded_names"])  # In ein Set umwandeln / convert to a set
    excluded_folders = set(config["paths"]["excluded_folders"])  # In ein Set umwandeln / convert to a set
    
    # Optionen
    # options
    watch_streamerbot = bool(config["options"]["watch_streamerbot"])
    watch_obs = bool(config["options"]["watch_obs"])
    only_local_db = bool(config["options"]["only_local_db"])
    threshold = config["options"]["similarity"]
    show_console = bool(config["options"]["show_console"])
    boxart_size = config["options"]["Box_Art_Size"]
    message = bool(config["options"]["message"])
    asannouncement = bool(config["options"]["AsAnnouncement"])
    censor_mode = bool(config["options"]["censor_mode"])
    width, height = map(int, boxart_size.split('x'))
    delay_programming = int(config["options"]["delay_programming"])*1000
    delay_general = int(config["options"]["delay_general"])*1000
    kick_enabled = bool(config["options"]["kick_enabled"])
    
    last_modified = os.path.getmtime(config_path)
    
    def load_config_live():
        global CLIENT_ID
        global token
        global kick_token
        global kick_enabled
        global language
        global delay_programming
        global delay_general
        global message
        nonlocal streamerbot_url
        nonlocal streamerbot_port
        nonlocal streamerbot_get_actions_name
        nonlocal streamerbot_get_token_name
        nonlocal streamerbot_category_name
        nonlocal streamerbot_send_message_name
        nonlocal allowed_paths
        nonlocal excluded_names
        nonlocal excluded_folders
        nonlocal watch_streamerbot
        nonlocal watch_obs
        nonlocal only_local_db
        nonlocal threshold
        nonlocal show_console
        nonlocal boxart_size
        nonlocal asannouncement
        nonlocal censor_mode
        nonlocal width, height
        
        
        with open("config.json", "r", encoding="utf-8") as file:
            config = json.load(file)

        
        # Prüfung ob ein Wert nicht vorhanden oder leer ist
        # Check if Value not exist or is empty
        def get_key_value(data, key):
            """ Holt den Wert aus der JSON-Struktur, falls vorhanden und nicht leer """
            if data:  # Überprüft, ob die Kategorie im Dictionary existiert
                return data.get(key) or None  # Holt den Wert des Schlüssels und gibt None zurück, wenn er leer ist
            return None

        # Werte aus der Config extrahieren
        # Extract Values out of Conifg file
        CLIENT_ID = get_key_value(config["twitch"], "CLIENT_ID")
        token = get_key_value(config["twitch"], "OAuth_token")
        kick_token = get_key_value(config["kick"], "OAuth_token")
        
        streamerbot_url= config["streamerbot"]["url"]
        streamerbot_port = config["streamerbot"]["port"]
        streamerbot_get_actions_name = config['streamerbot']['Get Actions ID'][0]['Action_Name']
        streamerbot_get_token_name = config['streamerbot']['Get Token'][0]['Action_Name']
        streamerbot_category_name = config['streamerbot']['Category'][0]['Action_Name']
        streamerbot_send_message_name = config['streamerbot']['Chat Message'][0]['Action_Name']
        
        allowed_paths = config["paths"]["allowed_paths"]
        excluded_names = set(config["paths"]["excluded_names"])  # In ein Set umwandeln / convert to a set
        excluded_folders = set(config["paths"]["excluded_folders"])  # In ein Set umwandeln / convert to a set
        
        # Optionen
        # options
        watch_streamerbot = bool(config["options"]["watch_streamerbot"])
        watch_obs = bool(config["options"]["watch_obs"])
        only_local_db = bool(config["options"]["only_local_db"])
        threshold = config["options"]["similarity"]
        show_console = bool(config["options"]["show_console"])
        boxart_size = config["options"]["Box_Art_Size"]
        message = bool(config["options"]["message"])
        asannouncement = bool(config["options"]["AsAnnouncement"])
        censor_mode = bool(config["options"]["censor_mode"])
        width, height = map(int, boxart_size.split('x'))
        delay_programming = int(config["options"]["delay_programming"])*1000
        delay_general = int(config["options"]["delay_general"])*1000
        kick_enabled = bool(config["options"]["kick_enabled"])
        setting_language = config["options"]["language"]

        german_variants = {"deutsch", "german", "de", "ger", "deu"}
        english_variants = {"englisch", "english", "en", "eng"}

        if isinstance(setting_language, str):
            setting_language = setting_language.strip().lower()
            if setting_language in german_variants:
                language = 1
            else:
                language = 0
        else:
            print("Invalid language setting in config.json, defaulting to English.")
            language = 0
        if language == 1:
            print("✅ Config.json wurde verändert. Erfolgreich reloaded.")
        if language == 0:
            print("✅ Config.json has changed. Succesful relaoded")

    # Varianten für die Sprach Einstellung und ein paar Spielschreibweisen
    # Variants for language options and a few games
    gta5_variants = {"gta v", "GTA V", "gtafive", "gtav", "gtav", "gta 5", "GTA 5", "gta5", "GTA5"}
    gta4_variants = {"GTA IV", "gta iv", "gta 4", "GTA 4"}

    not_in_local_db = False
    failed = False
    
    def start_logging():
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(
                filename='app.log',
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filemode='a',
                force=True# Log-Datei wird angehängt, nicht überschrieben / Log is appending and not overwriting
            )
        # Direktes Schreiben ohne Verzögerung
        # Write direct to logfile
        logging.getLogger().handlers[0].flush()
    def censoring():
        if censor_mode:
            with open("game_data.json", "r", encoding="utf-8") as file:
                data = json.load(file)

            if "Games" in data:
                for entry in data["Games"]:
                    entry["Path"] = ""

            with open("game_data_censored.json", "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            print(censor_mode)
            logging.info("Censor Mode is activated")
    censoring()

        
    def remove_intergrade_from_folder(game_folder):
        game_folder = re.sub(r'\s*Intergrade$', '', game_folder)
        return game_folder




    def is_ue_game_folder(game_folder):
        # Überprüfe, ob der Ordnernamen "ue" und eine Versionsnummer enthält (z.B. ue_5.x oder ue_9.x)
        pattern = r"ue_(\d+\.\d+)"  # Muster für "ue_" gefolgt von einer Version (z.B. 5.4, 9.9)
        return bool(re.search(pattern, game_folder.lower()))

    def is_ue_or_known_programming_folder(game_folder):
        known_names = ["blender"]  # Hier kannst du beliebig ergänzen
        ue_pattern = r"ue_(\d+\.\d+)"
        game_folder_lower = game_folder.lower()

        return bool(re.search(ue_pattern, game_folder_lower) or any(name in game_folder_lower for name in known_names))

    def is_ue_exe_path(exe_path):
        # Überprüfe, ob der Ordnernamen "ue" und eine Versionsnummer enthält (z.B. ue_5.x oder ue_9.x)
        pattern = r"ue_(\d+\.\d+)"  # Muster für "ue_" gefolgt von einer Version (z.B. 5.4, 9.9)
        return bool(re.search(pattern, exe_path.lower()))

    def is_ue_or_known_exe_path(exe_path):
        ue_pattern = r"ue_(\d+\.\d+)"
        godot_pattern = r"godot_v\d+\.\d+(\.\d+)?(-[a-z0-9_]+)?\.exe"

        exe_path_lower = exe_path.lower()
        return bool(
            re.search(ue_pattern, exe_path_lower)
            or re.search(godot_pattern, exe_path_lower)
            or any(exe.lower() in exe_path_lower for exe in known_exe_names)
        )

    
    # Überprüfen, ob obs64.exe noch läuft
    # check if obs64.exe is running
    def is_obs_running():
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == 'obs64.exe':
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    # Überprüfen, ob streamer.bot.exe noch läuft
    # check if streamer.bot.exe is running
    def is_streamerbot_running():
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == 'streamer.bot.exe':  
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def get_streamerbot_url():

        return f"http://{streamerbot_url}:{streamerbot_port}/DoAction"

    def send_message(game_folder, category_name, kick_category_name=None, kick_failed=None):
        
        streamerbot_url = get_streamerbot_url()

##        print(f"{streamerbot_url}")

        # Define the payload
        payload = {
            "action": {
              "name": streamerbot_send_message_name,
            },
            "args": {
                "failed": failed,
                "not_in_db": not_in_local_db,
                "game": game_folder,
                "Chat_Message": message,
                "Message_As_Announcement": asannouncement,
                "category_name": category_name,
                "kick_enabled": kick_enabled,
                "kick_category": kick_category_name,
                "kick_failed": kick_failed,
                "no_kick_msg": kick_failed is None,
            }
        }

        # Set headers (if required)
        headers = {
            "Content-Type": "application/json"
        }

        # Send the POST request
        response = requests.post(streamerbot_url, json=payload, headers=headers)

        # Check the response
        if response.status_code == 204:
            if language == 1:
                print(f"\n✅ Chatnachricht geschickt!\n")
            if language == 0:
                print(f"\n✅ Chatmessage sent!\n")
##            print(response.json())
        else:
            if language == 1:
                print(f"❌ Cahtnachricht senden fehlgeschlagen mit Error Meldung {response.status_code}")
                if not show_console:
                    start_logging()
                    logging.error(f"❌ Chatnachricht senden fehlgeschlagen mit Error Meldung {response.status_code}")
            if language == 0:
                print(f"❌ Chatmessage sending failed with status code {response.status_code}")
                if not show_console:
                    start_logging()
                    logging.error(f"❌ Chatmessage send failed with status code {response.status_code}")
            print(response.text)
        return


    def category_change(category_name, kick_category_name=None):
        
        streamerbot_url = get_streamerbot_url()

##        print(f"{streamerbot_url}")

        # Define the payload
        payload = {
            "action": {
              "name": streamerbot_category_name,
            },
            "args": {
                "category": category_name,
                "kick_category": kick_category_name,
                "kick_enabled": kick_enabled,
                           
            }
        }

        # Set headers (if required)
        headers = {
            "Content-Type": "application/json"
        }
        
        # Send the POST request
        try:
            response = requests.post(streamerbot_url, json=payload, headers=headers)

            # Check the response
            if response.status_code == 204:
                if language == 1:
                    print(f"\n✅ Kategorie '{category_name}' erfolgreich gesetzt!\n")
                if language == 0:
                    print(f"\n✅ Category '{category_name}' set successful!\n")
##                print(response.json())
            else:
                if language == 1:
                    print(f"❌ Kategorie senden fehlgeschlagen mit Error Meldung {response.status_code}")
                    if not show_console:
                        start_logging()
                        logging.error(f"❌ Kategorie senden fehlgeschlagen mit Error Meldung {response.status_code}")
                if language == 0:
                    print(f"❌ Category sending failed with status code {response.status_code}")
                    if not show_console:
                        start_logging()
                        logging.error(f"❌ Category sending failed with status code {response.status_code}")
                print(response.text)

        except requests.exceptions.ConnectionError as e:
            
            if not show_console:
                if not gui:
                    start_gui()                
            
            if language == 1:
                print("❌ Verbindung zu Streamer.bot konnte nicht hergestellt werden. Stelle sicher das der HTTP Server gestartet ist")
            if language == 0:
                print("❌ Could not connect to Streamer.bot. Make sure http server is running!")
            if not show_console:
                start_logging()
                logging.error(f"Connection error: {e}")
        except requests.exceptions.InvalidURL as e:
            
            if not show_console:
                if not gui:
                    start_gui()

            if language == 1:
                print("❌ Streamer.bot URL oder Port leer oder nicht gültig.")
            if language == 0:
                print("❌ Streamer.bot URL or Port empty or not valid.")
        except requests.exceptions.RequestException as e:
            
            if not show_console:
                if not gui:
                    start_gui()

            if language == 1:
                print("❌ Unbekannter Fehler bei Anfrage an Streamer.bot.")
            if language == 0:
                print("❌ Unknown error during request to Streamer.bot.")
            if not show_console:
                start_logging()
                logging.error(f"Request error: {e}")
                
        return

    
    def validate_oauth_token(token, CLIENT_ID, token_valid):
        url = 'https://id.twitch.tv/oauth2/validate'
        headers = {
            'Authorization': f'OAuth {token}'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            if language == 1:
                print("✅ Token ist gültig!")
            if language == 0:
                print("✅ Token is valid!")
            token_valid = True
            ##return response.json()  # Gibt die JSON-Antwort zurück, die Details zum Token enthält
        else:
            if language == 1:
                print(f"❌ Token ist nicht gültig | Erro Meldung: {response.status_code}")
                print(response.text)
            if language == 0:
                print(f"❌ Token is not valid! | Status Code: {response.status_code}")
                print(response.text)
            token_valid = False
        return token_valid
            
    # Funktion, um OAuth-Token zu bekommen
    # Function to retrieve OAuth-Token
    def get_access_token_action():
    
        streamerbot_url = get_streamerbot_url()

        payload = {
            "action": {
                "name": streamerbot_get_token_name,
            },
            "args": {
                "ScriptPath": settingspath
            }
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(streamerbot_url, json=payload, headers=headers)

            if response.status_code == 204:
                if language == 1:
                    print("\n✅ Get Token erfolgreich ausgeführt!\n")
                if language == 0:
                    print("\n✅ Get token successful!\n")
            else:
                if language == 1:
                    print(f"❌ Token erhalten nicht erfolgreich | Fehlercode {response.status_code}")
                    if not show_console:
                        start_logging()
                        logging.error(f"❌ Token erhalten nicht erfolgreich | Fehlercode {response.status_code}")
                if language == 0:
                    print(f"❌ Token not received successfully | Status code {response.status_code}")
                    if not show_console:
                        start_logging()
                        logging.error(f"❌ Token not received successfully | Status code {response.status_code}")
                ##print(response.text)

        except requests.exceptions.ConnectionError as e:
            
            if not show_console:
                if not gui:
                    start_gui()                
            
            if language == 1:
                print("❌ Verbindung zu Streamer.bot konnte nicht hergestellt werden. Stelle sicher das der HTTP Server gestartet ist")
            if language == 0:
                print("❌ Could not connect to Streamer.bot. Make sure http server is running!")
            if not show_console:
                start_logging()
                logging.error(f"Connection error: {e}")
        except requests.exceptions.InvalidURL as e:
            
            if not show_console:
                if not gui:
                    start_gui()

            if language == 1:
                print("❌ Streamer.bot URL oder Port leer oder nicht gültig.")
            if language == 0:
                print("❌ Streamer.bot URL or Port empty or not valid.")
        except requests.exceptions.RequestException as e:
            
            if not show_console:
                if not gui:
                    start_gui()

            if language == 1:
                print("❌ Unbekannter Fehler bei Anfrage an Streamer.bot.")
            if language == 0:
                print("❌ Unknown error during request to Streamer.bot.")
            if not show_console:
                start_logging()
                logging.error(f"Request error: {e}")

        return
    
    def save_token_to_config(token, CLIENT_ID):
        
        """Speichert den Token in die config.json."""
        try:
            with open("config.json", "r+", encoding="utf-8") as file:
                config = json.load(file)
                config["twitch"]["OAuth_token"] = token
                config["twitch"]["CLIENT_ID"] = CLIENT_ID
                file.seek(0)
                json.dump(config, file, indent=4)
                file.truncate()
        except Exception as e:
            if language == 1:
                print(f"❌ Fehler beim Speichern des Tokens oder der CLIENT_ID: {e}")
            if language == 0:
                print(f"❌ Error while saving of Tokens or CLIENT_ID: {e}")

                
    def get_kick_token():
        """Fordert einen neuen OAuth2 App Token an und speichert abgelaufene Tokens."""
        global kick_token, kick_client_id
        global _access_token, _token_expiry, _token_info
        token_url = "https://id.kick.com/oauth/token"

        data = {
            "grant_type": "client_credentials",
            "client_id": kick_client_id,
            "client_secret": kick_client_secret,
        }

        resp = requests.post(token_url, data=data)
        resp.raise_for_status()
        token_data = resp.json()

        kick_token = token_data["access_token"]
        _token_expiry = int(time.time()) + token_data["expires_in"] - 30  # 30s Puffer
        _token_info = token_data

        return kick_token   
 
    def save_kick_token_to_config(kick_token):
        
        """Speichert den Token in die config.json."""
        try:
            with open("config.json", "r+", encoding="utf-8") as file:
                config = json.load(file)
                config["kick"]["OAuth_token"] = kick_token
                file.seek(0)
                json.dump(config, file, indent=4)
                file.truncate()
        except Exception as e:
            if language == 1:
                print(f"❌ Fehler beim Speichern des Kick Tokens oder der CLIENT_ID: {e}")
            if language == 0:
                print(f"❌ Error while saving of the Kick Tokens or CLIENT_ID: {e}")

    # Funktion, um eine Twitch-Kategorie per Name zu suchen
    # Function to search Twitch-category with the Name
    def search_twitch_category(token, search_query):
        url = "https://api.twitch.tv/helix/search/categories"
        headers = {
            "Authorization": f"Bearer {token}",
            "Client-ID": CLIENT_ID

        }
        params = {"query": search_query}

        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            if language == 1:
                print(f"❌ Fehler bei der Kategorie-Suche: {response.status_code}, {response.text}")
            if language == 0:
                print(f"❌ Category search error: {response.status_code}, {response.text}")
            return []

        if response.status_code == 401:
            if language == 1:
                print(f"❌ Token ist nicht gültig | Erro Meldung: {response.status_code}")
            if language == 0:
                print(f"❌ Token is not valid! | Status Code: {response.status_code}")
            
            if is_streamerbot_running():               

                    
                token = get_access_token_action()

                # Warten, bis der Token empfangen und gespeichert wird
                time.sleep(2)
                save_token_to_config(token, CLIENT_ID)

                if language == 1:
                    print("✅ Token und CLIENT_ID erfolgreich gespeichert!\n")
                if language == 0:
                    print("✅ Token and CLIENT_ID saved successfull!\n")
            else:
                if language == 1:
                    print("Streamer.bot nicht gestartet!")
                if language == 0:
                    print("Streamer.bot not running!") 

        return response.json().get("data", [])
    
    def search_kick_category(kick_token, search_query):
        """Sucht nach einer Kategorie, die das Spiel in den Kick-Kategorien enthält."""
        url = "https://api.kick.com/public/v1/categories"
        
        headers = {
            "Authorization": f"Bearer {kick_token}",
        }
        params = {"q": search_query}

        response = requests.get(url, headers=headers, params=params)

        # ---- Token ungültig (401) ----
        if response.status_code == 401:

            # neuen Token holen
            kick_token = get_kick_token()

            save_kick_token_to_config(kick_token)
            time.sleep(2)
            # Retry mit neuem Token
            headers["Authorization"] = f"Bearer {kick_token}"
            response = requests.get(url, headers=headers, params=params)

            if response.status_code != 200:
                print(f"❌ Fehler auch nach Refresh: {response.status_code}, {response.text}")
                return []

        # ---- andere Fehler ----
        elif response.status_code != 200:
            if language == 1:
                print(f"❌ Fehler bei der Kategorie-Suche: {response.status_code}, {response.text}")
            else:
                print(f"❌ Category search error: {response.status_code}, {response.text}")
            return []

        # ---- Erfolg ----
        return response.json().get("data", [])

    
    def get_next_greater_3_4_size(width, height):
        """Berechnet die nächstgrößere 3:4-Größe und speichert sie direkt in config.json, falls sie sich geändert hat."""
        """Calculate next greater 3:4 Size and write it into the config.json if it changed"""
        
        # Gängige 3:4-Größen (sortiert nach Größe)
        # Standart 3:4 Sizes (sorted after Size)
        standard_sizes = [
            (240, 320), (285, 380), (300, 400), (360, 480), (480, 640),
            (600, 800), (720, 960), (768, 1024), (1080, 1440)
        ]
        
        # Prüfe, ob die aktuelle Größe bereits eine Standardgröße ist
        # Check if current Size is a standardsize
        if (width, height) in standard_sizes:
            return width, height  # Unverändert zurückgeben / give unchanged back

        # Finde die nächstgrößere Standardgröße
        # Find next greater standardsize
        for w, h in standard_sizes:
            if w >= width and h >= height:
                new_width, new_height = w, h
                break
        else:
            
            # Falls keine Standardgröße passt, berechne die nächste 3:4-Größe
            # If no suitable standardsize calculate next greater size
            new_width = math.ceil(width / 3) * 3  
            new_height = math.ceil(new_width * 4 / 3)

        new_size = f"{new_width}x{new_height}"

        # Neue Größe direkt in der config.json speichern
        # Save new size in config.json
        try:
            with open("config.json", "r+", encoding="utf-8") as file:
                config = json.load(file)

                # Aktuelle gespeicherte Größe abrufen
                # Rectrieve current size
                current_size = config["options"].get("Box_Art_Size", "")

                # Falls sich die Größe geändert hat, speichern
                # If current size not equal new size, save new size
                if current_size != new_size:
                    config["options"]["Box_Art_Size"] = new_size

                    file.seek(0)
                    json.dump(config, file, indent=4)
                    file.truncate()

        except Exception as e:
            if language == 1:
                print(f"❌ Fehler beim Speichern der Box_Art_Size: {e}")
            if language == 0:
                print(f"❌ Error while saving of the Box_Art_Size: {e}")


        return new_width, new_height
    
    # Funktion zum Abrufen des größten Box-Art-Bildes
    # Function to get the biggest Box Art
    def get_largest_box_art_url(box_art_url, category_id, width, height):
        """Passt die URL an eine gültige 3:4-Größe an."""
        new_width, new_height = get_next_greater_3_4_size(width, height)
        new_size = f"{new_width}x{new_height}"

        # Ersetze nur die Kategorie-ID, behalte aber _IGDB
        modified_url = re.sub(r"(\w+)(_IGDB)?(-\d+x\d+)", rf"{category_id}_IGDB\3", box_art_url, 1)

        return re.sub(r"\d+x\d+", new_size, modified_url)

    def get_valid_root_folder(exe_path, allowed_paths, excluded_folders):
        parts = exe_path.split("\\")

        # Pfad in eine Liste umwandeln
        # Convert path to list    
        parts = os.path.normpath(exe_path).split(os.sep)

##        print(parts)

        if "rocketleague" not in parts:

            # Case-insensitive Prüfung auf "Binaries" und "Win64"
            # Case sensitive check if binaries\win64 is in path
            
            if any("binaries" == part.lower() for part in parts) and any("win64" == part.lower() for part in parts):
                try:
                    
                    # Findet den Index von "Binaries"
                    # Find index of binaries
##                    index_binaries = parts.index("Binaries")
                    
                    index_binaries = next(i for i, part in enumerate(parts) if part.lower() == "binaries")
                    index_win64 = next(i for i, part in enumerate(parts) if part.lower() == "win64")
                    
                    # Den Ordner vor "Binaries" entfernen und "Binaries\Win64" beibehalten
                    # Remove folder before binaries and keep binaries\win64
##                    new_parts = parts[:index_binaries-1] + ["Binaries", "Win64"] + parts[parts.index("Win64")+1:]
                    new_parts = parts[:index_binaries - 1] + [parts[index_binaries], parts[index_win64]] + parts[index_win64 + 1:]
                    
                    # Den Laufwerksbuchstaben beibehalten (z.B. "E:"), bevor der neue Pfad mit den korrekten Teilen zusammengesetzt wird
                    # Save driveletter before new path is joined
                    drive = parts[0]  # z.B. 'E:'
                    
                    # Neuen Pfad korrekt mit den richtigen Trennzeichen und Laufwerk zusammenstellen
                    # New path with the correct driveletter and separator
                    exe_path = drive + "\\" + "\\".join(new_parts[1:])  # Joint den Rest des Pfades nach dem Laufwerk
                    
                    # Ausgabe des neuen Pfads sicherstellen
##                    print("Neuer Pfad:", exe_path)
##                    return exe_path

                except ValueError as e:
                    if language == 1:
                        print(f"Fehler beim Erstellen des neuen Pfades: {e}")
                    if language == 0:
                        print(f"Error while creating the new path: {e}")
                        
##        print(f"Aktueller exe_path nach Anpassung: {exe_path}")

        normalized_exe_path = os.path.normcase(os.path.normpath(exe_path))
        normalized_allowed_paths = [os.path.normcase(os.path.normpath(path)) for path in allowed_paths]


        current_folder = os.path.dirname(exe_path)  # Starten mit dem Ordner der exe-Datei / Start with the exe folder

##        print(f"Current: {current_folder}")

        normalized_current_folder = os.path.normcase(os.path.normpath(current_folder))

##        print(f"Excluded: {excluded_folders}")

##        while current_folder != os.path.dirname(current_folder):  # Solange wir nicht am Root angekommen sind / till we are at the root folder
##
##            # Überprüfe, ob der aktuelle Ordnername in excluded_folders enthalten ist
##            # Check if current folder is in excludec_folders
##            for excluded in excluded_folders:
##                if excluded.lower() in normalized_current_folder.lower():  # Case insensitive check
##
####                    print(f"Ordner '{current_folder}' wird ausgeschlossen.")
##
##                    # Gehe eine Ebene höher und prüfe erneut
##                    # go to the nex higher folder and check again
##                    current_folder = os.path.dirname(current_folder)
##                    normalized_current_folder = os.path.normcase(os.path.normpath(current_folder))  # Normalisiere den neuen Ordner / normalise the new folder path
##                    break  
##            else:   
##                return current_folder 

        while current_folder != os.path.dirname(current_folder):  # Solange nicht am Root angekommen

            # Hole den aktuellen Ordnernamen (nur den letzten Teil des Pfads)
            current_folder_name = os.path.basename(current_folder)

            # Prüfe, ob der exakte Ordnername in excluded_folders ist (Case-Insensitive)
            if any(excluded.lower() == current_folder_name.lower() for excluded in excluded_folders):
               ## print(f"Ordner '{current_folder}' wird ausgeschlossen.")

                # Gehe eine Ebene höher und prüfe erneut
                current_folder = os.path.dirname(current_folder)
                continue  # Setzt die Schleife fort, anstatt return zu erreichen

            # Falls der aktuelle Ordner **nicht** ausgeschlossen ist, zurückgeben
            return current_folder  

        # Wenn kein gültiger Ordner gefunden wurde
        if language == 1:
            print("Kein gültiger Ordner gefunden.") # Debug-Ausgabe
        if language == 0:
            print("No valid folder found.")  # Debug-Ausgabe
        return None

    # Set für bereits ausgegebene Prozesse (kombiniert aus PID und exe-Pfad)
    # Set already found processes (combined of PID and exe path)
    seen_processes = set()

    # Token nur einmal abrufen
    # Retrive Token only once
    if not only_local_db:
        
        if not token or not CLIENT_ID:
            
            if is_streamerbot_running():

                if language == 1:
                    print("❌ Kein OAuth-Token gefunden, versuche ihn zu erhalten")
                if language == 0:
                    print("❌ No OAuth-Token or CLIENT_ID found, try to receive it...")                    
                    
                token = get_access_token_action()

                # Warten, bis der Token empfangen und gespeichert wird
                time.sleep(2)
                ##save_token_to_config(token, CLIENT_ID)

                if language == 1:
                    print("✅ Token und CLIENT_ID erfolgreich gespeichert!\n")
                if language == 0:
                    print("✅ Token and CLIENT_ID saved successfull!\n")
            else:
                if language == 1:
                    print("Streamer.bot nicht gestartet!")
                if language == 0:
                    print("Streamer.bot not running!")                
                    
                

        else:
            token_valid = validate_oauth_token(token, CLIENT_ID, token_valid)

            if not token_valid:
                if is_streamerbot_running():

                    token = get_access_token_action()
                    # Warten, bis der Token empfangen und speichere ihn danach
                    # Wait till token received after that save it
                    time.sleep(2)
                    ##save_token_to_config(token, CLIENT_ID)

                    if language == 1:
                        print("✅ Token erfolgreich gespeichert!\n")
                    if language == 0:
                        print("✅ Token successful saved!\n")
                else:

                    if language == 1:
                        print("Streamer.bot nicht gestartet!")
                    if language == 0:
                        print("Streamer.bot not running!")
                

    # JSON-Daten werden hier gespeichert
    # Save json data
    saved_games = []

    # Spiel in lokaler Datenbank speichern
    # Save game in local database
    def save_saved_games(games):
        """
        Speichert die Spiele in game_data.json.
        Wenn ein Spiel mehrfach in der Liste vorhanden ist, wird nur der letzte Eintrag übernommen.
        """
        try:
            # Prüfe, ob die Datei existiert und lade vorhandene Daten
            if os.path.exists("game_data.json"):
                with open("game_data.json", "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    existing_games = existing_data.get("Games", [])
            else:
                existing_games = []

            # Erstelle ein Dictionary, um doppelte Spiele nach Name zusammenzuführen
            merged_games = {g["Game"]: g for g in existing_games}  # existierende Spiele
            for g in games:
                merged_games[g["Game"]] = g  # überschreibt alte Einträge mit den neuen Daten

            # Speichere die zusammengeführte Liste
            formatted_data = {
                "Games": list(merged_games.values()),
                "Database": {"Games in Database": len(merged_games)}
            }

            with open("game_data.json", "w", encoding="utf-8") as f:
                json.dump(formatted_data, f, ensure_ascii=False, indent=4)

    ##        if language == 1:
    ##            print("✅ Datei 'game_data.json' wurde erfolgreich gespeichert.")
    ##        if language == 0:
    ##            print("✅ File 'game_data.json' saved successfully.")

        except OSError as e:
            error_message = f"❌ Fehler: Problem beim Speichern der Datei 'game_data.json'. Details: {e}" if language == 1 else f"❌ Error: There was a problem while saving 'game_data.json'. Details: {e}"
            print(error_message)

    # Lokale Datenbank laden und in die neue Struktur umwandeln, falls nötig
    # Load local Database, if it is in old format change it to the new
    def load_saved_games():
        try:
            if os.path.exists("game_data.json"):
                with open("game_data.json", "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)

                        # Spiele-Liste extrahieren
                        if isinstance(data, dict) and "Games" in data:
                            games = data["Games"]
                        elif isinstance(data, list):
                            games = data
                        else:
                            if language == 1:
                                raise ValueError("Ungültige JSON-Struktur.")
                            if language == 0:
                                raise ValueError("Non valid JSON structure.")

                        # Kick-Keys ergänzen und Box Art umbenennen
                        for i, game in enumerate(games):
                            new_game = {}
                            for k, v in game.items():
                                if k == "Box Art":
                                    new_game["Twitch Box Art"] = v  # Name ändern, Inhalt beibehalten
                                else:
                                    new_game[k] = v

                            # Fehlende Kick-Keys hinzufügen
                            if "Kick Category Name" not in new_game:
                                new_game["Kick Category Name"] = ""
                            if "Kick Category ID" not in new_game:
                                new_game["Kick Category ID"] = ""
                            if "Kick Thumbnail" not in new_game:
                                new_game["Kick Thumbnail"] = ""

                            games[i] = new_game

                        # Datei direkt aktualisieren
                        save_saved_games(games)

                        return games  # Nur die Spiele-Liste zurückgeben

                    except json.JSONDecodeError:
                        if language == 1:
                            print("❌ Fehler: Ungültiges JSON-Format in der Datei 'game_data.json'.")
                        if language == 0:
                            print("❌ Error: Non valid JSON format in File 'game_data.json'.")
                        return []

            else:
                if language == 1:
                    print("❌ Fehler: Datei 'game_data.json' existiert nicht.")
                if language == 0:
                    print("❌ Error: File 'game_data.json' doesn't exist.")
                save_saved_games([])
                return []

        except OSError as e:
            print(f"❌ Error: Problems while opening file 'game_data.json'. Details: {e}")
            save_saved_games([])
            return []


    saved_games = load_saved_games()

    # Set für Spiele, die bereits ausgegeben wurden
    # Set already displayed games
    displayed_games = set()

    # Globale Variable für das aktuell laufende Spiel
    # Global variable for running game
    game_folder = None  # Initialisiert als None / initialised as none
    category_name = "Just Chatting"
    kick_category_name = "Just Chatting"
    if is_streamerbot_running():
        if kick_enabled:
            category_change(category_name, kick_category_name)
        else:
            category_change(category_name)
    obs_started = False
    streamerbot_started = False
    displayed_warning = False
    displayed_warning_category = False

    print("-" * 90)
    if language == 1:           
        print("⌛ Warte auf Spiel Prozess 🎮".center(90))
    if language == 0:
        print("⌛ Wating for the game process 🎮".center(90))
    print("-" * 90)

    while True:
       
        current_modified = os.path.getmtime(config_path)
        
        if current_modified != last_modified:
            ##print("Die config.json wurde geändert, neu laden!")
            last_modified = current_modified
            load_config_live()
            if not show_console:
                if not getattr(sys, 'frozen', False):  
                    # Falls als .py ausgeführt, direkt ohne Konsole starten
                    restart_program(with_console=False)
                else:
                    restart_program_no_console()
            else:
                if not gui:
                    start_gui()
            if censor_mode:
                censoring()# Hier rufst du deine Funktion auf        
        current_seen = set()
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                
                failed = False
                exe_path = proc.info['exe']
                pid = proc.info['pid']
                name = proc.info['name']


                
                # Sicherstellen, dass der Prozess ein valides exe_path hat und in allowed_paths liegt
                # Make sure process has an valid exe_path and is in allowed_paths
                if not exe_path or name in excluded_names:
                    continue

                # Prüfen, ob der exe_path in allowed_paths ist
                normalized_exe_path = os.path.normcase(os.path.normpath(exe_path))
                normalized_allowed_paths = [os.path.normcase(os.path.normpath(path)) for path in allowed_paths]

                if not any(normalized_exe_path.startswith(path) for path in normalized_allowed_paths):
##                    print(f"Prozess {name} mit exe_path {exe_path} ist nicht in allowed_paths.")
                    continue  # Wenn der exe_path nicht in allowed_paths liegt, überspringe diesen Prozess
                exe_lower = os.path.basename(exe_path).lower()
                
                #Überspringe verschiedene nicht gewollte Exe dateien
                #Skip not wanted exe files
                
                if "steamapps/common/obs studio" in exe_path.replace("\\", "/").lower():
                    continue
                
                if "launcher" in exe_lower and exe_lower.endswith(".exe"):
                    continue
                
                if "crs-" in exe_lower and exe_lower.endswith(".exe"):
                    continue

                if "crashpad_" in exe_lower and exe_lower.endswith(".exe"):
                    continue
                
                if "crashreport" in exe_lower and exe_lower.endswith(".exe"):
                    continue
                
                if "crashhandler" in exe_lower and exe_lower.endswith(".exe"):
                    continue

                if "errorreport" in exe_lower and exe_lower.endswith(".exe"): 
                    continue

                if "easyanticheat" in exe_lower and exe_lower.endswith(".exe"): 
                    continue
                
                if "uninst" in exe_lower and exe_lower.endswith(".exe"): 
                    continue
                
                if "unins0" in exe_lower and exe_lower.endswith(".exe"): 
                    continue
                
                if "unity.licensing" in exe_lower and exe_lower.endswith(".exe"): 
                    continue
                
                if "updater" in exe_lower and exe_lower.endswith(".exe"): 
                    continue

                if "webhandler" in exe_lower and exe_lower.endswith(".exe"): 
                    continue
                
                if "weblauncher" in exe_lower and exe_lower.endswith(".exe"): 
                    continue
                
                if "wslservice" in exe_lower and exe_lower.endswith(".exe"): 
                    continue

                if "msedge" in exe_lower and exe_lower.endswith(".exe"): 
                    continue
                if "gamingservices" in exe_lower and exe_lower.endswith(".exe"): 
                    continue  
                if "cortana" in exe_lower and exe_lower.endswith(".exe"): 
                    continue 
                if "storedesktopextension" in exe_lower and exe_lower.endswith(".exe"): 
                    continue    
                if "winstore.app" in exe_lower and exe_lower.endswith(".exe"): 
                    continue              
                if "video.ui" in exe_lower and exe_lower.endswith(".exe"): 
                    continue              
                if "calculatorapp" in exe_lower and exe_lower.endswith(".exe"): 
                    continue 
                if "gamebarft" in exe_lower and exe_lower.endswith(".exe"): 
                    continue 
                if "phoneexperiencehost" in exe_lower and exe_lower.endswith(".exe"):
                    continue 

                if "backgroundservice" in exe_lower and exe_lower.endswith(".exe"): 
                    continue                                
                                    
                if "vc_redist" in exe_lower and exe_lower.endswith(".exe"): 
                    continue
                
                if is_ue_or_known_exe_path(exe_path.lower()):
                    game_folder = "Software and game development"
                    kick_game_folder = "Software Development"
              
                else:    
                    # Gültigen Root-Ordner finden
                    # Find valid root folder
                    root_folder = get_valid_root_folder(exe_path, allowed_paths, excluded_folders)

    ##                if root_folder:
    ##                    print(f"Root: {root_folder}")

                    if not root_folder:
                        continue  # Falls kein gültiger Root-Ordner gefunden wurde, überspringe diesen Prozess
                                  # If no valid root folder found skip that process

                    # Spielname extrahieren (Ordner der .exe)
                    # Extrac gamename (Folder of .exe)
                    
                    game_folder = os.path.basename(root_folder)
                    kick_game_folder = game_folder

##                print(f" Debug output game_folder: {game_folder}")

                # Spezial Fälle um Twitch Kategorie richtig zu matchen            
                # Edge cases setting game_folder forceful to get twitch match            
                if "Intergrade" in game_folder:
                    game_folder = remove_intergrade_from_folder(game_folder)

                if is_ue_or_known_programming_folder(game_folder.lower()):
                    game_folder = "Software and game development"                     
                
                if game_folder in gta5_variants:
                    game_folder = "Grand Theft Auto V"

                if game_folder in gta4_variants:
                    game_folder = "Grand Theft Auto IV"

                if game_folder == "Mass Effect Ultimate Edition":
                    game_folder = "Mass Effect"

                ##if game_folder == "MarblesOnStream":
                  ##  game_folder = "Marbles On Stream"

                if "no mans sky" in game_folder.lower():
                    game_folder = "No Man's Sky"
                    
                if "the jackbox party" in game_folder.lower():
                    game_folder = "Jackbox Party Packs"

                if "only up" in game_folder.lower():
                    game_folder = "Only Up!"

                if "palworld" in game_folder.lower():
                    game_folder = "Palworld"

                if "silent hill 2" in game_folder.lower():
                    game_folder = "Silent Hill 2"
                                
                if game_folder.lower() == "repo":
                    game_folder = "R.E.P.O."
                    
                if game_folder.lower() == "beast management":
                    game_folder = "Project Unknown"

                if game_folder.lower() == "sololv":
                    game_folder = "Solo Leveling: Arise"
                    
                if "world of warcraft" in game_folder.lower():
                    game_folder = "World of Warcraft"

                if "spyro" in game_folder.lower():
                    game_folder = "Spyro The Dragon"

                if "final fantasy xiv" in game_folder.lower():
                    game_folder = "Final Fantasy XIV Online"

                if game_folder == "Counter-Strike Global Offensive":
                    game_folder = "Counter-Strike"
                    kick_game_folder = "Counter-Strike 2"
                    
                if game_folder == "rocketleague":
                    game_folder = "Rocket League"
                    
                if game_folder == "the witcher 2":
                    game_folder = "The Witcher 2: Assassins of Kings"
                                        
                # Eindeutige Kombination aus PID und exe_path (damit `current_seen` funktioniert)
                # Unique combination of PID and exe_path (so current_seen works)
                unique_id = (pid, exe_path)
                current_seen.add(unique_id)
                path_norm = os.path.normpath(exe_path)

                # Prüfen, ob das Spiel bereits in der JSON-Datei vorhanden ist
                # Check if Game is already saved in the local Database
                saved_games = load_saved_games()
                game_data = next((game for game in saved_games if game["Game"] == game_folder), None)
                
                if game_data and kick_enabled and unique_id not in seen_processes:
                    kick_id = str(game_data.get("Kick Category ID") or "").strip()
                    kick_name = str(game_data.get("Kick Category Name") or "").strip()

                    kick_missing = (kick_id == "" or kick_name == "")
                # Spiel gilt nur als in DB vorhanden, wenn game_data existiert und Kick nicht fehlt
                if game_data and game_folder not in displayed_games and not kick_missing:

                    # Spiel ist bereits in der JSON-Datei, gib die Twitch- und Kick-Daten aus
                    if language == 1:
                        print(f"\n✅ Gestartet: PID {pid}, Spiel: {game_folder} Path: {path_norm}\n")
                        print("-" * 90)
                        print(f"   🎮 Gefundene Twitch-Kategorie für '{game_folder}' in lokaler Datenbank:")
                        print(f"   📝 {game_data['Twitch Category Name']} (ID: {game_data['Twitch Category ID']})")
                        print(f"   📸 Twitch Box Art: {game_data['Twitch Box Art']}")
                        if kick_enabled and "Kick Category Name" in game_data:
                            print(f"   🟢 Kick Kategorie: {game_data['Kick Category Name']} (ID: {game_data['Kick Category ID']})")
                        print("-" * 90)

                    if language == 0:
                        print(f"\n✅ Started: PID {pid}, Game: {game_folder} Path: {path_norm}\n")
                        print("-" * 90)
                        print(f"   🎮 Found Twitch category for '{game_folder}' in local database:")
                        print(f"   📝 {game_data['Twitch Category Name']} (ID: {game_data['Twitch Category ID']})")
                        print(f"   📸 Twitch Box Art: {game_data['Twitch Box Art']}")
                        if kick_enabled and "Kick Category Name" in game_data:
                            print(f"   🟢 Kick category: {game_data['Kick Category Name']} (ID: {game_data['Kick Category ID']})")
                        print("-" * 90)

                    # Füge das Spiel der ausgegebenen Liste hinzu, um es nicht erneut anzuzeigen
                    # Add game to outputted list, so it does not show again                
                    category_name = game_data['Twitch Category Name']
                    if kick_enabled:
                        kick_category_name = game_data['Kick Category Name']
                    displayed_games.add(game_folder)
                    if is_streamerbot_running():
                        if category_set_already != category_name:
                            if kick_enabled:
                                category_change(category_name, kick_category_name)
                            else:
                                category_change(category_name)
                            category_set_already = category_name
                            if message:
                                if kick_enabled:
                                    send_message(game_folder, category_name, kick_category_name, kick_failed=False)
                                else:
                                    send_message(game_folder, category_name)
                                
                    
                
                elif not game_data or kick_missing:
                     
                    if not displayed_warning:
                        if language == 1:
                            print(f"\n✅ Gestartet: PID {pid}, Spiel: {game_folder}, Path: {path_norm}\n")

                        if language == 0:
                            print(f"\n✅ Started: PID {pid}, Game: {game_folder}, Path: {path_norm}\n")

                    if not only_local_db:
                        
                        # Twitch-Kategorie suchen
                        # Search Twitch Category
                        categories = search_twitch_category(token, game_folder)
##                        print(categories)
                        
                        # Speicher die Spiel- und Twitch-Daten in einem Dictionary
                        # Save game and twitch data in a dictionary
                        if categories:
                            best_match = False
                            highest_score = 0
                            # Zuerst exakte Übereinstimmung prüfen
                            for category in categories:
                                if game_folder.lower() == category["name"].lower():
                                    best_match = category
                                    break  # Falls exakter Match gefunden, abbrechen / break if exact match
                                
                            # Falls kein exakter Match gefunden, Fuzzy-Matching durchführen
                            # If no exact match make fuzzy match
                            if not best_match:
                                for category in categories:
                                    
                                    score = fuzz.ratio(game_folder.lower(), category["name"].lower(), score_cutoff=threshold)
                                    if score is not None and score > highest_score:  # Prüfe Threshold automatisch
                                        highest_score = score
                                        best_match = category
                                    else:
                                        game_splitted = game_folder.lower() if game_folder.isupper() else re.sub(r'(?<!^)(?=[A-Z])', ' ', game_folder).lower()
                                        # Zweiter Versuch mit toleranterem Matching
                                        fallback_score = fuzz.token_sort_ratio(game_splitted, category["name"].lower())
##                                        print(f"Fallback ratio: {fallback_score}")
                                        if fallback_score > threshold and fallback_score > highest_score:
                                            final_check_score = fuzz.ratio(game_splitted, category["name"].lower())
                                            if final_check_score > threshold:
                                                highest_score = fallback_score
                                                best_match = category                                      

                            
                           
                            if kick_enabled:
                                
                                kick_categories = search_kick_category(kick_token, kick_game_folder)
                                if kick_categories:
                                    kick_best_match = None
                                    highest_score_kick = 0

                                    # Exakte Übereinstimmung prüfen
                                    for kick_category in kick_categories:
                                        if kick_game_folder.lower() == kick_category["name"].lower():
                                            kick_best_match = kick_category
                                            break

                                    # Falls kein exakter Match, Fuzzy-Matching
                                    if not kick_best_match:
                                        for kick_category in kick_categories:
                                            score = fuzz.ratio(kick_game_folder.lower(), kick_category["name"].lower(), score_cutoff=threshold)
                                            if score is not None and score > highest_score_kick:
                                                highest_score_kick = score
                                                kick_best_match = kick_category
                                            else:
                                                kick_game_splitted = (
                                                    kick_game_folder.lower()
                                                    if kick_game_folder.isupper()
                                                    else re.sub(r'(?<!^)(?=[A-Z])', ' ', kick_game_folder).lower()
                                                )
                                                fallback_score = fuzz.token_sort_ratio(kick_game_splitted, kick_category["name"].lower())
                                                if fallback_score > threshold and fallback_score > highest_score_kick:
                                                    final_check_score = fuzz.ratio(kick_game_splitted, kick_category["name"].lower())
                                                    if final_check_score > threshold:
                                                        highest_score_kick = fallback_score
                                                        kick_best_match = kick_category

                            print(best_match)
                            if best_match:
                                if game_folder == "Silent Hill 2":
                                    game_data = {
                                        "Game": game_folder,
                                        "Path": os.path.normpath(exe_path),  
                                        "Twitch Category Name": best_match["name"],
                                        "Twitch Category ID": "2058570718",
                                        "Twitch Box Art": "https://static-cdn.jtvnw.net/ttv-boxart/2058570718_IGDB-285x380.jpg"
                                    }
                                elif game_folder == "Spyro The Dragon":
                                    category['id'] = "1885901697"
                                    game_data = {
                                        "Game": game_folder,
                                        "Path": os.path.normpath(exe_path),  
                                        "Twitch Category Name": best_match["name"],
                                        "Twitch Category ID": "1885901697",
                                        "Twitch Box Art": get_largest_box_art_url(category['box_art_url'], category['id'], width, height)
                                    }
                                elif game_folder == "Software and game development":
                                    game_data = {
                                        "Game": game_folder,
                                        "Path": "Not available in this Category",  
                                        "Twitch Category Name": best_match["name"],
                                        "Twitch Category ID": best_match["id"],
                                        "Twitch Box Art": get_largest_box_art_url(category['box_art_url'], category['id'], width, height)
                                    }                                    
                                else:
                                    game_data = {
                                        "Game": game_folder,
                                        "Path": os.path.normpath(exe_path),  
                                        "Twitch Category Name": best_match["name"],
                                        "Twitch Category ID": best_match["id"],
                                        "Twitch Box Art": get_largest_box_art_url(category['box_art_url'], category['id'], width, height)
                                    }
                                    
                                # Kick-Ergebnis ergänzen
                                if kick_best_match:
                                    game_data["Kick Category Name"] = kick_best_match["name"]
                                    game_data["Kick Category ID"] = str(kick_best_match["id"])
                                    game_data["Kick Thumbnail"] = kick_best_match["thumbnail"]
                                    kick_missing = False
                                else:
                                    kick_best_match = {
                                        "name": "No Match",
                                        "id": "No Match",
                                        "thumbnail": "No Match"
                                    }
                                    kick_missing = False                                  
                                    if language == 1:
                                        print(f"⚠️ Keine Kick-Kategorie für '{kick_game_folder}' gefunden.")
                                        if not show_console:
                                            start_logging()
                                            logging.info(f"⚠️ Keine Kick-Kategorie für '{kick_game_folder}' gefunden.")
                                            logging.info(f"⚠ Pfad aus welchem Name extrahiert wurde '{path_norm}")
                                    if language == 0:
                                        print(f"⚠️ No Kick Category found for '{game_folder}'.")
                                        if not show_console:
                                            start_logging()
                                            logging.info(f"⚠️ No Kick Category found for '{kick_game_folder}'.")
                                            logging.info(f"⚠ Path from which game name got extracted '{path_norm}")
                                    kick_failed = True
                                    if message:
                                        send_message(game_folder, category_name, kick_category_name, kick_failed)
                            
                                saved_games.append(game_data)

                                # Ausgabe der gespeicherten Daten, aber nur einmal
                                # Output data only once
                                if game_folder not in displayed_games:
                                    if language == 1:
                                        print("-" * 90)
                                        print(f"   🎮 Gefundene Twitch-Kategorie für '{game_folder}':")
                                        print(f"   📝 {best_match['name']} (ID: {best_match['id']})")
                                        print(f"   📸 Twitch Box Art: {get_largest_box_art_url(best_match['box_art_url'], best_match['id'], width, height)}")
                                        if kick_enabled:
                                            print(f"   🟢 Kick Kategorie: {kick_best_match['name']} (ID: {kick_best_match['id']})")
                                        print("-" * 90)

                                    if language == 0:
                                        print("-" * 90) 
                                        print(f"   🎮 Found Twitch category for '{game_folder}':")
                                        print(f"   📝 {best_match['name']} (ID: {best_match['id']})")
                                        print(f"   📸 Twitch Box Art: {get_largest_box_art_url(best_match['box_art_url'], best_match['id'], width, height)}")
                                        if kick_enabled:
                                            print(f"   🟢 Kick Category: {kick_best_match['name']} (ID: {kick_best_match['id']})")
                                        print("-" * 90)

                                    category_name = best_match['name']
                                    if kick_enabled:
                                        kick_category_name = kick_best_match['name']
                                    displayed_games.add(game_folder)
                                    first_save = True
                                    if is_streamerbot_running():
                                        if category_set_already != category_name:
                                            if kick_enabled:
                                                category_change(category_name, kick_category_name)
                                            else:
                                                category_change(category_name)
                                            category_set_already = category_name
                                            if message:
                                                if kick_enabled:                                                
                                                    send_message(game_folder, category_name, kick_category_name, kick_failed=False)
                                                else:
                                                    send_message(game_folder, category_name)
                            else:
                                if not displayed_warning:
                                    if language == 1:
                                        print(f"⚠️ Keine Twitch-Kategorie für '{game_folder}' gefunden.")
                                        if not show_console:
                                            start_logging()
                                            logging.info(f"⚠️ Keine Twitch-Kategorie für '{game_folder}' gefunden.")
                                            logging.info(f"⚠ Pfad aus welchem Name extrahiert wurde '{path_norm}")
                                    if language == 0:
                                        print(f"⚠️ No Twitch Category found for '{game_folder}'.")
                                        if not show_console:
                                            start_logging()
                                            logging.info(f"⚠️ No Twitch Category found for '{game_folder}'.")
                                            logging.info(f"⚠ Path from which game name got extracted '{path_norm}")
                                    
                                    displayed_warning = True
                                    failed = True
                                    if message:
                                        if kick_enabled:
                                            send_message(game_folder, category_name, kick_category_name)
                                        else:
                                            send_message(game_folder, category_name)
                        else:
                            if not displayed_warning:
                                if language == 1:
                                    print(f"⚠️ Keine Twitch-Kategorie für '{game_folder}' gefunden.")
                                    if not show_console:
                                        start_logging()
                                        logging.info(f"⚠️ Keine Twitch-Kategorie für '{game_folder}' gefunden.")
                                        logging.info(f"⚠ Pfad aus welchem Name extrahiert wurde '{path_norm}")
                                if language == 0:
                                    print(f"⚠️ No Twitch Category found for '{game_folder}'.")
                                    if not show_console:
                                        start_logging()
                                        logging.info(f"⚠️ No Twitch Category found for '{game_folder}'.")
                                        logging.info(f"⚠ Path from which game name got extracted '{path_norm}")
                                
                                displayed_warning = True
                                failed = True
                                if message:
                                    if kick_enabled:
                                        send_message(game_folder, category_name, kick_category_name)
                                    else:                                    
                                        send_message(game_folder, category_name)   
                    else:
                        if not displayed_warning:
                            if game_data == None:
                                if language == 1:
                                    print("-" * 90)
                                    print(f"⚠ Nur Lokale Datenbank verwenden ist aktiviert.")                       
                                    print(f"⚠️ Spiel nicht in lokaler Datenbank vorhanden.")
                                    print("-" * 90)
                                    if not show_console:
                                        start_logging()
                                        logging.warning(f"Nur lokale Datenbank verwenden ist aktiviert!")
                                        logging.info(f"{game_folder} ist nicht in lokaler Datenbank.")                                
                                        
                                if language == 0:
                                    print("-" * 90)
                                    print(f"⚠ Only local database is activated.")                       
                                    print(f"⚠️ Game is not in local database.")
                                    print("-" * 90)
                                    if not show_console:
                                        start_logging()
                                        logging.warning(f"Only local db is activated!")
                                        logging.info(f"{game_folder} not in local database.")       
                            displayed_warning = True
                            failed = True
                            not_in_local_db = True
                            if message:
                                if kick_enabled:                                
                                    send_message(game_folder, category_name, kick_category_name)
                                else:                                
                                    send_message(game_folder, category_name)

                            
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue
        time.sleep(1)        
        delayed_reset_called = {}  # Wird verwendet, um Verzögerungen pro Ordner zu verfolgen

        def delayed_category_reset(game_folder, displayed_games, seen_processes, current_seen):
            global delay_programming
            global known_exe_names

            delay_ms = delay_programming

            def reset():
                global category_set_already
               ## print("Reset wird ausgeführt")
               ## print(game_folder)
               ## print(displayed_games)

                # Überprüfen, ob der Ordner noch offen ist
                ##exe_list = ["UnrealEditor.exe", "Blender.exe", "AnotherTool.exe"]
                exe_list = known_exe_names
                print(exe_list)
                
                folder_open = False
                try:
                    for proc in psutil.process_iter(["pid", "name", "exe"]):
                        exe_path = proc.info["exe"]
                        if exe_path:
                            # prüfe, ob eine der exe-Namen in exe_path vorkommt (case-insensitive)
                            if any(exe_name.lower() in exe_path.lower() for exe_name in exe_list):
                                folder_open = True
                                break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                if folder_open:
                    ##print(f"Ordner {game_folder} ist noch geöffnet. Kein Reset.")
                    return  # Ordner läuft noch, also keinen Reset durchführen
                displayed_warning = False
                displayed_warning_category = False
                
                # Wenn der Ordner nicht mehr läuft, Reset durchführen
                if game_folder in displayed_games:
                    displayed_games.remove(game_folder)
                    category_name = "Just Chatting"
                    kick_category_name = "Just Chatting"
                    failed = False                    
                    if is_streamerbot_running():
                        if category_set_already != category_name:
                            if kick_enabled:
                                category_change(category_name, kick_category_name)
                            else:
                                category_change(category_name)
                            if message:
                                if kick_enabled:
                                    send_message(game_folder, category_name, kick_category_name, kick_failed=False)
                                else:
                                    send_message(game_folder, category_name)
                    category_set_already = category_name

                # Reset den Status nach der Verzögerung
                delayed_reset_called[game_folder] = False
##                print("Delay fertig")
                
            # Die Verzögerung in Sekunden (umgerechnet von Millisekunden)
            delay_seconds = delay_ms / 1000.0

            # Starte den Thread, der nach der Verzögerung die Reset-Funktion ausführt
            threading.Thread(target=lambda: (time.sleep(delay_seconds), reset())).start()

        def delayed_category_reset_dynamic(game_folder, displayed_games, seen_processes, current_seen):
            global delay_general

            delay_ms = delay_general

            def reset():
                global category_set_already

                folder_open = False
                try:
                    for proc in psutil.process_iter(["pid", "name", "exe"]):
                        exe_path = proc.info["exe"]
                        if exe_path:
                            if game_folder.lower() in exe_path.lower():
                                folder_open = True
                                break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

                if folder_open:
                    return  # Ordner läuft noch, kein Reset

                if game_folder in displayed_games:
                    displayed_games.remove(game_folder)
                    category_name = "Just Chatting"
                    kick_category_name = "Just Chatting"
                    if is_streamerbot_running():
                        if category_set_already != category_name:
                            if kick_enabled:
                                category_change(category_name, kick_category_name)
                            else:
                                category_change(category_name)
                            if message:
                                if kick_enabled:
                                    send_message(game_folder, category_name, kick_category_name, kick_failed=False)
                                else:
                                    send_message(game_folder, category_name)
                    category_set_already = category_name

                delayed_reset_called[game_folder] = False

            delay_seconds = delay_ms / 1000.0
            threading.Thread(target=lambda: (time.sleep(delay_seconds), reset())).start()

        # Beispiel für die Verwendung
        # Überprüfen, ob der Prozess beendet wurde
        for unique_id in seen_processes - current_seen:
            pid, exe_path = unique_id

            if language == 1:
                print("-" * 90)
                print(f"   ❌ Beendet: PID {pid}, Spiel: {game_folder}")
                print("-" * 90)
            if language == 0:
                print("-" * 90)
                print(f"   ❌ Closed: PID {pid}, Game: {game_folder}")
                print("-" * 90)

            if game_folder == "Software and game development":
                if delay_programming and delay_programming > 0:
                    # Wenn das Spiel im Ordner geschlossen wird und die Verzögerung noch nicht gesetzt wurde
                    if game_folder not in delayed_reset_called or delayed_reset_called[game_folder] == False:
                        delayed_category_reset(game_folder, displayed_games, seen_processes, current_seen)  # 50 Sekunden Verzögerung
                        delayed_reset_called[game_folder] = False  # Verzögerung für diesen Ordner wurde gesetzt

            elif game_folder != "Software and game development":
                if delay_general and delay_general > 0:
                    
                    if game_folder not in delayed_reset_called or not delayed_reset_called[game_folder]:
                        delayed_category_reset_dynamic(game_folder, displayed_games, seen_processes, current_seen)
                        delayed_reset_called[game_folder] = True
                else:               
                    displayed_warning = False
                    displayed_warning_category = False

                    # Entferne das Spiel aus displayed_games, wenn es beendet wurde
                    if game_folder in displayed_games:
                        displayed_games.remove(game_folder)
                        category_name = "Just Chatting"
                        kick_category_name = "Just Chatting"
                        
                        failed = False
                        if is_streamerbot_running():
                            if category_set_already != category_name:
                                if kick_enabled:                                
                                    category_change(category_name, kick_category_name)
                                else:                                
                                    category_change(category_name) 
                                if message:
                                    if kick_enabled:
                                        send_message(game_folder, category_name, kick_category_name, kick_failed=False)
                                    else:
                                        send_message(game_folder, category_name)
                        category_set_already = category_name

                        
##            # Entferne das Spiel aus displayed_games, wenn es beendet wurde
##            # Remove game from displayed_games when it is closed        
##            if game_folder in displayed_games:
##                displayed_games.remove(game_folder)
##                category_name = "Just Chatting"
##                category_set_already = category_name
##                failed = False
##                if is_streamerbot_running():
##                    category_change(category_name)
##                    send_message(game_folder, category_name)

                
        # Aktualisiere die Liste der bekannten Prozesse
        # Update list of known processes
        seen_processes = current_seen.copy()
        # Speichern der gesammelten Spielinformationen in einer JSON-Datei
        # Save all Infos in json
        if first_save:
            if saved_games != previous_saved_games:
                save_saved_games(saved_games)
                previous_saved_games = saved_games.copy()

        if watch_obs:

            # Überprüfen, ob OBS bereits gestartet wurde und nun nicht mehr läuft
            # Check if OBS already got started and now closed
            if obs_started and not is_obs_running():
                if language == 1:
                    print("⚠️ OBS wurde geschlossen. Beende das Programm...\n")
                if language == 0:
                    print("⚠️ OBS closed. Closing script...\n")
                time.sleep(5)
                terminate_current_instance()
                ##sys.exit(0)  # Beendet das Programm / closes programm

            # Überprüfen, ob OBS zum ersten Mal läuft
            # Check if OBS is started the first time
            if is_obs_running() and not obs_started:
                if language == 1:
                    print("✅ OBS wurde gestartet. Jetzt wird das Programm überwacht...\n")
                if language == 0:
                    print("✅ OBS started. Programm is now monitored...\n")
                obs_started = True

        if watch_streamerbot:
            # Überprüfen, ob OBS bereits gestartet wurde und nun nicht mehr läuft
            # Check if streamerbot already got started and now closed
            if streamerbot_started and not is_streamerbot_running():
                if language == 1:
                    print("⚠️ Streamer.bot wurde geschlossen. Beende das Programm...\n")
                if language == 0:
                    print("⚠️ Streamer.bot closed. Closing script...\n")
                time.sleep(5)
                ##sys.exit(0)  # Beendet das Programm / close Programm
                terminate_current_instance()

            # Überprüfen, ob Streamerbot zum ersten Mal läuft
            # Check if streamerbot is started the first time
            if is_streamerbot_running() and not streamerbot_started:
                if language == 1:
                    print("✅ Streamer.bot wurde gestartet. Jetzt wird das Programm überwacht...\n")
                if language == 0:
                    print("✅ Streamer.bot opened. Programm is now monitored...\n")
                streamerbot_started = True
            
        # Kurze Pause, um Systemressourcen zu schonen
        # short pause to save systemressources
        time.sleep(2)
        
# PyQt GUI starten (MUSS im Hauptthread laufen)
# Start PyQt gui, needs to run in mainthread
def start_gui():
    global gui
    app = QApplication([])

    # GUI initialisieren
    # Initialise gui
    console = ConsoleApp()
    console.show()
    gui = True

    # Umleitung der Standardausgabe
    # detour standardoutput
    sys.stdout = ConsoleRedirector(log_queue)
    sys.stderr = ConsoleRedirector(log_queue)

    # Logik im Hintergrund starten
    # Start logic in mainthread
    logic_thread = threading.Thread(target=main_logic)
    logic_thread.start()
    # Event, das ausgeführt wird, wenn das Fenster geschlossen wird
    # Event when window is closed
    def on_exit():
        if language == 1:
            print("GUI geschlossen. Beende das Script.")
        if language == 0:
            print("GUI closed. Exit Script.")
        os._exit(0)  # Beendet das Script / Exit program

    # Event verbinden, um das Script zu beenden, wenn das Fenster geschlossen wird
    # Event bound to end script when window is closed
    app.aboutToQuit.connect(on_exit)
    # GUI Event loop starten
    # Start gui loop
    app.exec_()
        
if __name__ == '__main__':

    if show_console:
        start_gui() 
    else:
        main_logic()
