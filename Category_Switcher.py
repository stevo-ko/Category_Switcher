"""
// Author: stevo_ko , https://twitch.tv/stevo_ko , Discord: stevo_ko on the streamer.bot Server, Github: https://github.com/stevo-ko/Category_Switcher
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
from ctypes import wintypes
import subprocess
import logging
import threading
import queue
import math
import io
import contextlib
import asyncio
import shutil
import hashlib
import struct


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
        "port": "",
        "url": ""
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
            "CrashMailer_64.exe",
            "GameLoader.exe"
        ],
        "excluded_folders": [
            "bin",
            "binaries",
            "win64",
            "win64r",
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
            "EGS",
            "WindowsNoEditor",
            "WindowsNoEditorNoDrivers",
            "WindowsNoDrivers",
            "game2"
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
        "delay_playnite": 0,
        "kick_enabled": False,
        "playnite_enabled": False,
        "matchfix_update_toast_notification": True,
        "backend_api": True,
    },
    "default_category": {
        "enabled": False,
        "twitch_category": "Just Chatting",
        "kick_category": "Just Chatting",
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
version_path = os.path.join(programm_ordner, "Version.json")

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

def restore_critical_files(files_to_restore):
    backup_folder = os.path.join(programm_ordner, "backups")
    if not os.path.isdir(backup_folder):
        return False

    restored = False
    for file in files_to_restore:
        backups = sorted(
            [f for f in os.listdir(backup_folder) if f.startswith(file + "_") and f.endswith(".bak")],
            key=lambda x: os.path.getmtime(os.path.join(backup_folder, x)),
            reverse=True
        )

        if not backups:
            continue

        latest_backup = os.path.join(backup_folder, backups[0])

        try:
            with open(latest_backup, "r", encoding="utf-8") as f:
                json.load(f)
        except json.JSONDecodeError:
            continue

        destination_file = os.path.join(programm_ordner, file)
        shutil.copy2(latest_backup, destination_file)
        restored = True
    return restored


def check_file_validity():
    critical_files = ["config.json", "game_data.json", "Version.json"]
    invalid = []
    for file in critical_files:
        file_path = os.path.join(programm_ordner, file)
        if not os.path.exists(file_path):
            invalid.append(file)
            continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json.load(f)
        except json.JSONDecodeError:
            invalid.append(file)
    return invalid  # leere Liste = alles ok

invalid_files = check_file_validity()
if invalid_files:
    restore_critical_files(invalid_files)


update_from_version_below_2 = False

def update_from_old_version(current):
    global update_from_version_below_2

    if "kick" not in current:
        update_from_version_below_2 = True
        
    else:
        update_from_version_below_2 = False    
    return update_from_version_below_2

try:
    with open("config.json", "r", encoding="utf-8") as file:
        config = json.load(file)

except (FileNotFoundError, json.JSONDecodeError):
##    print(f"Error loading {config_path}. Create default config.")
    save_default_config()
    config = default_config

else:
    # Mische fehlende Keys aus default_config ein
    update_from_old_version(config)
    updated_config = merge_config(default_config, config)
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(updated_config, f, indent=4)
    config = updated_config
    remove_from_config()
    
def backup_critical_files():
    # Backup der wichtigen Dateien
    # Backup important files
    critical_files = ["config.json", "game_data.json", "Version.json"]
    backup_folder = os.path.join(programm_ordner, "backups")
    os.makedirs(backup_folder, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")

    for file in critical_files:
        source_file = os.path.join(programm_ordner, file)
        destination_file = os.path.join(backup_folder, f"{file}_{timestamp}.bak")

        if os.path.exists(source_file):
            shutil.copy2(source_file, destination_file)
            print(f"Backup erstellt: {destination_file}")

            # Alte Backups löschen, wenn mehr als 10 vorhanden sind 
            backups = sorted(
                [f for f in os.listdir(backup_folder) if f.startswith(file + "_")],
                key=lambda x: os.path.getmtime(os.path.join(backup_folder, x))
            )

            # Falls mehr als 10, die ältesten löschen
            while len(backups) > 10:
                oldest = backups.pop(0)
                os.remove(os.path.join(backup_folder, oldest))
                ##print(f"Altes Backup gelöscht: {oldest}")
        #else:
            #print(f"Datei nicht gefunden: {source_file}")
           
backup_critical_files()       

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

modules = ["rapidfuzz", "requests", "psutil", "pydantic", "PyQt5", "watchdog", "toasted", "PIL"]

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
from numpy import stack
from rapidfuzz import fuzz
import requests
import psutil
from pydantic import BaseModel
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QMessageBox, QLabel, QDialog, QLabel, QFrame, QScrollArea, QSizePolicy, QStackedWidget
from PyQt5.QtCore import QTimer, QMetaObject, QObject, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QCursor, QPixmap
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from toasted import Toast, Text, Progress, ToastTextStyle, ToastTextAlign, ToastDuration, ToastDismissReason, ToastScenario, ToastImagePlacement, ToastNotificationMode, ToastSound, Button, ToastButtonStyle, Image, ToastResult
from PIL import Image as PILImage

class _ChangelogSignal(QObject):
    open_changelog = pyqtSignal(str, str, str)

_changelog_signal = _ChangelogSignal()

class _GuiSignals(QObject):
    show_console_window = pyqtSignal()
    hide_console_window = pyqtSignal()

_gui_signals = _GuiSignals()

def get_resource_path(relative_path):
    """Pfad zu Ressourcen im _internal/Assets Ordner neben der exe/py"""
    if getattr(sys, 'frozen', False):
        # exe → basiert auf Ordner der exe
        base_path = os.path.dirname(sys.executable)
    else:
        # py → basiert auf Ordner des Skripts
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, "_internal", "Assets", relative_path)
# Dummy für Test
CHANGELOG_DUMMY = """
 
## (DE)
- Done a few fixes not worthy of mentioning.. or i forgot what it was 

## (EN)
- Done a few fixes not worthy of mentioning.. or i forgot what it was 

"""

def _open_changelog_window(content: str, current_version: str, lang_suffix: str):
    try:
        app_instance = QApplication.instance()
        if not app_instance:
            app_instance = QApplication(sys.argv)

        dialog = QDialog()
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setWindowTitle("Matchfixes Changelog")
        icon_path = get_resource_path("icon.ico")
        dialog.setWindowIcon(QIcon(icon_path))
        dialog.setAttribute(Qt.WA_TranslucentBackground, True)
        dialog.setAttribute(Qt.WA_QuitOnClose, False)
        dialog.resize(700, 480)

        screen = app_instance.primaryScreen().geometry()
        dialog.move(
            (screen.width()  - dialog.width())  // 2,
            (screen.height() - dialog.height()) // 2,
        )

        # ── Parse markdown ─────────────────────────────────
        fallback_suffix = "(EN)" if lang_suffix == "(DE)" else "(DE)"

        raw_blocks: dict = {}
        order: list = []
        cur_key = None
        cur_bullets = []
        for line in content.splitlines():
            if line.startswith("## "):
                if cur_key is not None:
                    raw_blocks[cur_key] = cur_bullets
                cur_key = line[3:].strip()
                cur_bullets = []
                if cur_key not in order:
                    order.append(cur_key)
            elif line.startswith(("- ", "* ")) and cur_key is not None:
                cur_bullets.append(line[2:].strip())
        if cur_key is not None:
            raw_blocks[cur_key] = cur_bullets

        def _bullets_for(bare: str) -> list:
            for key in [f"{bare} {lang_suffix}", f"{bare} {fallback_suffix}", bare]:
                if key in raw_blocks:
                    return raw_blocks[key]
            return []

        seen: list = []
        parsed_versions: list = []
        for key in order:
            bare = re.sub(r'\s*\((DE|EN)\)\s*$', '', key).strip()
            if bare in seen:
                continue
            seen.append(bare)
            parsed_versions.append((bare, _bullets_for(bare)))

        if not parsed_versions:
            parsed_versions = [(current_version, [
                "Keine Einträge gefunden." if "(DE)" in lang_suffix else "No entries found."
            ])]

        latest_entry = next(
            (e for e in parsed_versions if e[0] == current_version),
            parsed_versions[0]
        )
        latest_ver     = latest_entry[0]
        latest_bullets = latest_entry[1] or [
            "Keine Einträge." if "(DE)" in lang_suffix else "No entries."
        ]
        older_versions = [e for e in parsed_versions if e[0] != latest_ver]

        # ── Outer container ────────────────────────────────
        outer = QFrame(dialog)
        outer.setObjectName("outerFrame")
        outer.setGeometry(0, 0, 700, 480)
        outer.setStyleSheet("""
            #outerFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #080F13, stop:0.25 #0C1C2A, stop:0.5 #132E40,
                    stop:0.72 #1A3D52, stop:0.88 #204A60, stop:1 #265468);
                border: 1px solid #28AEED;
                border-radius: 14px;
            }
        """)

        main_layout = QVBoxLayout(outer)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Drag ───────────────────────────────────────────
        _drag_pos = [None]
        def mousePressEvent(e):
            if e.button() == Qt.LeftButton:
                _drag_pos[0] = e.globalPos() - dialog.frameGeometry().topLeft()
        def mouseMoveEvent(e):
            if e.buttons() == Qt.LeftButton and _drag_pos[0]:
                dialog.move(e.globalPos() - _drag_pos[0])
        def mouseReleaseEvent(e):
            _drag_pos[0] = None

        # ── Titlebar ───────────────────────────────────────
        titlebar = QFrame()
        titlebar.setObjectName("titlebar")
        titlebar.setFixedHeight(38)
        titlebar.setStyleSheet("""
            #titlebar {
                background: transparent;
                border-bottom: 1px solid #1D3545;
                border-top-left-radius: 14px;
                border-top-right-radius: 14px;
            }
        """)
        titlebar.mousePressEvent   = mousePressEvent
        titlebar.mouseMoveEvent    = mouseMoveEvent
        titlebar.mouseReleaseEvent = mouseReleaseEvent

        tb_layout = QHBoxLayout(titlebar)
        tb_layout.setContentsMargins(14, 0, 14, 0)
        tb_layout.setSpacing(6)

        def make_dot(idle_bg, idle_border, hover_bg, cmd):
            btn = QPushButton()
            btn.setFixedSize(12, 12)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {idle_bg}; border: 1px solid {idle_border}; border-radius: 6px;
                }}
                QPushButton:hover {{ background: {hover_bg}; border-color: {hover_bg}; }}
            """)
            btn.clicked.connect(cmd)
            return btn
           
        icon_lbl = QLabel()
        px = QPixmap(get_resource_path("icon.ico"))
        icon_lbl.setPixmap(px.scaled(14, 14, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_lbl.setStyleSheet("background: transparent; border: none;")
        tb_layout.addWidget(icon_lbl)

        t1 = QLabel("Matchfix Liste" if "(DE)" in lang_suffix else "Matchfix List")
        t1.setFont(QFont("Segoe UI", 10))
        t1.setStyleSheet("color: #bfcfd6; background: transparent; border: none;")
        tb_layout.addWidget(t1)

        t2 = QLabel("— Changelog")
        t2.setFont(QFont("Segoe UI", 10))
        t2.setStyleSheet("color: #5A8A9A; background: transparent; border: none;")
        tb_layout.addWidget(t2)
        tb_layout.addStretch()

        tb_badge = QLabel(f" {latest_ver} latest ")
        tb_badge.setFont(QFont("Cascadia Code", 9, QFont.Bold))
        tb_badge.setStyleSheet("""
            color: #28AEED; background: rgba(40,174,237,0.10);
            border: 1px solid rgba(40,174,237,0.25);
            border-radius: 20px; padding: 1px 4px;
        """)
        #tb_layout.addWidget(tb_badge)
        tb_sep = QFrame(); tb_sep.setFixedSize(1, 14)
        tb_sep.setStyleSheet("background: #1D3545; border: none;")
        tb_layout.addWidget(tb_sep)
        tb_layout.addSpacing(4)
        tb_layout.addSpacing(6)
        tb_layout.addWidget(make_dot("#1e5a7a", "#1e5a7a", "#28AEED", dialog.showMinimized))
        tb_layout.addWidget(make_dot("#7a1f1f", "#7a1f1f", "#E81123", dialog.close))
        main_layout.addWidget(titlebar)

        # ── Accent line ────────────────────────────────────
        accent = QFrame()
        accent.setFixedHeight(1)
        accent.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #28AEED, stop:0.5 #00D4E8, stop:1 #1A6A9A);
            border: none;
        """)
        main_layout.addWidget(accent)

        # ── Latest version block ───────────────────────────
        latest_frame = QFrame()
        latest_frame.setStyleSheet("background: transparent;")
        lf_layout = QVBoxLayout(latest_frame)
        lf_layout.setContentsMargins(18, 14, 24, 0)
        lf_layout.setSpacing(0)

        hdr_row = QWidget()
        hdr_row.setFixedHeight(26)
        hdr_row.setStyleSheet("background: transparent;")
        hdr_rl = QHBoxLayout(hdr_row)
        hdr_rl.setContentsMargins(0, 0, 0, 0)
        hdr_rl.setSpacing(8)
        hdr_rl.setAlignment(Qt.AlignVCenter)

        dot_bar = QFrame()
        dot_bar.setObjectName("dotBar")
        dot_bar.setFixedSize(2, 20)
        dot_bar.setStyleSheet("""
            #dotBar {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #1A6A9A, stop:0.5 #28AEED, stop:1 #1A6A9A);
                border-radius: 1px; border: none;
            }
        """)
        hdr_rl.addWidget(dot_bar)

        ver_lbl = QLabel(latest_ver)
        ver_lbl.setFont(QFont("Cascadia Code", 14, QFont.Bold))
        ver_lbl.setStyleSheet("color: #28AEED; background: transparent; border: none;")
        hdr_rl.addWidget(ver_lbl)

        latest_tag = QLabel(" latest ")
        latest_tag.setFont(QFont("Cascadia Code", 9, QFont.Bold))
        latest_tag.setFixedHeight(18)
        latest_tag.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        latest_tag.setStyleSheet("""
            color: #28AEED; background: rgba(40,174,237,0.10);
            border: 1px solid rgba(40,174,237,0.20);
            border-radius: 4px; padding: 0px 4px;
        """)
        hdr_rl.addWidget(latest_tag)

        fade_line = QFrame()
        fade_line.setFixedHeight(1)
        fade_line.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 rgba(40,174,237,0.4), stop:1 transparent);
            border: none;
        """)
        hdr_rl.addWidget(fade_line, 1)
        
        lf_layout.addWidget(hdr_row)

        sec_line = QFrame()
        sec_line.setFixedHeight(1)
        sec_line.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 rgba(40,174,237,0.5), stop:0.6 rgba(40,174,237,0.12), stop:1 transparent);
            border: none; margin: 4px 0 6px;
        """)
        lf_layout.addWidget(sec_line)
        lf_layout.addSpacing(10)

        # ── Bullet helpers ─────────────────────────────────
        def _make_bullet_row(raw, last=False):
            raw_html = re.sub(
                r'`([^`]+)`',
                r'<span style="font-family:Cascadia Code;font-size:11px;color:#28AEED;'
                r'background:rgba(40,174,237,0.08);border:1px solid rgba(40,174,237,0.15);'
                r'border-radius:3px;padding:1px 5px;">\1</span>',
                raw
            )
            raw_html = re.sub(
                r'(→|->)',
                r'<span style="color:#28AEED;margin:0 2px;">→</span>',
                raw_html
            )
            full_html = (
                f'<table cellspacing="0" cellpadding="0"><tr>'
                f'<td valign="top" style="padding-top:4px;padding-right:8px;width:12px;">'
                f'<span style="color:#28AEED;font-size:8px;">●</span></td>'
                f'<td valign="top"><span style="color:#9DD4E8;font-size:12px;">{raw_html}</span></td>'
                f'</tr></table>'
            )
            border_bottom = "none" if last else "1px solid #0e1c28"
            row = QFrame()
            row.setObjectName("bRow")
            row.setStyleSheet(f"#bRow {{ background: transparent; border-bottom: {border_bottom}; }}")
            row.setMouseTracking(True)
            row.enterEvent = lambda e, r=row, b=border_bottom: r.setStyleSheet(
                f"#bRow {{ background: #1a2e42; border-bottom: {b}; }}"
            )
            row.leaveEvent = lambda e, r=row, b=border_bottom: r.setStyleSheet(
                f"#bRow {{ background: transparent; border-bottom: {b}; }}"
            )
            rl = QHBoxLayout(row)
            rl.setContentsMargins(10, 6, 14, 6)
            rl.setSpacing(0)
            txt = QLabel(full_html)
            txt.setFont(QFont("Segoe UI", 10))
            txt.setStyleSheet("background: transparent; border: none; padding: 0;")
            txt.setWordWrap(True)
            txt.setTextFormat(Qt.RichText)
            txt.setTextInteractionFlags(Qt.TextSelectableByMouse)
            txt.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            rl.addWidget(txt)
            return row

        def make_entry_card(bullets):
            card = QFrame()
            card.setObjectName("entryCard")
            card.setStyleSheet("""
                #entryCard {
                    background: #162535;
                    border: 1px solid #1D3545;
                    border-radius: 10px;
                }
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(0, 0, 0, 0)
            cl.setSpacing(0)
            for i, raw in enumerate(bullets):
                cl.addWidget(_make_bullet_row(raw, last=(i == len(bullets) - 1)))
                
            return card
        
        latest_scroll = QScrollArea()
        latest_scroll.setViewportMargins(0, 0, 5, 0)
        latest_scroll.viewport().setStyleSheet("background: transparent;")
        latest_scroll.setWidgetResizable(True)
        latest_scroll.setWidget(make_entry_card(latest_bullets))
        latest_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        latest_scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollBar:vertical {
                background: transparent; width: 10px;
                margin: 4px 2px 4px 0px;
            }
            QScrollBar::handle:vertical {
                background: #4a9aba; border-radius: 3px; min-height: 24px;
            }
            QScrollBar::handle:vertical:hover { background: #28AEED; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)
        lf_layout.addWidget(latest_scroll)
        main_layout.addWidget(latest_frame)
        
        main_layout.addStretch()

        # ── Older versions section ─────────────────────────
        if older_versions:
            lbl_show   = "Ältere Versionen anzeigen"   if "(DE)" in lang_suffix else "Show older versions"
            lbl_hide   = "Zurück zur neuen Version" if "(DE)" in lang_suffix else "Back to latest version"
            lbl_search = "Suche nach Version…"      if "(DE)" in lang_suffix else "Search for version…"
            lbl_back   = "Zurück zur Übersicht"     if "(DE)" in lang_suffix else "Back to overview"

            # ── Toggle row im main_layout (collapsed state) ─
            toggle_frame_main = QFrame()
            toggle_frame_main.setStyleSheet("background: transparent;")
            tfm_layout = QHBoxLayout(toggle_frame_main)
            tfm_layout.setContentsMargins(18, 12, 18, 8)
            tfm_layout.setSpacing(8)
            
            toggle_btn_main = QPushButton("▾")
            toggle_btn_main.setObjectName("toggleBtn")
            toggle_btn_main.setFixedSize(18, 18)
            toggle_btn_main.setStyleSheet("""
                #toggleBtn {
                    background: #0D1E2C; border: 1px solid #1D3545;
                    border-radius: 4px; color: #3A6070; font-size: 9px;
                }
            """)
            toggle_btn_main.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            
            lbl_weitere = "weitere" if "(DE)" in lang_suffix else "more"
            toggle_lbl_main = QLabel(f"{lbl_show}  ({len(older_versions)} {lbl_weitere})")
            toggle_lbl_main.setFont(QFont("Segoe UI", 10))
            toggle_lbl_main.setStyleSheet("color: #3A6070; background: transparent; border: none;")
            toggle_lbl_main.setAttribute(Qt.WA_TransparentForMouseEvents, True)

            tc_main = QWidget()
            tc_main.setStyleSheet("background: transparent;")
            tc_main.setCursor(QCursor(Qt.PointingHandCursor))
            tc_l = QHBoxLayout(tc_main)
            tc_l.setContentsMargins(0, 0, 0, 0)
            tc_l.setSpacing(8)
            tc_l.addWidget(toggle_btn_main)
            tc_l.addWidget(toggle_lbl_main)

            def _tc_main_enter(e):
                toggle_btn_main.setStyleSheet("#toggleBtn { background: rgba(40,174,237,0.1); border: 1px solid rgba(40,174,237,0.3); border-radius: 4px; color: #28AEED; font-size: 9px; }")
                toggle_lbl_main.setStyleSheet("color: #28AEED; background: transparent; border: none;")
            def _tc_main_leave(e):
                toggle_btn_main.setStyleSheet("#toggleBtn { background: #0D1E2C; border: 1px solid #1D3545; border-radius: 4px; color: #3A6070; font-size: 9px; }")
                toggle_lbl_main.setStyleSheet("color: #3A6070; background: transparent; border: none;")
            tc_main.enterEvent = _tc_main_enter
            tc_main.leaveEvent = _tc_main_leave
            tc_main.mousePressEvent = lambda e: expand()

            tl_line = QFrame()
            tl_line.setFixedHeight(1)
            tl_line.setStyleSheet("background: #1D3545; border: none;")

            tfm_layout.addWidget(tc_main)
            tfm_layout.addWidget(tl_line, 1)
            main_layout.addWidget(toggle_frame_main)

            # ── Overlay (expanded state) ────────────────────
            # Direkt Kind von outer, außerhalb des Layouts
            # Startet nach dem Accent-Streifen (y=40), endet über dem Footer
            OVERLAY_Y = 40   # titlebar(38) + accent(1) + 1px Puffer
            FOOTER_H  = 45   # footer(44) + sep(1)

            overlay = QFrame(outer)
            overlay.setObjectName("overlay")
            overlay.setStyleSheet("""
                #overlay {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                        stop:0 #080F13, stop:0.25 #0C1C2A, stop:0.5 #132E40,
                        stop:0.72 #1A3D52, stop:0.88 #204A60, stop:1 #265468);
                    
                }
            """)
            overlay.setVisible(False)

            ov_layout = QVBoxLayout(overlay)
            ov_layout.setContentsMargins(0, 0, 0, 0)
            ov_layout.setSpacing(0)

            # Toggle row oben im Overlay
            toggle_frame_ov = QFrame()
            toggle_frame_ov.setStyleSheet("background: transparent;")
            tfo_layout = QHBoxLayout(toggle_frame_ov)
            tfo_layout.setContentsMargins(18, 10, 18, 6)
            tfo_layout.setSpacing(8)

            toggle_btn_ov = QPushButton("▴")
            toggle_btn_ov.setObjectName("toggleBtnOv")
            toggle_btn_ov.setFixedSize(18, 18)
            toggle_btn_ov.setStyleSheet("""
                #toggleBtnOv {
                    background: #0D1E2C; border: 1px solid #1D3545;
                    border-radius: 4px; color: #3A6070; font-size: 9px;
                }
            """)
            toggle_btn_ov.setAttribute(Qt.WA_TransparentForMouseEvents, True)

            toggle_lbl_ov = QLabel(lbl_hide)
            toggle_lbl_ov.setFont(QFont("Segoe UI", 10))
            toggle_lbl_ov.setStyleSheet("color: #3A6070; background: transparent; border: none;")
            toggle_lbl_ov.setAttribute(Qt.WA_TransparentForMouseEvents, True)

            tc_ov = QWidget()
            tc_ov.setStyleSheet("background: transparent;")
            tc_ov.setCursor(QCursor(Qt.PointingHandCursor))
            tc_ov_l = QHBoxLayout(tc_ov)
            tc_ov_l.setContentsMargins(0, 0, 0, 0)
            tc_ov_l.setSpacing(8)
            tc_ov_l.addWidget(toggle_btn_ov)
            tc_ov_l.addWidget(toggle_lbl_ov)

            def _tc_ov_enter(e):
                toggle_btn_ov.setStyleSheet("#toggleBtnOv { background: rgba(40,174,237,0.1); border: 1px solid rgba(40,174,237,0.3); border-radius: 4px; color: #28AEED; font-size: 9px; }")
                toggle_lbl_ov.setStyleSheet("color: #28AEED; background: transparent; border: none;")
            def _tc_ov_leave(e):
                toggle_btn_ov.setStyleSheet("#toggleBtnOv { background: #0D1E2C; border: 1px solid #1D3545; border-radius: 4px; color: #3A6070; font-size: 9px; }")
                toggle_lbl_ov.setStyleSheet("color: #3A6070; background: transparent; border: none;")
            tc_ov.enterEvent = _tc_ov_enter
            tc_ov.leaveEvent = _tc_ov_leave
            tc_ov.mousePressEvent = lambda e: collapse()

            to_line = QFrame()
            to_line.setFixedHeight(1)
            to_line.setStyleSheet("background: #1D3545; border: none;")

            tfo_layout.addWidget(tc_ov)
            tfo_layout.addWidget(to_line, 1)
            ov_layout.addWidget(toggle_frame_ov)
            ov_layout.setSpacing(8)

            # Search bar
            search_frame = QFrame()
            search_frame.setFixedHeight(34)
            search_frame.setStyleSheet("background: transparent;")
            sf_layout = QHBoxLayout(search_frame)
            sf_layout.setContentsMargins(18, 0, 18, 4)

            search_box = QFrame()
            search_box.setObjectName("sBox")
            search_box.setStyleSheet(
                "#sBox { background: #0D1E2C; border: 1px solid #1D3545; border-radius: 8px; }"
            )

            sb_l = QHBoxLayout(search_box)
            sb_l.setContentsMargins(10, 0, 10, 0)
            sb_l.setSpacing(6)

            s_icon = QLabel("⌕")
            s_icon.setFont(QFont("Segoe UI", 11))
            s_icon.setStyleSheet("color: #2d4455; background: transparent; border: none;")
            sb_l.addWidget(s_icon)

            search_input = QLineEdit()
            search_input.setPlaceholderText(lbl_search)
            search_input.setFont(QFont("Segoe UI", 10))
            search_input.setStyleSheet(
                "QLineEdit { background: transparent; border: none; color: #9DD4E8; padding: 0; }"
            )
            def _on_focus_in(e):
                search_box.setStyleSheet(
                    "#sBox { background: #0D1E2C; border: 1px solid #28AEED; border-radius: 8px; }"
                )
                QLineEdit.focusInEvent(search_input, e)

            def _on_focus_out(e):
                search_box.setStyleSheet(
                    "#sBox { background: #0D1E2C; border: 1px solid #1D3545; border-radius: 8px; }"
                )
                QLineEdit.focusOutEvent(search_input, e)

            def _on_enter(e):
                if not search_input.hasFocus():
                    search_box.setStyleSheet(
                        "#sBox { background: #0D1E2C; border: 1px solid #28456A; border-radius: 8px; }"
                    )

            def _on_leave(e):
                if not search_input.hasFocus():
                    search_box.setStyleSheet(
                        "#sBox { background: #0D1E2C; border: 1px solid #1D3545; border-radius: 8px; }"
                    )

            search_input.focusInEvent  = _on_focus_in
            search_input.focusOutEvent = _on_focus_out
            search_box.enterEvent      = _on_enter
            search_box.leaveEvent      = _on_leave
            sb_l.addWidget(search_input, 1)
            sf_layout.addWidget(search_box)
            ov_layout.addWidget(search_frame)
            
            detail_header = QFrame()
            detail_header.setStyleSheet("background: transparent;")
            dh_layout = QVBoxLayout(detail_header)
            dh_layout.setContentsMargins(18, 6, 18, 0)
            dh_layout.setSpacing(0)
            detail_header.setVisible(False)
            
            ov_layout.addWidget(detail_header)

            # Scroll
            scroll = QScrollArea()
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll.setWidgetResizable(True)
            scroll.setViewportMargins(0, 0, 5, 0)
            scroll.setStyleSheet("""
                QScrollArea { border: none; background: transparent; }
                QScrollArea > QWidget > QWidget { background: transparent; }
                QScrollBar:vertical {
                    background: transparent; width: 10px;
                    margin: 4px 5px 4px 0px;
                }
                QScrollBar::handle:vertical {
                    background: #4a9aba; border-radius: 3px; min-height: 24px;
                }
                QScrollBar::handle:vertical:hover { background: #28AEED; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
            """)
            ov_layout.addWidget(scroll)

            stack = QStackedWidget()
            stack.setStyleSheet("background: transparent;")

            # Page 0: Versions list
            older_widget = QWidget()
            older_widget.setStyleSheet("background: transparent;")
            older_widget.setMaximumWidth(694)
            older_layout = QVBoxLayout(older_widget)
            older_layout.setContentsMargins(18, 6, 18, 6)
            older_layout.setSpacing(0)

            all_older_rows = []
            for ver, bullets in older_versions:
                row_frame = QFrame()
                row_frame.setObjectName("olderRow")
                row_frame.setCursor(QCursor(Qt.PointingHandCursor))
                row_frame.setStyleSheet(
                    "#olderRow { background: transparent; border-bottom: 1px solid #0e1c28; }"
                )
                row_frame.setMouseTracking(True)
                row_frame.enterEvent = lambda e, r=row_frame: r.setStyleSheet(
                    "#olderRow { background: rgba(40,174,237,0.04); border-bottom: 1px solid #0e1c28; }"
                )
                row_frame.leaveEvent = lambda e, r=row_frame: r.setStyleSheet(
                    "#olderRow { background: transparent; border-bottom: 1px solid #0e1c28; }"
                )
                row_hl = QHBoxLayout(row_frame)
                row_hl.setContentsMargins(4, 7, 8, 7)
                row_hl.setSpacing(10)

                ver_tag = QLabel(ver)
                ver_tag.setFont(QFont("Cascadia Code", 11, QFont.Bold))
                ver_tag.setStyleSheet("color: #28AEED; background: transparent; border: none;")
                ver_tag.setFixedWidth(55)

                preview = bullets[0] if bullets else "—"
                if len(bullets) > 1:
                    preview += f"  (+{len(bullets)-1})"
                prev_lbl = QLabel(preview)
                prev_lbl.setFont(QFont("Segoe UI", 10))
                prev_lbl.setStyleSheet("color: #3A6070; background: transparent; border: none;")

                arrow_lbl = QLabel("›")
                arrow_lbl.setFont(QFont("Segoe UI", 12))
                arrow_lbl.setStyleSheet("color: #1D3545; background: transparent; border: none;")

                row_hl.addWidget(ver_tag)
                row_hl.addWidget(prev_lbl, 1)
                row_hl.addWidget(arrow_lbl)

                older_layout.addWidget(row_frame)
                search_text = (preview + " " + " ".join(bullets)).lower()
                all_older_rows.append((ver, search_text, row_frame))
                row_frame.mousePressEvent = lambda e, v=ver, b=bullets: show_detail(v, b)

            older_layout.addStretch()
            stack.addWidget(older_widget)   # index 0

            # Page 1: Detail view
            detail_widget = QWidget()
            detail_widget.setStyleSheet("background: transparent;")
            detail_widget.setMaximumWidth(694)
            detail_layout = QVBoxLayout(detail_widget)
            detail_layout.setContentsMargins(18, 0, 0, 0)
            detail_layout.setSpacing(0)
            stack.addWidget(detail_widget)  # index 1

            scroll.setWidget(stack)
            
            # ── show_detail ────────────────────────────────
            def show_detail(ver, bullets):
                # dh_layout leeren
                while dh_layout.count():
                    item = dh_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

                # detail_layout leeren
                while detail_layout.count():
                    item = detail_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

                # ── Fixer Header in dh_layout ──
                back_btn = QPushButton("‹  " + lbl_back)
                back_btn.setFixedHeight(20)
                back_btn.setCursor(QCursor(Qt.PointingHandCursor))
                back_btn.setFont(QFont("Segoe UI", 10))
                back_btn.setStyleSheet("""
                    QPushButton {
                        background: transparent; color: #5A8A9A;
                        border: none; text-align: left; padding: 0;
                    }
                    QPushButton:hover { color: #28AEED; }
                """)
                back_btn.clicked.connect(lambda: (
                    scroll.verticalScrollBar().setValue(0),
                    detail_header.setVisible(False),
                    search_frame.setVisible(True),
                    stack.setCurrentIndex(0),
                    stack.setFixedHeight(older_widget.sizeHint().height()),
                    scroll.updateGeometry()
                ))
                dh_layout.addWidget(back_btn)

                dsep = QFrame()
                dsep.setFixedHeight(1)
                dsep.setStyleSheet("background: #1D3545; border: none; margin: 4px 0;")
                dh_layout.addWidget(dsep)
                dh_layout.addSpacing(8)

                ver_hdr_row = QWidget()
                ver_hdr_row.setFixedHeight(26)
                ver_hdr_row.setStyleSheet("background: transparent;")
                vhr_l = QHBoxLayout(ver_hdr_row)
                vhr_l.setContentsMargins(0, 0, 0, 0)
                vhr_l.setSpacing(8)
                vhr_l.setAlignment(Qt.AlignVCenter)

                vhdr_bar = QFrame()
                vhdr_bar.setFixedSize(2, 20)
                vhdr_bar.setStyleSheet("""
                    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                        stop:0 #1A6A9A, stop:0.5 #28AEED, stop:1 #1A6A9A);
                    border-radius: 1px; border: none;
                """)
                vhr_l.addWidget(vhdr_bar)

                vhdr_lbl = QLabel(ver)
                vhdr_lbl.setFont(QFont("Cascadia Code", 13, QFont.Bold))
                vhdr_lbl.setStyleSheet("color: #28AEED; background: transparent; border: none;")
                vhr_l.addWidget(vhdr_lbl)
                vhr_l.addStretch()
                dh_layout.addWidget(ver_hdr_row)

                dsep1 = QFrame()
                dsep1.setFixedHeight(1)
                dsep1.setStyleSheet("background: #1D3545; border: none; margin: 4px 0;")
                dh_layout.addWidget(dsep1)
                dh_layout.addSpacing(8)

                # ── Nur Card im scrollbaren detail_layout ──
                detail_layout.addWidget(make_entry_card(bullets))
                detail_layout.addStretch()

                search_frame.setVisible(False)
                detail_header.setVisible(True)
                stack.setMaximumHeight(16777215)
                stack.setCurrentIndex(1)



            # ── Toggle logic ───────────────────────────────
            _expanded = [False]

            def expand():
                _expanded[0] = True
                toggle_frame_main.setVisible(False)
                ov_h = dialog.height() - OVERLAY_Y - FOOTER_H
                overlay.setGeometry(1, OVERLAY_Y, 698, ov_h)
                stack.setCurrentIndex(0)
                search_frame.setVisible(True)
                overlay.setVisible(True)
                overlay.raise_()

            def collapse():
                _expanded[0] = False
                overlay.setVisible(False)
                detail_header.setVisible(False)                    
                search_input.clear()
                for _, _, rw in all_older_rows:
                    rw.setVisible(True)
                stack.setCurrentIndex(0)
                toggle_frame_main.setVisible(True)
                latest_scroll.verticalScrollBar().setValue(0)

            toggle_btn_main.clicked.connect(expand)
            toggle_lbl_main.mousePressEvent = lambda e: expand()
            toggle_lbl_main.enterEvent = lambda e: toggle_lbl_main.setStyleSheet(
                "color: #28AEED; background: transparent; border: none;"
            )
            toggle_lbl_main.leaveEvent = lambda e: toggle_lbl_main.setStyleSheet(
                "color: #3A6070; background: transparent; border: none;"
            )
            toggle_btn_ov.clicked.connect(collapse)
            toggle_lbl_ov.mousePressEvent = lambda e: collapse()
            toggle_lbl_ov.enterEvent = lambda e: toggle_lbl_ov.setStyleSheet(
                "color: #28AEED; background: transparent; border: none;"
            )
            toggle_lbl_ov.leaveEvent = lambda e: toggle_lbl_ov.setStyleSheet(
                "color: #3A6070; background: transparent; border: none;"
            )
            def filter_older(text):
                q = text.lower()
                for ver_str, search_str, row_widget in all_older_rows:
                    row_widget.setVisible(not q or q in ver_str.lower() or q in search_str)

            search_input.textChanged.connect(filter_older)

        else:
            main_layout.addStretch()

        # ── Footer ─────────────────────────────────────────
        footer_sep = QFrame()
        footer_sep.setFixedHeight(1)
        footer_sep.setStyleSheet("background: #1D3545; border: none;")
        main_layout.addWidget(footer_sep)

        footer = QFrame()
        footer.setObjectName("footer")
        footer.setFixedHeight(44)
        footer.setStyleSheet("""
            #footer {
                background: transparent; border: none;
                border-bottom-left-radius: 14px;
                border-bottom-right-radius: 14px;
            }
        """)
        ft_layout = QHBoxLayout(footer)
        ft_layout.setContentsMargins(18, 0, 18, 0)

        sig = QLabel('made by  <span style="color:#5A8A9A;">stevo_ko</span>')
        sig.setFont(QFont("Segoe UI", 10))
        sig.setTextFormat(Qt.RichText)
        sig.setStyleSheet("color: #3A6070; background: transparent; border: none;")
        ft_layout.addWidget(sig)
        ft_layout.addStretch()

        close_btn = QPushButton("Schließen" if "(DE)" in lang_suffix else "Close")
        close_btn.setFixedSize(110, 28)
        close_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        close_btn.setStyleSheet("""
            QPushButton {
                background: #0E2030; color: #28AEED;
                border: 1px solid #28AEED; border-radius: 7px; padding: 4px 14px;
            }
            QPushButton:hover { background: #1A3D52; color: #00FFFF; }
            QPushButton:pressed { background: #0A1E2C; }
        """)
        close_btn.clicked.connect(dialog.close)
        ft_layout.addWidget(close_btn)

        main_layout.addWidget(footer)
        dialog.show()
        def _adjust_height():
            toggle_h = toggle_frame_main.sizeHint().height() if older_versions else 0
            frame_h  = 26 + 1 + 10 + (len(latest_bullets) * 34 + 6) + 14
            max_h    = dialog.height() - 38 - 1 - 45 - 1 - toggle_h - 10
            latest_frame.setFixedHeight(min(frame_h, max_h))

        QTimer.singleShot(0, _adjust_height)

    except Exception as e:
        print(f"[changelog] Fehler: {e}")
        import traceback
        traceback.print_exc()
        
        
def _get_version_content(raw: str, lang_suffix: str = None) -> str:
    lines    = raw.splitlines()
    result   = []
    in_block = False

    for line in lines:
        if line.startswith("## "):
            matches_lang = (lang_suffix is None) or (lang_suffix in line)

            if in_block:
                break

            if matches_lang:
                in_block = True
                # Lang Suffix aus dem Header entfernen
                clean_line = line.replace(f" {lang_suffix}", "").replace(lang_suffix, "").strip()
                result.append(clean_line)
            continue

        if in_block:
            result.append(line)

    return "\n".join(result)
        
def _show_changelog():
    changelog_path = os.path.join(programm_ordner, "Matchfixes_Changelog.md")
    current_version = f"v{rules.get('version', '?')}" if rules else "?"
    lang_suffix = "(DE)" if language == 1 else "(EN)"
 
    content = None
    if os.path.exists(changelog_path):
        with open(changelog_path, "r", encoding="utf-8") as f:
            content = f.read()
 
    # Fallback: dummy content wenn Datei fehlt oder leer
    if not content or not content.strip():
        dummy = CHANGELOG_DUMMY \
            .replace("## (DE)", f"## {current_version} (DE)") \
            .replace("## (EN)", f"## {current_version} (EN)")
        content = dummy
 
    # Vollständigen Inhalt + aktuelle Version übergeben
    # Das Fenster filtert selbst nach current_version und baut die älteren Versionen
    _changelog_signal.open_changelog.emit(content, current_version, lang_suffix)

def _init_changelog_signal():
    _changelog_signal.open_changelog.connect(_open_changelog_window, Qt.QueuedConnection)
    if console is not None:
        _gui_signals.show_console_window.connect(console.show)
        _gui_signals.hide_console_window.connect(console.hide)

ico_path = get_resource_path("icon.ico")
png_path = get_resource_path("app.png")

if not os.path.exists(png_path):
    PILImage.open(ico_path).save(png_path)

MATCH_URL      = "https://github.com/stevo-ko/Category_Switcher/raw/refs/heads/main/matchfixes.switcher"
MATCH_CHANGELOG_URL = "https://github.com/stevo-ko/Category_Switcher/raw/refs/heads/main/Matchfixes_Changelog.md"
TOAST_APP_ID   = "stevo_ko.CategorySwitcher"
TOAST_APP_NAME = "Category Switcher"
TOAST_FLAG     = os.path.join(programm_ordner, "_internal", ".toast_registered")
matchfix_update_toast_notification = bool(config["options"]["matchfix_update_toast_notification"])
_toast_build_params = {}
verbose = False
 
def _get_text(de, en):
    return de if language == 1 else en

def _vlog(msg: str) -> None:
    if not verbose:
        return
    import datetime
    with open("crash_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now().strftime('%H:%M:%S.%f')}] {msg}\n")

def _toast_cleanup() -> None:
    _vlog("_toast_cleanup gestartet")
    if os.path.exists(TOAST_FLAG):
        try:
            registered = [i[0] for i in Toast.list_app_ids()]
            _vlog(f"Registrierte App IDs: {registered}")
            if TOAST_APP_ID in registered:
                Toast.unregister_app_id(TOAST_APP_ID)
                _vlog("unregister_app_id OK")
        except Exception as e:
            _vlog(f"unregister FEHLER: {e}")
        try:
            os.remove(TOAST_FLAG)
            _vlog("TOAST_FLAG entfernt")
        except Exception as e:
            _vlog(f"TOAST_FLAG entfernen FEHLER: {e}")
    else:
        _vlog("TOAST_FLAG existiert nicht – kein Cleanup nötig")

def _toast_init() -> None:
    _vlog("=== _toast_init gestartet ===")
    _toast_cleanup()
    time.sleep(0.5)
    try:
        os.makedirs(os.path.join(programm_ordner, "_internal"), exist_ok=True)
        Toast.register_app_id(TOAST_APP_ID, TOAST_APP_NAME, icon_uri=get_resource_path("icon.ico"))
        open(TOAST_FLAG, "w").close()
        _vlog("register_app_id OK")
    except Exception as e:
        _vlog(f"register_app_id FEHLER: {e}")

def _build_result_toast(de_status: str, en_status: str, counts: dict, changed: bool = False, first_download: bool = False, show_popup: bool = True) -> Toast:
    t = Toast(app_id=TOAST_APP_ID, duration=ToastDuration.LONG)
    if not show_popup:
        t.show_popup = False
    image = False
    if image:
        elements = [
            Image(
                source=f"ms-appx:///{get_resource_path('app.png').replace(os.sep, '/')}",
                placement=ToastImagePlacement.LOGO,
                is_circle=True,
            ),
            Text(de_status if language == 1 else en_status, style=ToastTextStyle.TITLE, align=ToastTextAlign.CENTER),
        ]
    else:
        elements = [
            Text(de_status if language == 1 else en_status, style=ToastTextStyle.TITLE, align=ToastTextAlign.CENTER),
        ]

    if changed:
        elements.append([
            [
                Text(_get_text("Alte Version    \u279c", "Old Version    \u279c"), style=ToastTextStyle.SUBTITLESUBTLE, align=ToastTextAlign.RIGHT),
                Text(f"v{counts.get('old_version', '?')}", style=ToastTextStyle.SUBTITLESUBTLE, align=ToastTextAlign.CENTER),
            ],
            [
                Text(_get_text("Neue Version", "New Version"), style=ToastTextStyle.SUBTITLE, align=ToastTextAlign.CENTER),
                Text(f"v{counts['version']}", style=ToastTextStyle.SUBTITLE, align=ToastTextAlign.CENTER),
            ],
        ])
        elements.append([
            [
                Text("Mappings", style=ToastTextStyle.BASESUBTLE, align=ToastTextAlign.CENTER),
                Text(str(counts['mappings']), style=ToastTextStyle.SUBTITLE, align=ToastTextAlign.CENTER),
            ],
            [
                Text("Exact", style=ToastTextStyle.BASESUBTLE, align=ToastTextAlign.CENTER),
                Text(str(counts['exact']), style=ToastTextStyle.SUBTITLE, align=ToastTextAlign.CENTER),
            ],
        ])
        elements.append([
            [
                Text(_get_text("Ausgeschlossen", "Excluded"), style=ToastTextStyle.BASESUBTLE, align=ToastTextAlign.CENTER),
                Text(str(counts['names']), style=ToastTextStyle.SUBTITLE, align=ToastTextAlign.CENTER),
            ],
            [
                Text("EXEs", style=ToastTextStyle.BASESUBTLE, align=ToastTextAlign.CENTER),
                Text(str(counts['exact_exe']), style=ToastTextStyle.SUBTITLE, align=ToastTextAlign.CENTER),
            ],
        ])
        elements.append(
            Button(
                _get_text("Changelog", "Changelog"),
                arguments="changelog",
            )
        )
    elif first_download:
        elements.append([
            [
                Text(_get_text("Version", "Version"), style=ToastTextStyle.SUBTITLE, align=ToastTextAlign.CENTER),
                Text(f"v{counts['version']}", style=ToastTextStyle.SUBTITLE, align=ToastTextAlign.CENTER),
            ],
        ])
        elements.append([
            [
                Text("Mappings", style=ToastTextStyle.BASESUBTLE, align=ToastTextAlign.CENTER),
                Text(str(counts['mappings']), style=ToastTextStyle.SUBTITLE, align=ToastTextAlign.CENTER),
            ],
            [
                Text("Exact", style=ToastTextStyle.BASESUBTLE, align=ToastTextAlign.CENTER),
                Text(str(counts['exact']), style=ToastTextStyle.SUBTITLE, align=ToastTextAlign.CENTER),
            ],
        ])
        elements.append([
            [
                Text(_get_text("Ausgeschlossen", "Excluded"), style=ToastTextStyle.BASESUBTLE, align=ToastTextAlign.CENTER),
                Text(str(counts['names']), style=ToastTextStyle.SUBTITLE, align=ToastTextAlign.CENTER),
            ],
            [
                Text("EXEs", style=ToastTextStyle.BASESUBTLE, align=ToastTextAlign.CENTER),
                Text(str(counts['exact_exe']), style=ToastTextStyle.SUBTITLE, align=ToastTextAlign.CENTER),
            ],
        ])
        elements.append(
            Button(
                _get_text("Changelog", "Changelog"),
                arguments="changelog",
            )
        )
    else:
        elements.append([
            [
                Text(_get_text("Version", "Version"), style=ToastTextStyle.SUBTITLE, align=ToastTextAlign.CENTER),
                Text(f"v{counts['version']}", style=ToastTextStyle.SUBTITLE, align=ToastTextAlign.CENTER),
            ],
        ])

    t.elements = elements
    _toast_build_params[id(t)] = (de_status, en_status, counts, changed, first_download)
    return t

def _load_rules_with_toast(toast_obj=None):
    _vlog(f"_load_rules_with_toast gestartet (toast_obj={'vorhanden' if toast_obj else 'None'})")
    key, iv    = get_key_and_iv(MATCH_ENC_KEY)
    local_path = os.path.join(programm_ordner, "matchfixes.switcher")
    local_changelog_path = os.path.join(programm_ordner, "Matchfixes_Changelog.md")

    def _upd(de_status, en_status, progress, de_detail, en_detail, percent):
        if toast_obj:
            _vlog(f"Toast update: {en_status} ({percent})")
            try:
                toast_obj.update({
                    "status":   de_status if language == 1 else en_status,
                    "progress": progress,
                    "detail":   de_detail if language == 1 else en_detail,
                    "percent":  percent,
                })
                _vlog("Toast update OK")
            except Exception as e:
                _vlog(f"Toast update fehlgeschlagen: {e}")

    def decrypt(raw):
        verified  = verify_and_strip_hmac(raw, key)
        decrypted = encrypt_decrypt(verified, key, iv)
        return json.loads(decrypted)

    def encrypt_and_save(data):
        raw       = json.dumps(data, ensure_ascii=False).encode()
        encrypted = encrypt_decrypt(raw, key, iv)
        secured   = add_hmac(encrypted, key)
        with open(local_path, "wb") as f:
            f.write(secured)
            
    def parse_version(v: str) -> float:
        try:   return float(v)
        except: return 0.0
        
    def merge(local, online):
        if local is None:
            return online, True
        
        local_v  = parse_version(local.get("version",  "0.00"))
        online_v = parse_version(online.get("version", "0.00"))

        if local_v > online_v:
            # Lokal neuer → unverändert behalten
            _vlog(f"Lokale Version ({local_v}) > Online ({online_v}) → behalte lokal")
            return local, False
        
        merged  = {k: online[k] for k in online}
        changed = merged != local
        return merged, changed

    def count(r):
        return {
            "version":   r.get("version", "?"),
            "mappings":  len(r.get("game_name_mappings", [])),
            "exact":     len(r.get("game_name_exact", [])),
            "names":     len(r.get("excluded_exe_names_in_code", [])),
            "exact_exe": len(r.get("excluded_exe_exact_in_code", [])),
        }

    _upd("🔍 Prüfe Update…", "🔍 Checking for update…",
         0.1,
         "Verbinde mit Server…", "Connecting to server…", "10%")

    online_raw = None
    try:
        response = requests.get(MATCH_URL, timeout=5)
        if response.status_code == 200:
            online_raw = response.content
            _vlog(f"Online Datei geladen ({len(online_raw)} bytes)")
        else:
            _vlog(f"Online Datei Statuscode: {response.status_code}")
    except Exception as e:
        _vlog(f"Online Datei Fehler: {e}")

    if online_raw is not None:
        _upd("⬇️ Update herunterladen…", "⬇️ Downloading update…",
             0.4,
             "Herunterladen…", "Downloading…", "40%")
        time.sleep(0.3)
    else:
        _upd("❌ Datei Online nicht gefunden", "❌ File online not found",
             0.4,
             "Datei online nicht gefunden", "File online not found", "40%")
        time.sleep(0.3)

    local_raw = None
    first_download = False

    if os.path.exists(local_path):
        with open(local_path, "rb") as f:
            local_raw = f.read()
        _vlog(f"Lokale Datei geladen ({len(local_raw)} bytes)")
    elif online_raw:
        try:
            with open(local_path, "wb") as f:
                f.write(online_raw)
            local_raw = online_raw
            first_download = True
            _vlog("Erster Download – lokal gespeichert")
        except Exception as e:
            _vlog(f"Lokales Speichern fehlgeschlagen: {e}")

    online_rules = local_rules = None

    if online_raw:
        try:
            online_rules = decrypt(online_raw)
            _vlog("Online Rules entschlüsselt OK")
        except Exception as e:
            _vlog(f"Online Rules entschlüsseln FEHLER: {e}")

    if local_raw:
        try:
            local_rules = decrypt(local_raw)
            _vlog("Lokale Rules entschlüsselt OK")
        except Exception as e:
            _vlog(f"Lokale Rules entschlüsseln FEHLER: {e}")

    changelog_raw = None
    try:
        response = requests.get(MATCH_CHANGELOG_URL, timeout=5)
        if response.status_code == 200:
            changelog_raw = response.content
            _vlog(f"Changelog geladen ({len(changelog_raw)} bytes)")
        else:
            _vlog(f"Changelog Statuscode: {response.status_code}")
    except Exception as e:
        _vlog(f"Changelog Fehler: {e}")

    if changelog_raw is not None:
        try:
            with open(local_changelog_path, "wb") as f:
                f.write(changelog_raw)
            _vlog("Changelog lokal gespeichert")
        except Exception as e:
            _vlog(f"Changelog speichern FEHLER: {e}")
        _upd("⬇️ Lade Changelog…", "⬇️ Loading changelog…",
             0.7,
             "Verarbeite Daten…", "Processing data…", "70%")
        time.sleep(0.3)
    else:
        if os.path.exists(local_changelog_path):
            with open(local_changelog_path, "rb") as f:
                changelog_raw = f.read()
            _vlog("Lokalen Changelog verwendet")
            _upd("⚠️ Changelog online nicht gefunden", "⚠️ Changelog online not found",
                 0.7,
                 "Weiter…", "Continuing…", "70%")
        else:
            _vlog("Kein Changelog verfügbar")
            _upd("❌ Changelog nicht verfügbar", "❌ Changelog not available",
                 0.7,
                 "Kein Changelog verfügbar", "No changelog available", "70%")
        time.sleep(0.3)

    if online_rules:
        if first_download:
            counts = count(online_rules)
            _vlog(f"Erster Download abgeschlossen: {counts}")
            _upd("⬇️ Lade Match Liste…", "⬇️ Loading match list…",
                 0.9, "Abgeschlossen…", "Done…", "90%")
            return online_rules, True, _build_result_toast(
                "✅ Match Liste heruntergeladen",
                "✅ Match list downloaded",
                counts,
                changed=False,
                first_download=True
            ), True

        merged, changed = merge(local_rules, online_rules)
        counts = count(merged)
        old_version = local_rules.get("version", "?") if local_rules else "?"
        counts["old_version"] = old_version
        _vlog(f"Merge abgeschlossen: changed={changed}, version={counts['version']}")

        if changed:
            try:
                encrypt_and_save(merged)
                _vlog("Merged Rules gespeichert")
                if language == 1:
                    logging.info("✅ matchfixes.switcher aktualisiert")
                else:
                    logging.info("✅ matchfixes.switcher updated")
            except Exception as e:
                _vlog(f"Merged Rules speichern FEHLER: {e}")
                logging.warning(e)

        _upd("⬇️ Lade Matchfix Liste…", "⬇️ Loading matchfix list…",
             0.9,
             "Abgeschlossen…", "Done…", "90%")

        return merged, changed, _build_result_toast(
            "✅ Matchfix Liste aktualisiert" if changed else "✅ Bereits aktuell",
            "✅ Matchfix list updated"       if changed else "✅ Already up to date",
            counts,
            changed=changed
        ), False

    if local_rules:
        counts = count(local_rules)
        counts["old_version"] = "?"
        _vlog(f"Nur lokale Rules verfügbar: {counts}")
        _upd("⬇️ Lade Match Liste…", "⬇️ Loading match list…",
             0.9,
             "Abgeschlossen…", "Done…", "90%")
        return local_rules, False, _build_result_toast(
            "⚠️ Nur lokal verfügbare Matchfixes",
            "⚠️ Only local available matchfixes",
            counts
        ), False

    _vlog("Keine Rules verfügbar – weder online noch lokal")
    _upd("❌ Laden fehlgeschlagen", "❌ Load failed",
         1.0,
         "Keine Daten verfügbar", "No data available", "100%")

    fail_toast = Toast(app_id=TOAST_APP_ID, duration=ToastDuration.LONG)
    fail_toast.elements = [
        Text(_get_text("❌ Matchfix Liste nicht verfügbar", "❌ Matchfix list unavailable"), style=ToastTextStyle.TITLE),
        Text(_get_text("Keine Verbindung und keine lokalen Daten.", "No connection and no local data."))
    ]
    return None, False, fail_toast, False

async def _run_update_notification():
    global _active_toast, rules, _toast_build_params, matchfix_version

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(
        lambda loop, ctx: None
        if isinstance(ctx.get("exception"), (asyncio.InvalidStateError, RuntimeError))
        else loop.default_exception_handler(ctx)
    )

    _vlog("=== _run_update_notification gestartet ===")
    _toast_init()

    if not matchfix_update_toast_notification:
        _vlog("matchfix_update_toast_notification = False, lade ohne Toast")
        rules_result, _, _, _ = await asyncio.get_event_loop().run_in_executor(
            None, _load_rules_with_toast, None
        )
        rules = rules_result
        matchfix_version = rules_result.get("version") if rules_result else None
        _vlog(f"Rules geladen: {rules_result is not None}")
        _notification_ready.set()
        return rules_result

    _vlog("Toast wird erstellt...")
    toast = Toast(app_id=TOAST_APP_ID, toast_id="update-toast")
    _active_toast = toast
    toast.elements = [
        Text("{status}"),
        Progress(value="{progress}", status="{detail}", display_value="{percent}"),
    ]

    async def _show_and_signal():
        _vlog("_show_and_signal...")
        
        _vlog("sleep ende, starte toast.show()")
        try:
            await toast.show({
                "status":   _get_text("🔍 Prüfe Update…",   "🔍 Checking for update…"),
                "progress": 0.0,
                "detail":   _get_text("Starte…",             "Starting…"),
                "percent":  "0%",
            })
            _vlog("toast.show() beendet")
        except RuntimeError as e:
            _vlog(f"Toast fehlgeschlagen: {e}")
            if "-2143420140" in str(e):
                _vlog("Benachrichtigungen blockiert – Toast wird übersprungen")
                if matchfix_update_toast_notification:
                    if language == 1:
                        print("⚠️ Benachrichtigungen sind ausgeschaltet oder Bitte nicht stören ist aktiviert. Toast Benachrichtigungen werden nicht angezeigt.")
                    if language == 0:
                        print("⚠️ Notifications are disabled or Do Not Disturb is active. Toast notifications will not be displayed.")
            else:
                _vlog(f"Unbekannter Toast Fehler: {e}")
        _vlog("toast.show() beendet")

    show_task = asyncio.create_task(_show_and_signal())
    _vlog("show_task erstellt, warte 1s...")
    await asyncio.sleep(2)
    _vlog("Sleep fertig, starte Executor...")

    try:
        rules_result, was_changed, result_toast, first_download = await asyncio.get_event_loop().run_in_executor(
            None, _load_rules_with_toast, toast
        )
        _vlog(f"Executor fertig: rules={rules_result is not None}, changed={was_changed}, first={first_download}")
    except Exception as e:
        import traceback
        _vlog(f"Executor FEHLER:\n{traceback.format_exc()}")
        rules_result, was_changed, result_toast, first_download = None, False, None, False

    rules = rules_result
    matchfix_version = rules_result.get("version") if rules_result else None

    if matchfix_update_toast_notification:
        await asyncio.sleep(1.0)
        toast.hide()
        show_task.cancel()
        _active_toast = None
        _vlog("Progress Toast versteckt")

        if result_toast:
            _notification_ready.set()
            if was_changed or first_download:
                _vlog("Zeige Result Toast (changed/first_download)")
                _dismissed = asyncio.Event()

                def _on_toast_result(result: ToastResult):
                    _dismissed.set()
                    if result.arguments == "changelog":
                        _show_changelog()

                result_toast.on_result(_on_toast_result)
                show_result = asyncio.create_task(result_toast.show())

                for _ in range(100):
                    if _dismissed.is_set():
                        break
                    await asyncio.sleep(0.1)

                result_toast.hide()
                _active_toast = None
                params = _toast_build_params.get(id(result_toast))
                if params:
                    silent = _build_result_toast(*params, show_popup=False)
                    _active_toast = silent
                    _vlog("Silent Toast wird gestartet")

                    @silent.on_result
                    def _silent_result(result: ToastResult):
                        if result is not None and result.arguments == "changelog":
                            _show_changelog()

                    _silent_task = asyncio.create_task(silent.show())

            elif rules_result is None:
                _vlog("Zeige Fehler Toast")
                show_result = asyncio.create_task(result_toast.show())
                await asyncio.sleep(10.0)
                result_toast.hide()

                silent = Toast(app_id=TOAST_APP_ID, show_popup=False)
                silent.elements = result_toast.elements
                _active_toast = silent
                _silent_task = asyncio.create_task(silent.show())

            else:
                _vlog("Zeige 'bereits aktuell' Toast")
                show_result = asyncio.create_task(result_toast.show())
                _active_toast = result_toast
                await asyncio.sleep(10.0)
                result_toast.hide()
                _active_toast = None

                if rules_result is None:
                    silent = Toast(app_id=TOAST_APP_ID, show_popup=False)
                    silent.elements = result_toast.elements
                    _active_toast = silent
                    _silent_task = asyncio.create_task(silent.show())

    _vlog("=== _run_update_notification beendet ===")
    return rules_result
# Logging-Queue
log_queue = queue.Queue()
_output_buffer = []

# PyQt für GUI/Konsolen Window
# PyQt GUI for console window
class ConsoleRedirector:
    def __init__(self, queue):
        self.queue = queue

    def write(self, message):
        
        """Leitet die Nachricht an die Queue weiter"""
        """Sends print to queue"""
        if message.strip():
            if sys.__stdout__ is not None:  # ← nur Guard, sonst alles gleich
                sys.__stdout__.write(message + "\n")
            if gui:
                self.queue.put(message)
            else:
                _output_buffer.append(message)
            

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
    def closeEvent(self, event):
        QApplication.instance().quit()
            
if show_console:
    
    # Umleitung der Standardausgabe auf die Queue
    # Send standartoutput to queue
    sys.stdout = ConsoleRedirector(log_queue)
    sys.stderr = ConsoleRedirector(log_queue)

  

restarted = "--restarted" in sys.argv
gui = False
console = None
   
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

    merged_config = merge_config(config, extracted_config)
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

# double_instance_thread = threading.Thread(target=monitor_instances, daemon=True)
# double_instance_thread.start()


def terminate_current_instance():
    # Hole den PID der aktuellen Instanz (dieses Skript)
    current_pid = os.getpid()
    try:
        current_proc = psutil.Process(current_pid)
        current_proc.terminate()  # Beendet den aktuellen Prozess
        print(f"Die aktuelle Instanz (PID {current_pid}) wurde beendet.")
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        print("Fehler beim Beenden der aktuellen Instanz.")


MATCH_ENC_KEY = ""


def get_key_and_iv(match_enc_key):
    key = hashlib.sha256(match_enc_key.encode('utf-8')).digest()
    iv  = hashlib.md5(match_enc_key.encode('utf-8')).digest()
    return key, iv
 
def encrypt_decrypt(data, key, iv):
    result     = bytearray(len(data))
    block_size = 64
    for i in range(0, len(data), block_size):
        counter   = struct.pack('>Q', i // block_size)
        keystream = hashlib.sha256(key + iv + counter).digest() + \
                    hashlib.sha256(key + iv + counter + b'\x01').digest()
        block = data[i:i + block_size]
        for j, byte in enumerate(block):
            result[i + j] = byte ^ keystream[j]
    return bytes(result)
 
def add_hmac(data, key):
    import hmac
    mac = hmac.new(key, data, hashlib.sha256).digest()
    return mac + data
 
def verify_and_strip_hmac(data, key):
    import hmac
    mac      = data[:32]
    content  = data[32:]
    expected = hmac.new(key, content, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expected):
        raise ValueError("HMAC verification failed - data tampered!")
    return content   
 

excluded_exe_patterns = []
excluded_exe_names = []
excluded_exe_exact = []
game_name_mappings = []
game_name_exact = []
latest_game_event = None
game_started_event = threading.Event()
Playnite_Game_Stopped = None
observer = None
watcher_started = False
waiting_for_game = False
game_set = False
Playnite_Game_Retry = None
Playnite_exit = None
playnite_enabled = None
game_stopped = None
program_stopped = None
playnite_running = None

_last_check = 0
_last_result = True

# Pfad zur JSON
##filepath = r"E:\Playnite portable\RunningGame.json"

filepath = None

class JsonHandler(FileSystemEventHandler):
    last_run = 0

    def on_modified(self, event):
        global latest_game_event, Playnite_Game_Stopped

        # Nur auf genau die RunningGame.json reagieren
        if os.path.normcase(event.src_path) != os.path.normcase(filepath):
            return
        
        try:
            with io.open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            latest_game_event = data

            if data.get("Event") == "GameStarted":
                game_started_event.set()

            if data.get("Event") == "GameStopped":
                game_started_event.clear()
                Playnite_Game_Stopped = True

        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"Fehler beim Lesen der JSON: {e}")



# ----------------------------
# Watchdog Start / Stop
# ----------------------------
def start_watcher():
    global observer
    if observer is not None and observer.is_alive():
        ##print("Watcher läuft bereits.")
        return

    observer = Observer()
    #print(f"Observer-Typ: {type(observer).__name__}")
    event_handler = JsonHandler()
    directory = os.path.dirname(filepath)
    observer.schedule(event_handler, path=directory, recursive=False)
    observer.start()
    ##print("Watcher gestartet.")

def stop_watcher():
    global observer
    if observer is None:
        return
    observer.stop()
    observer.join()
    observer = None
    ##print("Watcher gestoppt.")


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
previous_game_folder = None
prev_game_set = False
first_save = False
game_folder = "Nothing"
found_folder = None
alternatives_tried = False
alternatives_tried_kick = False
delay_programming = 0
delay_general = 0
delay_playnite = 0
message = False
server = None
kick_failed = False
default_category = None
default_twitch_category = None
default_kick_category = None
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
                    "nmake.exe","gcc.exe","g++.exe","cmake.exe","ninja.exe","node.exe",
                    "npm.exe","dotnet.exe","java.exe","javac.exe","psql.exe","mysql.exe","dbeaver.exe","git.exe",
                    "tortoisegitproc.exe","vmware.exe","virtualbox.exe","qemu-system-x86_64.exe","adb.exe","docker.exe",
                    "dottrace.exe","dotmemory.exe","perfview.exe","choco.exe","scoop.exe","winget.exe","postman.exe",
                    "curl.exe","wget.exe","perfwatson2.exe","ServiceHub.IntellicodeModelService.exe"
                    ]
known_art_exe_names = [
    # Adobe Creative Cloud
    "Photoshop.exe", "Illustrator.exe", "InDesign.exe", "Adobe Premiere Pro.exe",
    "AfterFX.exe", "Adobe Animate.exe", "Adobe Fresco.exe", "Adobe Substance 3D Painter.exe",
    "Adobe Substance 3D Designer.exe", "Adobe Substance 3D Sampler.exe", "Adobe Substance 3D Stager.exe",
    "Lightroom.exe", "AfterEffects.exe",

    # 2D Zeichenprogramme / Illustration
    "CLIPStudioPaint.exe", "krita.exe", "gimp-2.10.exe", "gimp.exe",
    "Painter.exe", "sai.exe", "sai2.exe", "MediBangPaintPro.exe",
    "PaintStorm.exe", "Rebelle 6.exe", "Rebelle 5.exe", "ArtRage 6.exe", "ArtRage.exe",
    "inkscape.exe", "CorelDrw.exe", "Affinity Photo.exe", "Affinity Designer.exe",
    "Affinity Publisher.exe", "Photo.exe", "Designer.exe", "SketchBook.exe",

    # Animation
    "HarmonyPremium.exe", "Harmony Premium.exe", "OpenToonz.exe",
    "TVPaint Animation 11 64bits.exe", "TVPaint Animation 12 64bits.exe",
    "Aseprite.exe", "aseprite.exe",

    # 3D / Sculpting / Modeling
    "ZBrush.exe", "maya.exe", "3dsmax.exe", "Cinema 4D.exe", "houdini.exe",
    "3DCoat.exe", "3DCoatTextura.exe", "SubstancePainter.exe", "SubstanceDesigner.exe",
    "MarvelousDesigner.exe", "CharacterCreator.exe", "iClone.exe",
    "ZBrush64.exe", "Wrap4Blender.exe",

    # Sonstige Kreativ-Tools
    "procreate.exe",
]
   
last_modified = None  
save_games_to_file = True
unique_id = None
seen_processes = None
printed_closed = False
report_sended = False
window_title = None
wiki_title = None
BACKEND_URL = "https://backend.stevo-ko.de/"
backend_token = ""
username = None
switcher_version = None
matchfix_version = None
operating_system = None
windowsapps_map = {}       # {exe_name.lower(): display_name}




def main_logic():
    
    global token, CLIENT_ID, token_valid, category_set_already, language, previous_saved_games, previous_game_folder, prev_game_set, first_save, game_folder, alternatives_tried, alternatives_tried_kick, config_path, last_modified, message, with_console, known_exe_names, settingspath, update_from_version_below_2, printed_closed, found_folder

    ##art exe names
    global known_art_exe_names
    ##gui
    global console
    
    ##toast notification
    global matchfix_update_toast_notification
    
    ## delays
    global delay_programming, delay_general, delay_playnite, game_stopped, program_stopped
    
    ## kick globals
    global kick_token, kick_client_id, kick_client_secret, kick_enabled, kick_missing, kick_failed, displayed_no_category_kick

    ## Playnite globals
    global _last_check, _last_result, Playnite_exit, Playnite_Game_Retry, playnite_enabled, save_games_to_file, observer, filepath, game_set, Playnite_Game_Stopped, watcher_started, waiting_for_game, game_started_event, latest_game_event, playnite_running 

    ## Hardcoded Matches
    global rules, excluded_exe_patterns, excluded_exe_names, excluded_exe_exact, game_name_mappings, game_name_exact 
    
    ## Default categorys when none is found
    global default_category, default_twitch_category, default_kick_category
    
    ## Variables for report system
    global report_sended, window_title, wiki_title, BACKEND_URL, backend_token, username, switcher_version, matchfix_version, avatar_url, operating_system, version_path, backend_api
    
    ## Dict for windowsapps
    global windowsapps_map
    
    
##    print(config_path)
##    print(last_modified)
    ctypes.windll.kernel32.SetConsoleTitleW("Category Switcher")
    sys.argv[0] = ("Category Switcher")
##    print(settingspath)
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
    #backend_token = get_key_value(config["backend"], "OAuth_token")
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
    delay_playnite = int(config["options"]["delay_playnite"])*1000
    kick_enabled = bool(config["options"]["kick_enabled"])
    playnite_enabled = bool(config["options"]["playnite_enabled"])
    matchfix_update_toast_notification = bool(config["options"]["matchfix_update_toast_notification"])
    backend_api = bool(config["options"]["backend_api"])
    
    # Kategorie wenn keine gefunden wird
    # Category when None is found
    default_category = config["default_category"]["enabled"]
    default_twitch_category = config["default_category"]["twitch_category"]
    default_kick_category = config["default_category"]["kick_category"]
    
    last_modified = os.path.getmtime(config_path)
    
    def load_config_live():
        global CLIENT_ID
        global token
        global kick_token
        global kick_enabled
        global playnite_enabled
        global language
        global delay_programming
        global delay_general
        global delay_playnite
        global message
        global matchfix_update_toast_notification
        global default_category
        global default_twitch_category
        global default_kick_category
        global backend_api
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
        #backend_token = get_key_value(config["backend"], "OAuth_token")
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
        playnite_enabled = bool(config["options"]["playnite_enabled"])
        setting_language = config["options"]["language"]
        matchfix_update_toast_notification = bool(config["options"]["matchfix_update_toast_notification"])
        backend_api = bool(config["options"]["backend_api"])

        default_category = config["default_category"]["enabled"]
        default_twitch_category = config["default_category"]["twitch_category"]
        default_kick_category = config["default_category"]["kick_category"]


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
            print("✅ Config.json wurde verändert. Erfolgreich neu geladen.")
        if language == 0:
            print("✅ Config.json has changed. Succesful reloaded")

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
    
    def get_windowsapps_map() -> dict:
        """
        Gibt ein Dict {exe_name.lower(): display_name} aller installierten
        Windows Store Apps zurück.
        """
        APPX_ROOT = r"SOFTWARE\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\Repository\Packages"
        
        try:
            result = subprocess.run(
                ['powershell', '-NoProfile', '-Command',
                'Get-AppxPackage | ForEach-Object { $_.PackageFullName }'],
                capture_output=True, text=True, timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            valid_full_names = set()
            if result.returncode == 0 and result.stdout.strip():
                valid_full_names = {line.strip() for line in result.stdout.splitlines() if line.strip()}
        except Exception:
            valid_full_names = set()

        windowsapps_mapping = {}

        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, APPX_ROOT) as root:
                i = 0
                while True:
                    try:
                        pkg_key = winreg.EnumKey(root, i)
                        i += 1
                    except OSError:
                        break

                    if valid_full_names and pkg_key not in valid_full_names:
                        continue

                    try:
                        with winreg.OpenKey(root, pkg_key) as pkg:
                            try:
                                display_name = winreg.QueryValueEx(pkg, "DisplayName")[0]
                            except OSError:
                                display_name = ""

                            try:
                                install_loc = winreg.QueryValueEx(pkg, "PackageRootFolder")[0]
                            except OSError:
                                install_loc = ""

                            if not display_name or display_name.startswith("@{") or display_name.startswith("ms-resource"):
                                display_name = pkg_key.split("_")[0]

                            if install_loc and "\\SystemApps\\" in install_loc:
                                continue

                            if not install_loc or not os.path.isdir(install_loc):
                                continue

                            try:
                                for f in os.listdir(install_loc):
                                    if f.lower().endswith('.exe'):
                                        windowsapps_mapping[f.lower()] = display_name
                            except (PermissionError, FileNotFoundError):
                                pass

                    except OSError:
                        pass

        except OSError as e:
            print(f"⚠️  Registry-Fehler: {e}")

        return windowsapps_mapping
        
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
            or "microsoft visual studio" in exe_path_lower
        )

    def is_known_art_program_path(exe_path):
        exe_path_lower = exe_path.lower()
        return any(exe.lower() in exe_path_lower for exe in known_art_exe_names)
    
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
    
    

    def is_playnite_running():
        if not playnite_enabled:
            return False
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name']
                if not name:
                    continue
                name_lower = name.lower()
                if name_lower in ('playnite.desktopapp.exe', 'playnite.fullscreenapp.exe'):
                    
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
            ##print(response.text)
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
                return True
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
                ##print(response.text)

        except requests.exceptions.ConnectionError as e:
            
            if not show_console:
                if not gui:
                    _gui_signals.show_console_window.emit()                  
            
            if language == 1:
                print("❌ Verbindung zu Streamer.bot konnte nicht hergestellt werden. Stelle sicher das der HTTP Server gestartet ist")
            if language == 0:
                print("❌ Could not connect to Streamer.bot. Make sure http server is running!")
                
            if not show_console:
                start_logging()
                logging.error(f"Connection error: {e}")
            return 
            
        except requests.exceptions.InvalidURL as e:
            
            if not show_console:
                if not gui:
                    _gui_signals.show_console_window.emit()   

            if language == 1:
                print("❌ Streamer.bot URL oder Port leer oder nicht gültig.")
            if language == 0:
                print("❌ Streamer.bot URL or Port empty or not valid.")
        except requests.exceptions.RequestException as e:
            
            if not show_console:
                if not gui:
                    _gui_signals.show_console_window.emit()   

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
                    _gui_signals.show_console_window.emit()                  
            
            if language == 1:
                print("❌ Verbindung zu Streamer.bot konnte nicht hergestellt werden. Stelle sicher das der HTTP Server gestartet ist")
            if language == 0:
                print("❌ Could not connect to Streamer.bot. Make sure http server is running!")
            if not show_console:
                start_logging()
                logging.error(f"Connection error: {e}")
            return None
        except requests.exceptions.InvalidURL as e:
            
            if not show_console:
                if not gui:
                    _gui_signals.show_console_window.emit()   

            if language == 1:
                print("❌ Streamer.bot URL oder Port leer oder nicht gültig.")
            if language == 0:
                print("❌ Streamer.bot URL or Port empty or not valid.")
            return None
        except requests.exceptions.RequestException as e:
            
            if not show_console:
                if not gui:
                    _gui_signals.show_console_window.emit()   

            if language == 1:
                print("❌ Unbekannter Fehler bei Anfrage an Streamer.bot.")
            if language == 0:
                print("❌ Unknown error during request to Streamer.bot.")
            if not show_console:
                start_logging()
                logging.error(f"Request error: {e}")
            return None
        return token
    
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

    #Backend Functions

    def get_switcher_version():
        try:
            with open(version_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("ProgramVersion", "unknown")
        except Exception as e:
            print(f"❌ Failed to read version.json: {e}")
            return "Unknown"

    def get_twitch_avatar(username, client_id, token):
        url = "https://api.twitch.tv/helix/users"

        headers = {
            "Client-ID": client_id,
            "Authorization": f"Bearer {token}"
        }

        params = {
            "login": username
        }

        r = requests.get(url, headers=headers, params=params)
        data = r.json()

        if "data" in data and len(data["data"]) > 0:
            return data["data"][0]["profile_image_url"]

        return None

    def get_streamerbot_path():
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                name = (proc.info['name'] or '').lower()
                if 'streamer' in name and 'bot' in name:
                    return proc.info['exe']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None


    def load_json(path):
        with open(path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)

    def get_broadcaster():
        path = get_streamerbot_path()
        if not path:
            return None

        user_dat = os.path.join(os.path.dirname(path), 'data', 'users.dat')

        try:
            data = load_json(user_dat)
        except Exception as e:
            print("JSON ERROR:", e)
            return None

        users_raw = data.get('users', {})
        users = list(users_raw.values()) if isinstance(users_raw, dict) else users_raw

        # Broadcaster (role 4), Twitch bevorzugt
        admin = next(
            (u for u in users
            if u.get('type') == 'twitch' and int(u.get('role', 0)) == 4),
            None
        )

        # Fallback Kick
        if not admin:
            admin = next(
                (u for u in users
                if u.get('type') == 'kick' and int(u.get('role', 0)) == 4),
                None
            )

        if not admin:
            return None

        return admin.get('display') or admin.get('name')    
    def get_windows_edition():
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
            )

            product_name = winreg.QueryValueEx(key, "ProductName")[0]
            display_version = winreg.QueryValueEx(key, "DisplayVersion")[0]
            current_build = int(winreg.QueryValueEx(key, "CurrentBuild")[0])

            # Windows 11 starts at build 22000+
            if current_build >= 22000:
                os_name = product_name.replace("Windows 10", "Windows 11")
            else:
                os_name = product_name

            return f"{os_name} {display_version} (Build {current_build})"

        except Exception:
            return "Unknown OS"
        
    operating_system = get_windows_edition()   
    windowsapps_map = get_windowsapps_map()
    #print (operating_system)
    username = get_broadcaster()
    avatar_url = get_twitch_avatar(username, CLIENT_ID, token)
    switcher_version = get_switcher_version()

    
    def send_user():
        if not DEBUG_MODE:
            if username:
                # User registrieren
                requests.post(
                    f"{BACKEND_URL}/user",
                    json={"username": username, "avatar_url": avatar_url},
                    headers={"X-Api-Key": backend_token},
                    timeout=5
                )
                
                # Game Data hochladen
                if os.path.exists("game_data.json"):
                                 
                    with open("game_data.json", "r", encoding="utf-8") as f:
                        game_data = json.load(f)
                    
                    #print (game_data)
                    requests.post(
                        f"{BACKEND_URL}/user/{username}/game-data",
                        json=game_data,
                        headers={"X-Api-Key": backend_token},
                        timeout=10
                    )
    if backend_api:
        send_user()


    def send_report():
        if not DEBUG_MODE:
            try:
                res = requests.post(
                    f"{BACKEND_URL}/report",
                    json={
                        "error": "Category Not Found",
                        "stack": "",
                        "username": username,
                        "version": switcher_version,
                        "matchfix_version": matchfix_version,
                        "os": operating_system,
                        "game_folder": game_folder,
                        "exe_path": exe_path,
                        "window_title": window_title,
                        "wiki_title": wiki_title
                    },
                    headers={"X-Api-Key": backend_token},
                    timeout=5
                )

                return res

            except requests.RequestException as e:
                print("REQUEST FAILED:", e)
                return None



    # Funktion, um eine Twitch-Kategorie per Name zu suchen
    # Function to search Twitch-category with the Name
    def search_twitch_category(tokensearch, search_query, _retry=False):
        global token

        if not search_query or not search_query.strip():  # ← Guard
            return []        

        url = "https://api.twitch.tv/helix/search/categories"
        headers = {
            "Authorization": f"Bearer {tokensearch}",
            "Client-ID": CLIENT_ID

        }
        params = {"query": search_query}

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 401:
            if language == 1:
                print(f"❌ Token ist nicht gültig | Erro Meldung: {response.status_code}")
            if language == 0:
                print(f"❌ Token is not valid! | Status Code: {response.status_code}")
            
            if is_streamerbot_running():               

                    
                get_access_token_action()

                # Warten, bis der Token empfangen und gespeichert wird
                time.sleep(2)
                with open("config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                    token = config["twitch"]["OAuth_token"]                
            
                if not token:
                    print("❌ No token received!" if language == 0 else "❌ Kein Token empfangen!")
                    return []
                else:
                    if language == 1:
                        print("✅ Token und CLIENT_ID erfolgreich gespeichert!\n")
                    if language == 0:
                        print("✅ Token and CLIENT_ID saved successfull!\n")
            else:
                if language == 1:
                    print("Streamer.bot nicht gestartet!")
                if language == 0:
                    print("Streamer.bot not running!")
            return search_twitch_category(token, search_query, _retry=True)
                    
        if response.status_code != 200:
            if language == 1:
                print(f"❌ Fehler bei der Kategorie-Suche: {response.status_code}, {response.text}")
            if language == 0:
                print(f"❌ Category search error: {response.status_code}, {response.text}")
            return []

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

    def search_wikipedia_game(query):
        url = "https://en.wikipedia.org/w/api.php"

        params = {
            "action": "opensearch",
            "search": query,
            "limit": 1,
            "namespace": 0,
            "format": "json"
        }

        headers = {
            "User-Agent": "StreamerBotGameResolver/1.0"
        }

        try:
            r = requests.get(url, params=params, headers=headers, timeout=5)

            if r.status_code != 200:
                return None

            data = r.json()

            if isinstance(data, list) and len(data) > 1 and data[1]:
                return data[1][0]

        except:
            return None

        return None
    
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
    # def get_largest_box_art_url(box_art_url, category_id, width, height):
    #     """Passt die URL an eine gültige 3:4-Größe an."""
    #     new_width, new_height = get_next_greater_3_4_size(width, height)
    #     new_size = f"{new_width}x{new_height}"

    #     # Ersetze nur die Kategorie-ID, behalte aber _IGDB
    #     modified_url = re.sub(r"(\w+)(_IGDB)?(-\d+x\d+)", rf"{category_id}_IGDB\3", box_art_url, 1)

    #     return re.sub(r"\d+x\d+", new_size, modified_url)
    


    TWITCH_404_BASE = "https://static-cdn.jtvnw.net/ttv-static/404_boxart"


    def is_valid_twitch_image(url):
        try:
            r = requests.get(url, stream=True, timeout=2)

            final_url = r.url

            if r.status_code != 200:
                return False

            if "404_boxart" in final_url:
                return False

            return True

        except:
            return False


    def get_largest_box_art_url(box_art_url, category_id, width, height):
        new_w, new_h = get_next_greater_3_4_size(width, height)
        size = f"{new_w}x{new_h}"

        def make_url(use_igdb: bool):
            url = re.sub(
                r"(\w+)(_IGDB)?(-\d+x\d+)",
                rf"{category_id}{'_IGDB' if use_igdb else ''}\3",
                box_art_url,
                count=1
            )
            return re.sub(r"\d+x\d+", size, url)

        # 1. IGDB Versuch
        url = make_url(True)
        if is_valid_twitch_image(url):
            return url

        # 2. fallback ohne IGDB
        url = make_url(False)
        if is_valid_twitch_image(url):
            return url

        # 3. dynamischer 404 (WICHTIGER FIX)
        return f"{TWITCH_404_BASE}-{size}.jpg"

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

    def debug_window_check():
        results = []
        
        def callback(hwnd, _):
            if ctypes.windll.user32.IsWindowVisible(hwnd):
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                proc_id = wintypes.DWORD()
                ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(proc_id))
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                    results.append((hwnd, proc_id.value, buff.value))
            return True
        
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        ctypes.windll.user32.EnumWindows(WNDENUMPROC(callback), 0)
        
        with open("all_windows_debug.txt", "w", encoding="utf-8") as f:
            f.write(f"frozen={getattr(sys, 'frozen', False)}\n")
            f.write(f"Eigene PID: {os.getpid()}\n")
            f.write(f"Gefundene Fenster: {len(results)}\n\n")
            for hwnd, pid, title in results:
                f.write(f"HWND: {hwnd}, PID: {pid}, Titel: {title}\n")


    def get_window_title_by_exe(pid, timeout=0, interval=0.5, check_children=True):
            """
            Ermittelt den Fenstertitel eines Prozesses.
            Prüft bei check_children=True auch Kindprozesse, falls der Hauptprozess
            selbst kein sichtbares Fenster hat (z.B. bei Launcher-Wrapper-exes).
            Bei timeout > 0 wird bis zu 'timeout' Sekunden gepollt.
            """
            def _get_candidate_pids():
                pids = [pid]
                if check_children:
                    try:
                        proc = psutil.Process(pid)
                        pids.extend(child.pid for child in proc.children(recursive=True))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                return pids

            def _find_title():
                candidate_pids = set(_get_candidate_pids())
                titles = []
                
                def callback(hwnd, _):
                    if ctypes.windll.user32.IsWindowVisible(hwnd):
                        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                        if length > 0:
                            proc_id = wintypes.DWORD()
                            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(proc_id))
                            if proc_id.value in candidate_pids:
                                buff = ctypes.create_unicode_buffer(length + 1)
                                ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                                titles.append(buff.value)
                    return True
                
                WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
                ctypes.windll.user32.EnumWindows(WNDENUMPROC(callback), 0)
                
                if not titles:
                    return None
                
                title = titles[0]
                title = re.sub(r'[™®©℠]', '', title)
                title = re.sub(r'\s+v\d+[\.\d]*$', '', title, flags=re.IGNORECASE)
                
                suffixes_to_remove = [
                    r'\s*-\s*Steam$',
                    r'\s*-\s*Epic Games$',
                    r'\s*-\s*GOG$',
                    r'\s*\(\d+\)$',
                    r'\s*\[.*?\]$',
                    r'\s*\|.*$',
                ]
                for suffix in suffixes_to_remove:
                    title = re.sub(suffix, '', title, flags=re.IGNORECASE)
                
                return title.strip() or None

            if timeout <= 0:
                return _find_title()

            elapsed = 0.0
            while elapsed < timeout:
                title = _find_title()
                if title:
                    return title
                time.sleep(interval)
                elapsed += interval
            return None

    def get_all_window_pids():
        pids_with_window = set()

        def callback(hwnd, _):
            if ctypes.windll.user32.IsWindowVisible(hwnd):
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    proc_id = wintypes.DWORD()
                    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(proc_id))
                    pids_with_window.add(proc_id.value)
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        ctypes.windll.user32.EnumWindows(WNDENUMPROC(callback), 0)
        return pids_with_window


    # Set für bereits ausgegebene Prozesse (kombiniert aus PID und exe-Pfad)
    # Set already found processes (combined of PID and exe path)
    seen_processes = set()
    _notification_ready.wait(timeout=30)

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
                if token is None:
                    return
                
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
                        
            if update_from_version_below_2:
                get_access_token_action()
                
    else:            
        if language == 1:
            print("⚠️ Nur lokale Datenbank verwenden ist aktiviert.")  
        if language == 0:
            print("⚠️ Use only local database is enabled.")
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
                    print("🆕 Die Datei wird mit einer leeren Spiele-Liste neu erstellt.\n")
                if language == 0:
                    print("❌ Error: File 'game_data.json' doesn't exist.")
                    print("🆕 The file will be created new with an empty games list.\n")
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
    connection = None
    category_name = "Just Chatting"
    kick_category_name = "Just Chatting"
    if is_streamerbot_running():
        if kick_enabled:
            connection = category_change(category_name, kick_category_name)
        else:
            connection = category_change(category_name)
    obs_started = False
    streamerbot_started = False
    displayed_warning = False
    displayed_warning_category = False
    
    if token is not None and connection is not None:
        print("-" * 90)
        if language == 1:           
            print("⌛ Warte auf Spiel Prozess 🎮".center(88))
        if language == 0:
            print("⌛ Wating for the game process 🎮".center(84))
        print("-" * 90)


    if rules:
        excluded_exe_patterns = rules["excluded_exe_patterns_in_code"]
        excluded_exe_names = rules["excluded_exe_names_in_code"]
        excluded_exe_exact = set(rules["excluded_exe_exact_in_code"])
        game_name_mappings = rules["game_name_mappings"]
        game_name_exact = rules["game_name_exact"]
        
    else:
        if language == 1:
            print("⚠️ Matchfixes nicht verfügbar, die Kategorien können für manche Spiele nicht korrekt gefunden werden!")
        if language == 0:
            print("⚠️ Matchfixes not available, finding categorys might not work properly for some games!")       

    process_to_game = {}
    while True:
        try:
           
            current_modified = os.path.getmtime(config_path)
            
            if current_modified != last_modified:
                ##print("Die config.json wurde geändert, neu laden!")
                last_modified = current_modified
                load_config_live()
  
                #print(f"show_console = {show_console}")
                #print(f"frozen = {getattr(sys, 'frozen', False)}")
                #print(f"console = {console}")
                if not show_console:
                    #print("hide path")
                    if not getattr(sys, 'frozen', False):
                       # print("frozen block")
                        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
                        if hwnd:
                            ctypes.windll.user32.ShowWindow(hwnd, 0)
                    if console is not None:
                        #print("emitting hide signal")
                        _gui_signals.hide_console_window.emit()
                else:
                    #print("emitting show signal")
                    _gui_signals.show_console_window.emit()
                
                # if not show_console:
                #     if not getattr(sys, 'frozen', False):  
                #         # Falls als .py ausgeführt, direkt ohne Konsole starten
                #         restart_program(with_console=False)
                #     else:
                #         restart_program_no_console()
                # else:
                #     if not gui:
                #         start_gui()
                if censor_mode:
                    censoring()# Hier rufst du deine Funktion auf        
            current_seen = set()
            window_pids_this_cycle = get_all_window_pids()
            root_folder = None
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    
                    failed = False
                    exe_path = proc.info['exe']
                    pid = proc.info['pid']
                    name = proc.info['name']


                    is_windowsapps = not exe_path or 'WindowsApps' in (exe_path or '')
                    # Sicherstellen, dass der Prozess ein valides exe_path hat und in allowed_paths liegt
                    # Make sure process has an valid exe_path and is in allowed_paths
                    if not exe_path or name in excluded_names:
                        continue
                    
                    # Prüfen, ob der exe_path in allowed_paths ist
                    normalized_exe_path = os.path.normcase(os.path.normpath(exe_path))
                
                    normalized_allowed_paths = [os.path.normcase(os.path.normpath(path)) for path in allowed_paths]
                    name_lower = name.lower()
                    
                    skip_path_check = name_lower in (
                        'playnite.desktopapp.exe',
                        'playnite.fullscreenapp.exe'
                    ) or is_windowsapps or is_known_art_program_path(exe_path.lower())
                    

                    if not skip_path_check:
                        if not any(normalized_exe_path.startswith(path) for path in normalized_allowed_paths):
    ##                        print(f"Prozess {name} mit exe_path {exe_path} ist nicht in allowed_paths.")
                            continue  # Wenn der exe_path nicht in allowed_paths liegt, überspringe diesen Prozess
                         
                    exe_lower = os.path.basename(exe_path).lower()
                    
                    #Überspringe verschiedene nicht gewollte Exe dateien
                    #Skip not wanted exe files
                    
 
                    # Pfad-Patterns prüfen (z.B. obs studio, steamvr)
                    if any(pattern in exe_path.replace("\\", "/").lower() for pattern in excluded_exe_patterns):
                        continue
                    
                    # Exe-Name Contains prüfen
                    if any(name in exe_lower for name in excluded_exe_names) and exe_lower.endswith(".exe"):
                        continue
                           
                    # Exakte Exe-Namen prüfen
                    if exe_lower in excluded_exe_exact:
                        continue
                    
                    if "retroarch" in exe_lower and exe_lower.endswith(".exe"):
                        continue
                        if is_playnite_running() or game_set:
                            continue
                        
                    if "minecraft" in exe_lower and exe_lower.endswith(".exe"):
                        root_folder = "Minecraft"

                        
                                       
                    if (("playnite.desktopapp" in exe_lower or "playnite.fullscreenapp" in exe_lower ) and exe_lower.endswith(".exe")):
                        
                        if playnite_enabled:
                            playnite_running = True
                            if not watcher_started:
                                folder_path = os.path.dirname(exe_path)
                                filepath = os.path.join(folder_path, "RunningGame.json")                        
                                # Prüfen ob Datei existiert
                                if not os.path.exists(filepath):
                                    # Fallback auf %appdata%\playnite
                                    folder_path = os.path.join(os.getenv("APPDATA"), "playnite")
                                    filepath = os.path.join(folder_path, "RunningGame.json")

                               #print(filepath)                        
                                start_watcher()
                                watcher_started = True
                                game_started_event.clear()
                                if language == 1:
                                    print(f"\n✅ Playnite erkannt: PID {pid} Path: {exe_path}\n")
                                if language == 0:
                                    print(f"\n✅ Playnite detected: PID {pid} Path: {exe_path}\n")
                                    
                                print("-" * 90)
                                if language == 1:           
                                    print("⌛ Warte auf GameStarted Event 🎮".center(82))
                                if language == 0:
                                    print("⌛ Waiting on the GameStarted Event 🎮".center(80))
                                print("-" * 90)
                                waiting_for_game = True

                            if waiting_for_game:                             
                                while True:
                                    game_started_event.wait(timeout=1)
                                    # 1️⃣ Wenn Spiel gestartet wurde → weiter
                                    if game_started_event.is_set():
                                        waiting_for_game = False
                                        if game_folder is not None and game_folder != latest_game_event['Name']:
                                            if not prev_game_set:  # ← nur setzen wenn noch nicht gesetzt
                                                previous_game_folder = latest_game_event['Name']
                                                prev_game_set = True
                                            
                                        game_folder = latest_game_event['Name']
                                        kick_game_folder = game_folder
                                        exe_path = latest_game_event['Path']
                                        game_set = True

                                        if latest_game_event.get('Type') != "Emulator":
                                            save_games_to_file = False

                                        #print(f"🎮 Neuestes Spiel aus Playnite: {game_folder}")
                                        break

                                    # 2️⃣ Wenn Playnite nicht mehr läuft → abbrechen
                                    if not is_playnite_running():
                                        
                                        waiting_for_game = False
                                        game_set = False
                                        Playnite_Game_Retry = True
                                        Playnite_Game_Stopped = False
                                        Playnite_exit = True
                                        save_games_to_file = True
                                        if watcher_started:
                                            watcher_started = False
                                            stop_watcher()
                                        
                                        break

                                time.sleep(0.5)  # CPU-schonend
                                                            
                                if Playnite_exit:
                                    game_folder = "Playnite"
                                    continue    
                                
                            if game_set is not None:
                                if game_folder is not None and game_folder != latest_game_event['Name']:
                                    if not prev_game_set:  # ← nur setzen wenn noch nicht gesetzt
                                        previous_game_folder = latest_game_event['Name']
                                        prev_game_set = True
                                game_folder = latest_game_event['Name']
                                kick_game_folder = game_folder
                                exe_path = latest_game_event['Path']
                                ##print(f"🎮 Spiel aus Playnite wird gesetzt: {game_folder}")
                        else:
                            continue
                        
                    if playnite_running == True and waiting_for_game == False:
                        
                        if not is_playnite_running():
                            game_set = False
                            Playnite_Game_Retry = True
                            Playnite_Game_Stopped = False
                            Playnite_exit = True
                            save_games_to_file = True
                            if watcher_started:
                                watcher_started = False
                                stop_watcher()             

                    if is_windowsapps and not game_set:
                        display_name = windowsapps_map.get(exe_lower)
                        if not display_name:
                            continue  # unbekannte WindowsApp, überspringen
                        
                        if pid not in window_pids_this_cycle:   
                            continue # Windowsapp ohne Fenster überspringen
                        
                        new_folder = display_name
                        if not prev_game_set:
                            previous_game_folder = new_folder
                            prev_game_set = True
                        game_folder = new_folder
                        kick_game_folder = game_folder
                        found_folder = game_folder
                    
                    if is_ue_or_known_exe_path(exe_path.lower()):
                        if game_folder is not None and game_folder != "Software and game development":
                            if not prev_game_set:
                                previous_game_folder = game_folder
                                prev_game_set = True
                        

                        game_folder = "Software and game development"
                        kick_game_folder = "Software Development"
                        if not prev_game_set:
                            previous_game_folder = game_folder
                            prev_game_set = True
                            
                        if game_folder in displayed_games:  # ← bereits erkannt, überspringen
                            unique_id = (pid, exe_path)
                            current_seen.add(unique_id)
                            process_to_game.setdefault(unique_id, game_folder)
                            continue  # ← rest des Loops überspringen
                        
                    elif is_known_art_program_path(exe_path.lower()):
                        if pid not in window_pids_this_cycle: 
                            continue  
                        
                        if game_folder is not None and game_folder != "Art":
                            if not prev_game_set:
                                previous_game_folder = game_folder
                                prev_game_set = True

                        game_folder = "Art"
                        kick_game_folder = "Art"
                        if not prev_game_set:
                            previous_game_folder = game_folder
                            prev_game_set = True

                        if game_folder in displayed_games:
                            unique_id = (pid, exe_path)
                            current_seen.add(unique_id)
                            process_to_game.setdefault(unique_id, game_folder)
                            continue
                
                    else:    
                        # Gültigen Root-Ordner finden
                        # Find valid root folder
                        if not root_folder:
                            if not is_windowsapps:
                                root_folder = get_valid_root_folder(exe_path, allowed_paths, excluded_folders)
                                
                ##                if root_folder:
                ##                    print(f"Root: {root_folder}")

                                if not root_folder:
                                    continue  # Falls kein gültiger Root-Ordner gefunden wurde, überspringe diesen Prozess
                                            # If no valid root folder found skip that process

                                # Spielname extrahieren (Ordner der .exe)
                                # Extrac gamename (Folder of .exe)
                                if not game_set:
                                    #game_folder = os.path.basename(root_folder)
                                    new_folder = os.path.basename(root_folder)
                                    #if game_folder is not None and game_folder != new_folder:
                                    if not prev_game_set:  # ← nur setzen wenn noch nicht gesetzt
                                        previous_game_folder = new_folder
                                        prev_game_set = True

                                    game_folder = new_folder
                                    kick_game_folder = game_folder
                                    found_folder = game_folder
                    if not game_folder:
                        game_folder = root_folder
                        kick_game_folder = game_folder

    ##                print(f" Debug output game_folder: {game_folder}")
                    exe_lower = os.path.basename(exe_path).lower()
                    # launcher excludes

                    launcher_list = [
                        "riot games",
                        "battle.net",
                        "electronic arts",
                        "ubisoft game launcher",
                        "origin games",
                        "epic games",
                        "ea desktop",
                        "electronic arts",
                        "steam"
                    ]
                    
                    

                    if game_folder.lower() in launcher_list:
                        continue
                    
                    # Spezial Fälle für Emulator Games zum matchen
                    
                    for mapping in game_name_mappings:
                        if mapping["contains"] in game_folder.lower():
                            game_folder = mapping["result"]
                            kick_game_folder = mapping.get("kick_result", game_folder)
                            break

                    for mapping in game_name_exact:
                        if mapping["match"] == game_folder.lower():
                            game_folder = mapping["result"]
                            kick_game_folder = mapping.get("kick_result", game_folder)
                            break          
                        

                    # Spezial Fälle um Twitch Kategorie richtig zu matchen            
                    # Edge cases setting game_folder forceful to get twitch match            
                    if "Intergrade" in game_folder:
                        game_folder = remove_intergrade_from_folder(game_folder)
                        kick_game_folder = game_folder

                    if is_ue_or_known_programming_folder(game_folder.lower()):
                        game_folder = "Software and game development"                     
                                    
                    if game_folder in gta5_variants:
                        game_folder = "Grand Theft Auto V"
                        kick_game_folder = game_folder

                    if game_folder in gta4_variants:
                        game_folder = "Grand Theft Auto IV"
                        kick_game_folder = game_folder

                    # Entfernt alle gängigen Test-Endungen wie Demo, Alpha, Beta, Test (mit Klammern, Bindestrichen, Version etc.)
                    # Liste möglicher Suffixe
                    suffixes = ("demo", "alpha", "beta", "test")

                    # Nur ersetzen, wenn einer dieser Begriffe im Namen vorkommt
                    if any(suffix in game_folder.lower() for suffix in suffixes):
                        game_folder = re.sub(
                            r'[\s\-_()]*\b(?:demo|alpha|beta|test)(?:[\s\-_()]*version|\s*v?\d+)?[\s\-_()]*$',
                            '',
                            game_folder,
                            flags=re.IGNORECASE
                        ).strip()
                        kick_game_folder = game_folder

                                            
                    # Eindeutige Kombination aus PID und exe_path (damit `current_seen` funktioniert)
                    # Unique combination of PID and exe_path (so current_seen works)
                    unique_id = (pid, exe_path)
                    # if not seen_processes or any(path == exe_path for _, path in seen_processes):
                    #     current_seen.add(unique_id)
                    #     process_to_game.setdefault(unique_id, game_folder)
                    
                    

                    if unique_id in seen_processes:
                        current_seen.add(unique_id)
                        process_to_game.setdefault(unique_id, game_folder)                
                    
                        #continue
                    #current_seen.add(unique_id)
                    path_norm = os.path.normpath(exe_path)
                    #process_to_game[unique_id] = game_folder

                    # Prüfen, ob das Spiel bereits in der JSON-Datei vorhanden ist
                    # Check if Game is already saved in the local Database
                    saved_games = load_saved_games()
                    game_data = next((game for game in saved_games if game["Game"] == game_folder), None)
                    
                    if game_data and kick_enabled and (unique_id not in seen_processes or Playnite_Game_Retry):
                        kick_id = str(game_data.get("Kick Category ID") or "").strip()
                        kick_name = str(game_data.get("Kick Category Name") or "").strip()

                        kick_missing = (kick_name == "")
                        Playnite_Game_Retry = False
                        
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
                        current_seen.add(unique_id)             
                        process_to_game.setdefault(unique_id, game_folder)
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
                            if not categories:

                                if not alternatives_tried:
                                    if language == 1:
                                        print(f"\n✅ Versuche alternativen Weg für Kategorie findung")

                                    if language == 0:
                                        print(f"\n✅ Trying alternative way for category finding")
                                    
                                    window_title = get_window_title_by_exe(pid, timeout=30)
                                    categories_window_title = search_twitch_category(token, window_title) 
                                    
                                    if not categories_window_title:
                                        
                                        wiki_name = search_wikipedia_game(game_folder)

                                        if wiki_name != window_title:
                                                                                
                                            categories = search_twitch_category(token, wiki_name)  
                                            alternatives_tried = True
                                            game_folder = wiki_name
                                        else:
                                            alternatives_tried = True  
                                            
                                    else:
                                        categories = categories_window_title
                                        game_folder = window_title
                                        alternatives_tried = True
                  
                                                        
                            # Speicher die Spiel- und Twitch-Daten in einem Dictionary
                            # Save game and twitch data in a dictionary
                            if categories:
                                
                                best_match = False
                                highest_score = 0
                                
                                if game_data:
                                    best_match = {
                                        "name": game_data["Twitch Category Name"],
                                        "id": game_data["Twitch Category ID"],
                                        "box_art_url": game_data["Twitch Box Art"]
                                    }
                                    category = best_match      
                                else:
                                
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
                                    if unique_id not in seen_processes:
                                        displayed_no_category_kick = False                                    
                                    kick_categories = search_kick_category(kick_token, kick_game_folder)
                                    
                                    if not kick_categories:
                                        
                                        if not alternatives_tried_kick:
                                            window_title = get_window_title_by_exe(pid) 
                                            kick_categories_window_title = search_kick_category(kick_token, window_title)                          
                                            if not kick_categories_window_title:
                                                if wiki_name != window_title:
                                                    kick_categories = search_kick_category(kick_token, wiki_name)
                                                    alternatives_tried_kick = True
                                                    kick_game_folder = wiki_name
                                                else:
                                                    alternatives_tried_kick = True
                                            else:
                                                kick_categories = kick_categories_window_title
                                                kick_game_folder = window_title
                                                alternatives_tried_kick = True

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
                                        category['id'] = "1608308954"
                                        game_data = {
                                            "Game": game_folder,
                                            "Path": os.path.normpath(exe_path),  
                                            "Twitch Category Name": best_match["name"],
                                            "Twitch Category ID": category['id'],
                                            "Twitch Box Art": get_largest_box_art_url(category['box_art_url'], category['id'], width, height)
                                        }

                                    elif game_folder == "Dispatch":
                                        category['id'] = "602959317"
                                        game_data = {
                                            "Game": game_folder,
                                            "Path": os.path.normpath(exe_path),  
                                            "Twitch Category Name": best_match["name"],
                                            "Twitch Category ID": category['id'],
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
                                        
                                    if kick_enabled:                                # Kick-Ergebnis ergänzen
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
                                            if not displayed_no_category_kick:                                  
                                                if language == 1:
                                                    print(f"⚠️ Keine Kick-Kategorie für '{kick_game_folder}' gefunden.")
                                                    if not show_console:
                                                        start_logging()
                                                        logging.info(f"⚠️ Keine Kick-Kategorie für '{kick_game_folder}' gefunden.")
                                                        logging.info(f"⚠ Pfad aus welchem Name extrahiert wurde '{path_norm}")
                                                if language == 0:
                                                    print(f"⚠️ No Kick Category found for '{kick_game_folder}'.")
                                                    if not show_console:
                                                        start_logging()
                                                        logging.info(f"⚠️ No Kick Category found for '{kick_game_folder}'.")
                                                        logging.info(f"⚠ Path from which game name got extracted '{path_norm}")
                                                kick_failed = True
                                                displayed_no_category_kick = True
                                                
                                
                                    saved_games.append(game_data)
                                    current_seen.add(unique_id)
                                    process_to_game.setdefault(unique_id, game_folder)

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
                                            if default_category:
                                                if displayed_no_category_kick:
                                                    kick_category_name = default_kick_category
                                            
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
                                                        if kick_failed:
                                                            send_message(game_folder, category_name, kick_category_name, kick_failed=True) 
                                                        else:                                               
                                                            send_message(game_folder, category_name, kick_category_name, kick_failed=False)
                                                    else:
                                                        send_message(game_folder, category_name)
                                else:
                                    if not displayed_warning:
                                        if not default_category:
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
                                        else:

                                            if language == 1:
                                                print(f"⚠️ Keine Twitch-Kategorie für '{game_folder}' gefunden. Verwende Standard-Kategorie '{default_twitch_category}'.")
                                                if not show_console:
                                                    start_logging()
                                                    logging.info(f"⚠️ Keine Twitch-Kategorie für '{game_folder}' gefunden. Verwende Standard-Kategorie '{default_twitch_category}'.")
                                                    logging.info(f"⚠ Pfad aus welchem Name extrahiert wurde '{path_norm}")
                                            if language == 0:                                                
                                                print(f"⚠️ No Twitch Category found for '{game_folder}'. Using default category '{default_twitch_category}'.")
                                                if not show_console:
                                                    start_logging()
                                                    logging.info(f"⚠️ No Twitch Category found for '{game_folder}'. Using default category '{twitch_category}'.")
                                                    logging.info(f"⚠ Path from which game name got extracted '{path_norm}")  
                                            displayed_games.add(game_folder)  
                                            category_name = default_twitch_category
                                            if kick_enabled:
                                                kick_category_name = default_kick_category
                                            if is_streamerbot_running():
                                                if category_set_already != category_name:
                                                    if kick_enabled:
                                                        category_change(category_name, kick_category_name)
                                                    else:
                                                        category_change(category_name)
                                                    category_set_already = category_name 
                                        current_seen.add(unique_id)
                                        process_to_game.setdefault(unique_id, game_folder)                                      
                                        displayed_warning = True
                                        failed = True
                                        if message:
                                            if kick_enabled:
                                                send_message(game_folder, category_name, kick_category_name)
                                            else:
                                                send_message(game_folder, category_name)
                                displayed_warning = True
                            else:
                                if not displayed_warning:
                                    if not default_category:
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
                                    else:
                                        if language == 1:
                                            print(f"⚠️ Keine Twitch-Kategorie für '{game_folder}' gefunden. Verwende Standard-Kategorie '{default_twitch_category}'.")
                                            if not show_console:
                                                start_logging()
                                                logging.info(f"⚠️ Keine Twitch-Kategorie für '{game_folder}' gefunden. Verwende Standard-Kategorie '{default_twitch_category}'.")
                                                logging.info(f"⚠ Pfad aus welchem Name extrahiert wurde '{path_norm}")
                                        if language == 0:                                                
                                            print(f"⚠️ No Twitch Category found for '{game_folder}'. Using default category '{default_twitch_category}'.")
                                            if not show_console:
                                                start_logging()
                                                logging.info(f"⚠️ No Twitch Category found for '{game_folder}'. Using default category '{default_twitch_category}'.")
                                                logging.info(f"⚠ Path from which game name got extracted '{path_norm}")  
                                        displayed_games.add(game_folder)    
                                        category_name = default_twitch_category
                                        if kick_enabled:
                                            kick_category_name = default_kick_category
                                        if is_streamerbot_running():
                                            if category_set_already != category_name:
                                                if kick_enabled:
                                                    category_change(category_name, kick_category_name)
                                                else:
                                                    category_change(category_name)
                                                category_set_already = category_name                                          
                                    current_seen.add(unique_id)
                                    process_to_game.setdefault(unique_id, game_folder)                                    
                                    displayed_warning = True
                                    failed = True
                                    if message:
                                        if kick_enabled:
                                            send_message(game_folder, category_name, kick_category_name)
                                        else:                                    
                                            send_message(game_folder, category_name) 
                            if not report_sended:
                                if backend_api:    
                                    send_report() 
                                    report_sended = True
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
            
            delayed_reset_called = {}  

            def delayed_category_reset(displayed_games, seen_processes, current_seen, stopped_program_snap, previous_game_snap, prev_game_data_snap):
                global delay_programming, game_folder, program_stopped
                
                delay_ms = delay_programming

                def reset_stale_id(stopped):
                    
                    stale_ids = [uid for uid, g in process_to_game.items() if g == stopped]
                    for uid in stale_ids:
                        process_to_game.pop(uid, None)

                def reset():
                    global category_set_already , game_folder, program_stopped, previous_game_folder, prev_game_set
                    
                    stopped_program = stopped_program_snap
                    prev_game = previous_game_snap
                    game_data = prev_game_data_snap
                    reset = False
                    current_program = game_folder
                    #stopped_program = program_stopped

                    if current_program == stopped_program:
                        reset = False
                    
                    if current_program != None and current_program != stopped_program:
                        reset_stale_id(stopped_program)
                        #displayed_games.remove(stopped_program)
                        prev_game_set = False
                        reset = True 
                    
                    if game_folder == None:
                        reset = True           

                    if prev_game != None and prev_game != stopped_program:
                        reset = True                               

                    
                    if reset:
                        if stopped_program in displayed_games:
                            displayed_games.remove(stopped_program)
                            category_set_already = None
                            failed = False

                            reset_stale_id(stopped_program)
                                
                            if prev_game is not None and prev_game in displayed_games:
                                if game_data: 
                                    category_name = game_data["Twitch Category Name"]
                                    kick_category_name = game_data.get("Kick Category Name", "Just Chatting")
                                    game_folder = prev_game
                                    previous_game_folder = None 
                                    prev_game_set = False
                                else:
                                    category_name = "Just Chatting"
                                    kick_category_name = "Just Chatting"
                                    previous_game_folder = None
                                    prev_game_set = False
                            else:
                                category_name = "Just Chatting"
                                kick_category_name = "Just Chatting"
                                previous_game_folder = None
                                prev_game_set = False


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
                            if playnite_enabled:
                                if not is_playnite_running():
                                    if watcher_started:
                                        stop_watcher()
                    program_stopped = None
                    delayed_reset_called[stopped_program] = False
                    displayed_warning = False
                    displayed_warning_category = False

                delay_seconds = delay_ms / 1000.0
                threading.Thread(target=lambda: (time.sleep(delay_seconds), reset())).start()
                
            def delayed_category_reset_dynamic(displayed_games, seen_processes, current_seen, game_stopped_snap, previous_game_folder_snap, prev_game_data_snap):
                global delay_general, Playnite_Game_Stopped, game_stopped, game_folder

                delay_ms = delay_general

                def reset_displayed_games(closed_game):
                    global category_set_already, Playnite_Game_Stopped, game_stopped, game_folder, previous_game_folder, prev_game_set

                    stale_ids = [uid for uid, g in process_to_game.items() if g == closed_game]
                    for uid in stale_ids:
                        process_to_game.pop(uid, None)
                    previous_game_folder = None
                    prev_game_set = False                                           
                    displayed_games.remove(closed_game)

                def reset():
                    global category_set_already, Playnite_Game_Stopped, game_stopped, game_folder, previous_game_folder, prev_game_set

                    stopped_game = game_stopped_snap
                    prev_game = previous_game_folder_snap
                    game_data = prev_game_data_snap
                    reset = False
                    current_game = game_folder
                    
                    if current_game == stopped_game:
                        reset = False
                    
                    if current_game != None and current_game != stopped_game:
                        prev_game_set = False
                        reset = False 
                    
                    if current_game == None:
                        reset = True
                        
                    if prev_game != None and prev_game != stopped_game:
                        reset = True
                        
                    if prev_game == stopped_game:
                        reset_displayed_games(stopped_game)

                    if reset:
                        if stopped_game in displayed_games:
                            displayed_games.remove(stopped_game)
                            category_set_already = None
                            failed = False

                            stale_ids = [uid for uid, g in process_to_game.items() if g == stopped_game]
                            for uid in stale_ids:
                                process_to_game.pop(uid, None)


                            if prev_game is not None and prev_game in displayed_games:
                                if game_data:  # ← direkt verwenden
                                    category_name = game_data["Twitch Category Name"]
                                    kick_category_name = game_data.get("Kick Category Name", "Just Chatting")
                                    game_folder = prev_game
                                    previous_game_folder = None 
                                    prev_game_set = False
                                else:
                                    category_name = "Just Chatting"
                                    kick_category_name = "Just Chatting"
                                    previous_game_folder = None
                                    prev_game_set = False
                            else:
                                category_name = "Just Chatting"
                                kick_category_name = "Just Chatting"
                                previous_game_folder = None
                                prev_game_set = False


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
                            if playnite_enabled:
                                if not is_playnite_running():
                                    if watcher_started:
                                        stop_watcher()
                    game_stopped = None
                    delayed_reset_called[stopped_game] = False
                    displayed_warning = False
                    displayed_warning_category = False

                delay_seconds = delay_ms / 1000.0
                threading.Thread(target=lambda: (time.sleep(delay_seconds), reset())).start()
            
                
            def delayed_category_reset_playnite(displayed_games, seen_processes, current_seen, game_stopped_snap, previous_game_folder_snap, prev_game_data_snap):
                global delay_general, Playnite_Game_Stopped, game_stopped, game_folder

                delay_ms = delay_playnite

                def reset_displayed_games(closed_game):
                    global category_set_already, Playnite_Game_Stopped, game_stopped, game_folder, previous_game_folder, prev_game_set

                    stale_ids = [uid for uid, g in process_to_game.items() if g == closed_game]
                    for uid in stale_ids:
                        process_to_game.pop(uid, None)
                    previous_game_folder = None
                    prev_game_set = False                                           
                    #displayed_games.remove(closed_game)

                def reset():
                    global category_set_already, Playnite_Game_Stopped, game_stopped, game_folder

                    stopped_game = game_stopped_snap
                    prev_game = previous_game_folder_snap
                    game_data = prev_game_data_snap
                    reset = False
                    current_game = game_folder

                    
                    if current_game == stopped_game:
                        reset = False
                    
                    if current_game != None and current_game != stopped_game:
                        reset = False
                    
                    if current_game == None:
                        reset = True
                        
                    if prev_game != None and prev_game != stopped_game:
                        reset = True
                        
                    if prev_game != stopped_game:
                        reset_displayed_games(stopped_game)
                                                
                    if reset:
                        if stopped_game in displayed_games:
                            displayed_games.remove(stopped_game)
                            category_set_already = None
                            failed = False

                            if prev_game is not None and prev_game in displayed_games:
                                if game_data: 
                                    category_name = game_data["Twitch Category Name"]
                                    kick_category_name = game_data.get("Kick Category Name", "Just Chatting")
                                    game_folder = prev_game
                                    previous_game_folder = None 
                                    prev_game_set = False
                                else:
                                    category_name = "Just Chatting"
                                    kick_category_name = "Just Chatting"
                                    previous_game_folder = None
                                    prev_game_set = False
                            else:
                                category_name = "Just Chatting"
                                kick_category_name = "Just Chatting"
                                previous_game_folder = None
                                prev_game_set = False
                                Playnite_Game_Retry = True
                                waiting_for_game = True
                                


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
                            if playnite_enabled:
                                if not is_playnite_running():
                                    if watcher_started:
                                        stop_watcher()

                    delayed_reset_called[stopped_game] = False
                    displayed_warning = False
                    displayed_warning_category = False
                    save_games_to_file = True

                delay_seconds = delay_ms / 1000.0
                threading.Thread(target=lambda: (time.sleep(delay_seconds), reset())).start()
            
            if Playnite_Game_Stopped:
                
                if language == 1:
                    print("-" * 90)
                    print(f"   ❌ Spiel beendet: {game_folder}")
                    print("-" * 90)
                if language == 0:
                    print("-" * 90)
                    print(f"   ❌ Game Closed: {game_folder}")
                    print("-" * 90) 
                
                if delay_playnite and delay_playnite > 0:
                    
                    Playnite_Game_Stopped = False
                    if game_folder not in delayed_reset_called or not delayed_reset_called[game_folder]:
                        game_stopped = game_folder
                        prev_game_data = next((g for g in saved_games if g["Game"] == previous_game_folder), None)
                        game_folder = None
                        delayed_reset_called[game_stopped] = True
                        delayed_category_reset_playnite(displayed_games, seen_processes, current_seen, game_stopped, previous_game_folder, prev_game_data)
                            
        
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
                        Playnite_Game_Stopped = False
                waiting_for_game = True
                game_set = False
                save_games_to_file = True
                Playnite_Game_Retry = True
        
            if not is_playnite_running():
                
                if Playnite_exit or (playnite_running == True and waiting_for_game == False): 
                    if playnite_running == True:
                        name = "Playnite"
                    else: 
                        name = game_folder
                    if language == 1:
                        print("-" * 90)
                        print(f"   ❌ {name} Beendet: PID {pid}")
                        print("-" * 90)
                    if language == 0:
                        print("-" * 90)
                        print(f"   ❌ {name} Closed: PID {pid}")
                        print("-" * 90)   
                    Playnite_exit = False
                    playnite_running = False
                    #printed_closed = True
                    
                                
                for unique_id in seen_processes - current_seen:
                    pid, exe_path = unique_id
                    closed_game = process_to_game.pop(unique_id, game_folder)
                    if closed_game is None:
                        continue  # ← unbekannter Prozess, ignorieren                
                    still_running = any(g == closed_game for g in process_to_game.values())
                    if still_running:
                        #printed_closed = True  # ← kein Print, kein Reset
                        continue
                    
                    if not printed_closed:
                        if language == 1:
                            print("-" * 90)
                            print(f"   ❌ Beendet: PID {pid}, Spiel: {closed_game}")
                            print("-" * 90)
                        if language == 0:
                            print("-" * 90)
                            print(f"   ❌ Closed: PID {pid}, Game: {closed_game}")
                            print("-" * 90)   
                    printed_closed = False

                    if closed_game == "Software and game development":
                        
                        if delay_programming and delay_programming > 0:
                            # Wenn das Spiel im Ordner geschlossen wird und die Verzögerung noch nicht gesetzt wurde
                            if closed_game not in delayed_reset_called or delayed_reset_called[closed_game] == False:
                                program_stopped = closed_game
                                prev_game_data = next((g for g in saved_games if g["Game"] == previous_game_folder), None)
                                game_folder = None
                                delayed_reset_called[program_stopped] = True  # Verzögerung für diesen Ordner wurde gesetzt
                                delayed_category_reset(displayed_games, seen_processes, current_seen, program_stopped, previous_game_folder, prev_game_data)  # 50 Sekunden Verzögerung


                    elif closed_game != "Software and game development":
                        if delay_general and delay_general > 0:
                            
                            if game_folder not in delayed_reset_called or not delayed_reset_called[closed_game]:
                                game_stopped = closed_game
                                prev_game_data = next((g for g in saved_games if g["Game"] == previous_game_folder), None)
                                game_folder = None
                                delayed_reset_called[game_stopped] = True
                                delayed_category_reset_dynamic(displayed_games, seen_processes, current_seen, game_stopped, previous_game_folder, prev_game_data)

                                
                        else:               
                            displayed_warning = False
                            displayed_warning_category = False

                            # Entferne das Spiel aus displayed_games, wenn es beendet wurde
                            
                            
                            if closed_game in displayed_games:
                                displayed_games.remove(closed_game)
                                #category_name = "Just Chatting"
                            # kick_category_name = "Just Chatting"
                                stale_ids = [uid for uid, g in process_to_game.items() if g == closed_game]
                                for uid in stale_ids:
                                    process_to_game.pop(uid, None)
                                prev_game_data = next((g for g in saved_games if g["Game"] == previous_game_folder), None)
                                current_game = game_folder
                                if current_game != closed_game:
                                    if closed_game == previous_game_folder:
                                        previous_game_folder = current_game
                                        continue
                                    previous_game_folder = current_game
                                    if previous_game_folder is not None and previous_game_folder in displayed_games and prev_game_data:
                                        category_name = prev_game_data["Twitch Category Name"]
                                        kick_category_name = prev_game_data.get("Kick Category Name", "Just Chatting")
                                        game_folder = previous_game_folder
                                        stale_ids = [uid for uid, g in process_to_game.items() if g == closed_game]
                                        for uid in stale_ids:
                                            process_to_game.pop(uid, None)
                                    #continue
                                else:
                                    
                                    if previous_game_folder is not None and previous_game_folder in displayed_games and prev_game_data:
                                        category_name = prev_game_data["Twitch Category Name"]
                                        kick_category_name = prev_game_data.get("Kick Category Name", "Just Chatting")
                                        game_folder = previous_game_folder
                                        stale_ids = [uid for uid, g in process_to_game.items() if g == closed_game]
                                        for uid in stale_ids:
                                            process_to_game.pop(uid, None)
                                        # optional: previous zurücksetzen nach Restore

                                    else:
                                        category_name = "Just Chatting"
                                        kick_category_name = "Just Chatting"   
                                    
                                #previous_game_folder = None
                                prev_game_set = False                      
                                failed = False
                                game_set = False
                                Playnite_exit = False
                                if watcher_started:
                                    stop_watcher()
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
                    if save_games_to_file:
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

        except Exception:  # ← NEU: fängt alle unbehandelten Exceptions im while-body
            import traceback
            import datetime
            with open("crash_log.txt", "a", encoding="utf-8") as f:
                f.write(f"\n--- {datetime.datetime.now()} ---\n")
                traceback.print_exc(file=f)
            traceback.print_exc()  # auch in der Konsole ausgeben
            time.sleep(2)  # Loop läuft weiter statt abzustürzen
    
        
# PyQt GUI starten (MUSS im Hauptthread laufen)
# Start PyQt gui, needs to run in mainthread
def start_gui():
    global gui, console
    app = QApplication.instance() or QApplication([])

    console = ConsoleApp()

    def _on_show():
        global gui
        for msg in _output_buffer:
            log_queue.put(msg)
        console.show()
        gui = True


    def _on_hide():
        global gui
        print("hide signal received")
        console.hide()
        gui = False

    _gui_signals.show_console_window.connect(_on_show)
    _gui_signals.hide_console_window.connect(_on_hide)

    if show_console:
        _on_show()  # sofort anzeigen + umleiten
        gui = True
    sys.stdout = ConsoleRedirector(log_queue)
    sys.stderr = ConsoleRedirector(log_queue)
    
    double_instance_thread = threading.Thread(target=monitor_instances, daemon=True)
    double_instance_thread.start()
    
    logic_thread = threading.Thread(target=main_logic)
    logic_thread.start()

    def on_exit():
        if language == 1:
            print("GUI geschlossen. Beende das Script.")
        if language == 0:
            print("GUI closed. Exit Script.")
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QDialog):
                widget.close()
        try:
            if _active_toast:
                _active_toast.hide()
            _toast_cleanup()
        except:
            pass
        os._exit(0)

    app.aboutToQuit.connect(on_exit)
    app.exec_()
       
if __name__ == '__main__':

    rules = None
    _qt_app = QApplication.instance() or QApplication(sys.argv)
    _qt_app.setQuitOnLastWindowClosed(False)
    _init_changelog_signal()
    _notification_ready = threading.Event()
    def _run_notification():
        global rules, excluded_exe_patterns, excluded_exe_names, excluded_exe_exact, game_name_mappings, game_name_exact
        # Windows-spezifischer Fix
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        # loop.set_exception_handler(
        #     lambda loop, ctx: None
        #     if isinstance(ctx.get("exception"), (asyncio.InvalidStateError, RuntimeError))
        #     else loop.default_exception_handler(ctx)
        # )
            try:
                rules = loop.run_until_complete(_run_update_notification())
     
            except Exception as e:
                import traceback
                with open("crash_log.txt", "w") as f:
                    traceback.print_exc(file=f)
        except Exception as e:
            import traceback
            with open("crash_log.txt", "w") as f:
                traceback.print_exc(file=f)
        finally:
            _notification_ready.set()
    

        try:
            loop.run_forever()
        except Exception:
            pass

    notification_thread = threading.Thread(target=_run_notification, daemon=True)
    notification_thread.start()
    if show_console:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)    
        start_gui() 
        _qt_app.exec_()
    else:
        
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE
        #main_logic()
        
        start_gui()
        #threading.Thread(target=main_logic, daemon=True).start()
        _qt_app.exec_()
