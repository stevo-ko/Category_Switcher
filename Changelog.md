## :small_blue_diamond: **v2.0-Sv1.0 (DE)**

### ✨ Features
- 📦 **GitHub Release**
- 🌍 Mehrsprachiges **Einstellungsmenü** in *Streamer.bot* für einfachere Konfiguration  
- 🔄 Neuer **Update-Checker** mit automatischem Herunterladen & Aktualisieren der Exe bei neuen Versionen  
- 🧪 **Experimentell:** **Kick-Kategorie-Wechsel**  
  - ⚠️ Wird in zukünftigen Updates mit Feedback sicher noch Anpassungen benötigen  

### ⚙️ Verbesserungen (QoL)
- ✅ Kein separater **API-Endpunkt** mehr nötig, um den OAuth-Token von *Streamer.bot* abzurufen  
- 🔌 Keine manuelle Eingabe von **Adresse & Port** des HTTP-Servers mehr nötig – erfolgt automatisch  
- 🗂️ Neues **Einstellungsmenü**: Einfacheres Hinzufügen/Ausschließen von Pfaden und Exe-Namen  
- 📖 Überarbeitete **Installationsanleitung**  

### 🛠️ Kategorie-Matching Fixes
- 🖥️ Korrekte Erkennung für die meisten **Programme & Entwickler-Tools**  
- 🎮 Fix für **Arena Breakout: Infinite**  
- 🔧 Verschiedene kleinere Bugfixes  

## :small_blue_diamond: **v2.0-Sv1.0 (EN)**

### ✨ Features
- 📦 **GitHub Release**
- 🌍 Added a **multilanguage Settings Menu** in *Streamer.bot* to make configuration easier  
- 🔄 Added an **Update Checker** with automatic download & update of the executable when a new version is available  
- 🧪 **Experimental:** **Kick Category Change**  
  - ⚠️ Will likely require adjustments in future updates with user feedback  

### ⚙️ Quality of Life (QoL)
- ✅ Removed the need for a **dedicated API** to retrieve the OAuth token from *Streamer.bot*  
- 🔌 No need to manually add the **address & port** of the HTTP server anymore – handled automatically  
- 🗂️ New **Settings Menu**: Easier handling of path & exe name inclusion/exclusion  
- 📖 Rewritten **Install Manual** to reflect latest changes  

### 🛠️ Category Matching Fixes
- 🖥️ Correct recognition for most **Programming & Development software**  
- 🎮 Fix for **Arena Breakout: Infinite**  
- 🔧 Miscellaneous small fixes

## :small_blue_diamond: **v1.1.5**

### :white_check_mark: General
  - :shield: Fixed most false flags by antivirus programs — a new **VirusTotal scan** has been provided in the first post.

### :tools: Bug Fixes
  - :octagonal_sign: Fixed an issue where the console wouldn’t close automatically when **Streamer.bot** was shut down.  
  - :file_folder: Corrected the handling of *excluded folders* — now only exact matches are excluded (not folders that simply **contain** the word).

### :video_game: Default Game Match Fixes (default config updates)
  - :package: Fixed matching of R.E.P.O.  
  - :tada: **The Jackbox Party Packs**: *Megapicker* is now excluded by default, Packs are all matched to category.  
  - :man_detective: Fixed detection for **The Project Unknown**.  
  - :crossed_swords: Fixed matching for **World of Warcraft (WoW)**.  
  - :dart: **Valorant** is *probably* fixed — needs further testing.

:small_blue_diamond: **v1.0**  
- :tada: Initial release  

:small_blue_diamond: **v1.1**  
- :tools: **No more Python installation required!** The app is now compiled into an .exe using PyInstaller.  
- :rocket: **Simplified setup**: No need to register an app in Twitch Developer settings anymore.  
- :video_game: **No more copying Action IDs!** The software now handles this automatically.  
- :arrows_counterclockwise: **Prevents multiple instances** from running in the background.  
- :scroll: **New "console" window**: Can be enabled/disabled and displays emojis on non-Windows 11 OS.  
- :pencil: **Automatic config creation**: A default `config.json` will be created if none is present.  
- :speech_balloon: **Chat Messages**: Added an Chat Message Action, you can Enable and Disable it and also can set if it should be an Announcement or a normal Message
- :open_file_folder: **New `game_data.json` format**: Now shows the total number of games in the database at the end.  
  - :arrows_counterclockwise: Existing `game_data.json` will be reformatted automatically on first run.  
- ✍ **Rewrote and optimized many lines of code.**  
- :scroll: **Now published under GPLv3!**
