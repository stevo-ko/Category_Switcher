## :small_blue_diamond: **v2.0.13-Sv1.0.2 (DE)**

### 🚀 Neue Features
- 🔔 Windows-Benachrichtigungen können ausgeschalten werden - derzeit nur direkt in der config.json möglich. Standart ist aktiviert

### 🛠️ Fixes
- 🔧 Problem bei dem Kategorie zurücksetzen bei Software & Development behoben

## :small_blue_diamond: **v2.0.13-Sv1.0.2 (EN)**

### 🚀 New Features
- 🔔 Windows notifications can be disabled - currently only possible in the config.json. Default is enabled

### 🛠️ Fixes
- 🔧 Fixed a problem where category resetting for software & development was not working

## :small_blue_diamond: **v2.0.12-Sv1.0.2 (DE)**

### 🚀 Neue Features
- 🧩 Hardcoded-Match-Fixes wurden ausgelagert und werden nun beim Start automatisch auf Updates geprüft – ein vollständiges Programm-Update ist dafür nicht mehr erforderlich
- 🔄 Wird ein zweites Spiel oder Programm erkannt und gematcht, merkt sich die Anwendung die zuletzt aktive Kategorie. Läuft das erste Spiel nach dem Schließen des zweiten weiterhin, wird automatisch zurück zur vorherigen Kategorie gewechselt
- 🔔 Windows-Benachrichtigungen wurden integriert – aktuell werden diese für Updates der Matchfix-Liste beim Start verwendet

### 🛠️ Kategorie-Matching Fixes
- 🔧 Problem bei der Kategorie-Suche nach Laufzeiten von über 4 Stunden behoben, da der Token ungültig wurde

## :small_blue_diamond: **v2.0.12-Sv1.0.2 (EN)**

### 🚀 New Features
- 🧩 Hardcoded match fixes have been moved externally and are now checked for updates at startup — no full program release is required anymore
- 🔄 If a second game or program is started and matched, the application will remember the previously active category. Once the second game closes, it will automatically switch back if the first game is still running
- 🔔 Windows notifications have been implemented — currently used for matchfix list updates during startup

### 🛠️ Category-Matching Fixes
- 🔧 Fixed an issue where category searching stopped working correctly after running for more than 4 hours, cause of invalid token


## :small_blue_diamond: **v2.0.11-Sv1.0.2 (DE)**

### 🛠️ Kategorie-Matching Fixes
- 🎮 Fix für **The Elder Scrolls IV: Oblivion Remastered**

## :small_blue_diamond: **v2.0.11-Sv1.0.2 (EN)**

### 🛠️ Category-Matching Fixes
- 🎮 Fix for **The Elder Scrolls IV: Oblivion Remastered**

## :small_blue_diamond: **v2.0.10-Sv1.0.2 (DE)**

### 🛠️ Exe erkennung
- 🎮 "SteamVR" wird nun nicht mehr gesehen

## :small_blue_diamond: **v2.0.10-Sv1.0.2 (EN)**

### 🛠️ Exe detecting
- 🎮 "SteamVR" will not get detected anymore

## :small_blue_diamond: **v2.0.9-Sv1.0.2 (DE)**

### 🛠️ Kategorie-Matching Fixes
- 🎮 Fix für **The Exit 8** und **Voices of the Void**

## :small_blue_diamond: **v2.0.9-Sv1.0.2 (EN)**

### 🛠️ Category-Matching Fixes
- 🎮 Fix for **The Exit 8** and **Voices of the Void**

## :small_blue_diamond: **v2.0.8-Sv1.0.2 (DE)**

### 🛠️ Kategorie-Matching Fixes
- 🎮 Fix für **Where Winds Meet**

## :small_blue_diamond: **v2.0.8-Sv1.0.2 (EN)**

### 🛠️ Category-Matching Fixes
- 🎮 Fix for **Where Winds Meet**

## :small_blue_diamond: **v2.0.7-Sv1.0.2 (DE)**

### 🛠️ Kategorie-Matching Fixes
- 🎮 Fix für **Fears of Fathom Serie**
- 🔧 Fixed **UnboundLocalError Connection**


## :small_blue_diamond: **v2.0.7-Sv1.0.2 (EN)**

### 🛠️ Category-Matching Fixes
- 🎮 Fix for **Fears of Fathom Series**
- 🔧 Fixed **UnboundLocalError Connection**


## :small_blue_diamond: **v2.0.6-Sv1.0.2 (DE)**

### 🛠️ Kategorie-Matching Fixes
- 🎮 Fix für **RV There Yet?**


## :small_blue_diamond: **v2.0.6-Sv1.0.2 (EN)**

### 🛠️ Category-Matching Fixes
- 🎮 Fix for **RV There Yet?**

## :small_blue_diamond: **v2.0.5-Sv1.0.2 (DE)**
### 🛠️ Fixes
- Spiele Launcher werden nun richtig ignoriert wenn am standart pfad installiert.
- RuneLite ist jetzt als Old School RuneScape erkannt

## :small_blue_diamond: **v2.0.5-Sv1.0.2 (EN)**
### 🛠️ Fixes
- Fixed excluding of default game launchers
- Fixed runelite matching as Old School RuneScape

## :small_blue_diamond: **v2.0.1-Sv1.0.1 (DE)**

### ✨ Features
- 📦 **Playnite Integration** Es werden nun auch Spiele in **Playnite** erkannt, somit nun auch Emulator-Spiele möglich zu matchen.
  - ⚠️Achtung: Nur mit dem Zusatz Playnite Addon **Running Game To Json** möglich! 
  - ⚠️Achtung 2: Wenn Playnite geschlossen wird, wird die Kategorie zu Just Chatting gewechselt auch wenn das Spiel noch läuft.
- ⚙️ **Backups** Es werden die 3 wichtigeen Dateien `config.json`, `game_data.json` und `Version.json` in einem Backup gesichert und automatisch wiederhegestellt bei Fehler.

### ⚙️ Verbesserungen (QoL)
- ✅ Verzögerunden der Kategorie-Änderungen werden anders behandelt und funktionieren richtig.
- 🎮 Wenn Verzögerung aktiv - bei öffnen eines neuen Spiels - wird die Kategorie sofort zu dem Spiel gewechselt, anstatt zu Just Chatting

### 🛠️ Kategorie-Matching Fixes
- 🎮 Fix für **Dispatch**.
- 🎮 Fix für **Demo,Alpha,Beta,Test** diese werden nun korrekt als die Spiele erkannt und gesetzt
- 🔧 Verschiedene kleinere Bugfixes  

## :small_blue_diamond: **v2.0.1-Sv1.0.1 (EN)**

### ✨ Features
- 📦 **Playnite Integration** Games from **Playnite** are now detected as well, making it possible to match emulator games. 
  - ⚠️ Note: Only works with the additional playnite addon **Running Game To Json**!
  - ⚠️ Note 2: When Playnite is closed, the category will also change to Just Chatting if the game is still running.
- ⚙️ **Backups** The 3 important files `config.json`, `game_data.json` and `Version.json` are saved in a backup and automatically restored in case of errors.
  
### ⚙️ Improvements (QoL)
- ✅ Delays in category changes are now handled differently and work correctly.
- 🎮 When delay is active – opening a new game now immediately switches to the game’s category instead of Just Chatting.

### 🛠️ Category-Matching Fixes
- 🎮 Fix for **Dispatch**.
- 🎮 Fix for **Demo, Alpha, Beta, Test** Games – these are now correctly recognized as the full games.
- 🔧 Various smaller bug fixes.


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
- 🎮 Fix für **Arena Breakout: Infinite** und **SCP: 5K**
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
- 🎮 Fix for **Arena Breakout: Infinite** and **SCP: 5K** 
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
