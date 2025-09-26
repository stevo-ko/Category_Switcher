<div align="center">
  <img src="https://github.com/stevo-ko/Category_Switcher/blob/main/Release%20EXE/_internal/icon.ico" width="100" height="100">
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

:pencil: **Info**: Detection is based on the folder name in the path of the opened program.

---


### :scroll: **Changelog** :scroll:
[**Changelog**](Changelog.md)

---

### :shield: **VirusTotal Scan** :shield:

| File | Description | Link |
|------|-------------|------|
| Exe File | The exe is just the repacked Python file with PyInstaller. <br>Sadly, this approach will never be fully unflagged. | [View on VirusTotal](https://www.virustotal.com/gui/file/077f0879be70aa72b42f4a5defd53a4683945fffa396cf3cfc06ef2c62c0fd21/detection) |
| Python Source | Original Python source code. | [View on VirusTotal](https://www.virustotal.com/gui/file/160d23391633a3df0a92eb42f766f66c5f329d56ddec0fc56791ed55e8428b92) |


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

---

- Falls etwas nicht funktioniert, schau dir die **FAQ** unten an, erstelle ein Issue hier oder kontaktiere mich auf dem **Streamer.bot Server** im Thread.  
 



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