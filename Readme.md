[![GitHub Release](https://img.shields.io/github/v/release/stevo-ko/Category_Switcher?display_name=tag&label=Latest%20Release&color=1E9111)](https://github.com/stevo-ko/Category_Switcher/releases/latest)
![Language](https://img.shields.io/badge/Language-DE-brightgreen)
![Language](https://img.shields.io/static/v1?label=Language&message=EN&color=1E90FF)
[![Downloads](https://img.shields.io/github/downloads/stevo-ko/Category_Switcher/total)](https://github.com/stevo-ko/Category_Switcher/releases/latest)



<div align="center">
  <img src="https://github.com/stevo-ko/Category_Switcher/blob/main/Release%20EXE/_internal/Assets/icon.ico" width="100" height="100">
  <h1>:video_game: <strong>Category Switcher</strong> :video_game:</h1><br>

  
  <h3>Category Switcher is a small program intended to automate the changing of the category when you live stream.<br>
  The category to which it will change depends on the program you are running.</h3>
  <br>

<img src="https://github.com/stevo-ko/Category_Switcher/blob/main/Readme/Category%20Switcher.png" width="700" height="532">

</div>

<h2>✨ Features ✨</h2>

- :mag: **Auto category search**: Detects if a program is started and searches for the matching category
- :arrows_counterclockwise: **Auto category change**: Sends the category as an argument to **Streamer.bot** and that changes it.
- :speech_balloon: **Just Chatting**: If the programm closes the category will auto change back to Just Chatting.
- :file_cabinet: **Local Database**: Matched categories are saved to a local database, to prevent calling Twitch API everytime.
- :globe_with_meridians: **Plattforms**: Twitch and Kick(experimental) are supported at the moment.
- <img src="https://playnite.link/applogo.png" alt="Playnite" width="20" height="20"> **Playnite Integration:** Integration is made possible with the Addon [Running Game To Json](https://playnite.link/addons.html#7ad03f78-50f9-40d5-a7a3-cac5776e5482). More info in the Install Instructions below.

:pencil: **Info**: Detection is based on the folder name in the path of the opened program.

---


### :scroll: **Changelog** :scroll:
[**Changelog**](Changelog.md)

---

### :shield: **VirusTotal Scan** :shield:

| File | Description | Link |
|------|-------------|------|
| Exe File | The exe is just the repacked Python file with PyInstaller. <br>Sadly, this approach will never be fully unflagged. | [View on VirusTotal](https://www.virustotal.com/gui/file/a9ab55b027f11090ca2620af13858f031a2f41ea7dcae5e7ed6a3aa8debbdf72) |
| Python Source | Original Python source code. | [View on VirusTotal](https://www.virustotal.com/gui/file/ae0390bd8cc30ed101fe879660300f31e9357d8bbb59bd586fd7cf043c3eca68) |


<details>
<summary><h1><strong>🇬🇧 English Install Instructions</strong></h1></summary>

### :rocket: **Installation** :rocket:

- Download the **latest** release.
- Extract **Category_Switcher.zip**
- Import the action to **Streamer.bot** with the import code inside **Category_Switcher.stevo** or using the file itself.
- Go to **Streamer.bot → Servers/Clients → HTTP Server**.
- Ensure the **HTTP server** is enabled and started, you can change port and adress as you like before starting the server.


<div align="center">
<img src="https://github.com/stevo-ko/Category_Switcher/blob/main/Readme/Http%20Server.png" width="1609" height="908">
</div>
<br>

- Change the path to the exe in the Action **Open Category Switcher** , also change the Working Directory to the exe dir.

<div align="center">
<img src="https://github.com/stevo-ko/Category_Switcher/blob/main/Readme/Edit%20Sub%20Action.png" width="400" height="407">
</div>
<br>

- Go to the imported Action "[STEVO] Settingsmenu" right click on the first Trigger and click Test Trigger, or alternative default hotkey CTRL+Y (you can change that)
- Wait a few seconds till the settings menu opens
<div align="center">
<img src="https://github.com/stevo-ko/Category_Switcher/blob/main/Readme/Main%20Settingsmenu.png" width="400" height="500">
</div>
<br>

- Go to Game Root Folders check if the default Paths are sufficient, if not toggle the togglebutton to ON and press Add, you will get an Popup where you can chose a Folder.
- If you made all changes to your liking press the Save button.
- Category Switcher is already running and you can test it out and hopefully be happy with it.
<h2>Done ✅</h2>  


- If there is something wrong check the FAQ down below, writen an Issue here or contact me on the Streamer.bot Server in the thread.

<details>
<summary><h2><strong><img src="https://playnite.link/applogo.png" alt="Playnite" width="32" height="32"> Playnite Install Instructions</strong></h2></summary>

- Download and Install Playnite from [Playnite.link](https://playnite.link/download)
- Open Playnite and go to **Add-ons → Extensions → Generic** and install the **Running Game To Json** Addon.
- You can find the Addon also [here](https://playnite.link/addons.html#7ad03f78-50f9-40d5-a7a3-cac5776e5482)
- You can also install the Addon with that link:  
  `playnite://playnite/installaddon/7ad03f78-50f9-40d5-a7a3-cac5776e5482`
- After installing you just need to enable Playnite in the Settings of the Category Switcher and you are good to go.

</details>
</details>

---

<details>
<summary><h1><strong>🇩🇪 Deutsche Installationsanleitung</strong></h1></summary>
  
### :rocket: **Installation** :rocket:

- Lade das **neueste Release** herunter
- Entpacke **Category_Switcher.zip**.
- Importiere die Action in **Streamer.bot** mithilfe des Import-Codes in **Category_Switcher.stevo** oder über die Datei selbst.   
- Gehe zu **Streamer.bot → Servers/Clients → HTTP Server**. 
- Stelle sicher, dass der **HTTP-Server** aktiviert und gestartet ist. Du kannst den Port und die Adresse nach Belieben ändern, bevor du den Server startest. 

<div align="center">
<img src="https://github.com/stevo-ko/Category_Switcher/blob/main/Readme/Http%20Server.png" width="1609" height="908">
</div>
<br>

- Ändere in der Action **Open Category Switcher** den Pfad zur `.exe` und passe auch das Arbeitsverzeichnis auf den Ordner der `.exe` an.  

<div align="center">
<img src="https://github.com/stevo-ko/Category_Switcher/blob/main/Readme/Edit%20Sub%20Action.png" width="400" height="407">
</div>
<br>

- Gehe zur importierten Action **"[STEVO] Settingsmenu"**, klicke mit Rechtsklick auf den ersten Trigger und wähle **Test Trigger**, oder nutze alternativ das Standard-Hotkey **CTRL+Y** (dies kannst du auch ändern).  
- Warte ein paar Sekunden, bis sich das Einstellungsmenü öffnet.  

<div align="center">
<img src="https://github.com/stevo-ko/Category_Switcher/blob/main/Readme/Main%20Settingsmenu_de.png" width="400" height="500">
</div>
<br>

- Gehe zu **Spiele-Hauptordner** und prüfe, ob die Standard-Pfade ausreichen. Wenn nicht, schalte den Toggle-Button auf **ON** und klicke auf **Hinzufügen**. Es öffnet sich ein Popup, in dem du einen Ordner auswählen kannst.  
- Wenn du alle Änderungen nach deinen Wünschen vorgenommen hast, klicke auf **Speichern**.  
- Der Category Switcher läuft nun bereits – du kannst ihn direkt testen und hoffentlich Freude daran haben.  

<h2>Fertig ✅</h2>  

- Falls etwas nicht funktioniert, schau dir die **FAQ** unten an, erstelle ein Issue hier oder kontaktiere mich auf dem **Streamer.bot Server** im Thread.  
 
<details>
<summary><h2><strong><img src="https://playnite.link/applogo.png" alt="Playnite" width="32" height="32"> Playnite Installationsanleitung</strong></h2></summary>

- Lade **Playnite** von [Playnite.link](https://playnite.link/download) herunter und installiere es.  
- Öffne **Playnite** und gehe zu **Add-ons → Erweiterungen → Allgemein**, und installiere das Add-on **Running Game To Json**.  
- Du findest das Add-on auch [hier](https://playnite.link/addons.html#7ad03f78-50f9-40d5-a7a3-cac5776e5482).  
- Alternativ kannst du das Add-on auch direkt über diesen Link installieren:  
  `playnite://playnite/installaddon/7ad03f78-50f9-40d5-a7a3-cac5776e5482`  
- Nach der Installation musst du nur noch **Playnite** in den **Einstellungen des Category Switchers** aktivieren – und schon bist du startklar.

</details>
</details>

---

<details>
<summary><h1><strong>❓ FAQ</strong></h1></summary>

<h2>EN</h2>

<details><summary style="font-size: 1.3em; font-weight: bold;">Q: Do I need admin rights?</summary>
<br>

**A:** Apart from excluding the EXE from your antivirus, admin rights are not required.
</details>

<details><summary style="font-size: 1.3em; font-weight: bold;">Q: How can i get a Game or Program fixed, cause it does not get the right category?</summary>
<br>
<strong>A:</strong>  Please provide the following details: 

- 🎮 **Game name**  
- 📂 **Full path** to the game's `.exe` file  
</details>

<details><summary style="font-size: 1.3em; font-weight: bold;"> Q: How can i manually add a Game or program so it will change the category? </summary>
<br>

**A:** You need to add the game manually in the game_data.json using the following format:



```json
{
    "Game": "Example",
    "Path": "C:\\Example\\Example\\Example.exe",
    "Twitch Category Name": "Example",
    "Twitch Category ID": "123456",
    "Twitch Box Art": "https://static-cdn.jtvnw.net/ttv-boxart/123456_IGDB-285x380.jpg",
    "Kick Category Name": "Example",
    "Kick Category ID": "",
    "Kick Thumbnail": ""
}
```

- **Game** needs to match the Found Name of the Game, please read the Info in the first Post
- **Path** is not needed for the program to work correctly but if wanted write it down
- **Twitch Category Name** , **ID** , **Kick Category Name** and **Kick Category ID** should be fairly self describing, needed are only the Name on both
- **Box Art** is also not needed for the program to work correctly
- Attention If you insert it at the bottom of the json you need to add " , " after the " } " bracket before your game

<strong>It is important to have a double \ between each part of the path for it to be a correct json format</strong>

</details>

<h2>DE</h2>

<details><summary style="font-size: 1.3em; font-weight: bold;">Q: Benötige ich Admin-Rechte?</summary>
<br>

**A:** Abgesehen davon, die EXE von deinem Antivirus auszuschließen, werden keine Admin-Rechte benötigt.
</details>

<details><summary style="font-size: 1.3em; font-weight: bold;">Q: Wie kann ich ein Game oder Programm beheben lassen, wenn es nicht in die richtige Kategorie eingeordnet wird?</summary>
<br>
<strong>A:</strong>  Bitte stelle folgende Details bereit: 

- 🎮 **Game name**  
- 📂 **Full path** zur `.exe`-Datei des Spiels  
</details>

<details><summary style="font-size: 1.3em; font-weight: bold;">Q: Wie kann ich ein Game oder Programm manuell hinzufügen, damit es die Kategorie ändert?</summary>
<br>

**A:** Du musst das Game manuell in die game_data.json eintragen, und zwar im folgenden Format:

```json
{
    "Game": "Example",
    "Path": "C:\\Example\\Example\\Example.exe",
    "Twitch Category Name": "Example",
    "Twitch Category ID": "123456",
    "Twitch Box Art": "https://static-cdn.jtvnw.net/ttv-boxart/123456_IGDB-285x380.jpg",
    "Kick Category Name": "Example",
    "Kick Category ID": "",
    "Kick Thumbnail": ""
}
```


- **Game** muss mit dem Found Name des Games übereinstimmen, bitte dazu die Info im ersten Post lesen
- **Path** wird für die Funktion des Programms nicht benötigt, kann aber eingetragen werden, wenn gewünscht
- **Twitch Category Name** , **ID** , **Kick Category Name** und **Kick Category ID** sind selbsterklärend, benötigt wird aber nur der Name bei beidem
- **Box Art** wird für die Funktion des Programms ebenfalls nicht benötigt
- Achtung: Wenn du den Eintrag am Ende der json einfügst, musst du nach der schließenden " } " Klammer ein " , " setzen, bevor dein Game folgt

<strong>Wichtig ist, dass zwischen jedem Teil des Pfades ein doppelter \ stehen muss, damit es ein korrektes json-Format ist</strong>


</details>

</details>

---


<div align="center">

<h1> <strong>End Note 📝 </strong></h1>
</div>

Since the program populates a local database, **you can contribute** to a central database!  
Share your **game_data.json** after some time of use, or if you're feeling adventurous, start every game you have once! 🎮💾

🔒 Privacy Tip: If you don’t want to expose your paths, set **Censor Mode** to true in config.json and run the program once. Then you will get an censored game_data.json to share 🔧✨

If you encounter any issues or have questions, feel free to reach out! 🚀  

---

<details><summary style="font-size: 1.3em; font-weight: bold;"><h2>Credits</h2></summary>

Base GUI Code from [MustachedManiac](https://mustachedmaniac.com/)
<br>
Icons from [Icons8](https://icons8.com/)
</details>
