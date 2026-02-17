# OSSL2Gif – Einfache GIF-zu-Textur-Umwandlung

Mit OSSL2Gif kannst du animierte GIFs einfach in Texturen für Second Life/OpenSim umwandeln – ganz ohne Programmierkenntnisse!

**⚠️ ACHTUNG: VERALTETE VERSION**  Diese Version wird von der Version **2.0.1** abgelöst und nicht weiterentwickelt. 

<img src="https://raw.githubusercontent.com/ManfredAabye/OSSL2Gif/refs/heads/main/logo003.png" alt="Project Badge" width="400">

## Voraussetzungen

- **Python 3.13**
  - Download: <https://www.python.org/downloads/>
  - Während der Installation: Haken setzen bei „Add Python to PATH“
- **pip** (wird meist mit Python installiert)
- **tkinter** (bei Python fast immer schon dabei)
- **Pillow** (für die Bildverarbeitung)
- **Optional:** Für ein moderneres Aussehen `ttkbootstrap`

## Installation – Schritt für Schritt

1. **Python installieren**
   - Lade Python 3.13 von [python.org](https://www.python.org/downloads/) herunter und installiere es.
   - Achte darauf, dass „Add Python to PATH“ aktiviert ist.

2. **Prüfen, ob Python und pip funktionieren**
   - Öffne die Eingabeaufforderung (Windows-Taste, dann „cmd“ eingeben und Enter).
   - Prüfe die Versionen:

     ```bash
     python --version
     pip --version
     ```

   - Beide Befehle sollten eine Versionsnummer anzeigen.

3. **Benötigte Pakete installieren**
   - Wechsle in den Ordner, in dem sich die Dateien befinden (z.B. `PyOSSL2Gif`).
   - Installiere Pillow (für GIFs und Bilder):

     ```bash
     pip install Pillow
     ```

   - Optional: Installiere ttkbootstrap für ein modernes Aussehen:

     ```bash
     pip install ttkbootstrap
     ```

## Starten

- Im Ordner mit der Datei `main.py` folgenden Befehl ausführen:

  ```bash
  python main.py
  ```
- Unter Release gibt es ein fertiges Programm welches unter Windows 11 erstellt wurde.

## Bedienung

1. **GIF laden:** Klicke auf „GIF laden“ und wähle eine animierte GIF-Datei aus.
2. **Vorschau:** Das GIF und die spätere Textur werden angezeigt.
3. **Effekte:** Du kannst Graustufen, Schärfe, Weichzeichnen und Transparenz einstellen.
4. **Bildgröße:** Passe die Zielgröße der Textur an.
5. **Randlos:** Entfernt überflüssige transparente Ränder.
6. **Play/Pause:** Animation abspielen oder anhalten.
7. **Bild hinzufügen:** Einzelne GIF-Frames zur Textur hinzufügen.
8. **Sprache:** Wähle die Sprache im Dropdown-Menü.
9. **Speichern:** Speichere das GIF oder die Textur als Datei.
10. **LSL exportieren:** Erzeuge ein LSL-Skript für Second Life/OpenSim.

## Tipps

- Für ein modernes Aussehen installiere `ttkbootstrap` (siehe oben).
- Die Benutzeroberfläche ist mehrsprachig (Deutsch, Englisch, Französisch, Spanisch).
- Bei Problemen: Stelle sicher, dass du Python 3.13 verwendest und alle Pakete installiert sind.

---



