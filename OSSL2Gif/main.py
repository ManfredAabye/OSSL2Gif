# OSSL2Gif - Ein Tool zum Konvertieren von GIF-Animationen in Texturen für OpenSimulator, Second Life und andere.
# Version 1.0.6 © 2025 by Manfred Zainhofer

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import math
from translations import tr

try:
    import ttkbootstrap as tb
    THEME_AVAILABLE = True
except ImportError:
    tb = None
    THEME_AVAILABLE = False
    import ctypes
    import locale

    def get_keyboard_layout():
        # Windows-spezifisch: Tastaturlayout ermitteln
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        hWnd = user32.GetForegroundWindow()
        thread_id = user32.GetWindowThreadProcessId(hWnd, 0)
        klid = user32.GetKeyboardLayout(thread_id)
        # Die unteren 16 Bit enthalten die Sprachkennung (LANGID)
        lid = klid & 0xFFFF
        # Sprachcode (z.B. 0x407 = Deutsch, 0x409 = Englisch)
        lang_map = {
            0x407: 'de',
            0x409: 'en',
            0x40c: 'fr',
            0x410: 'it',
            0x419: 'ru',
            0x40a: 'es',
            0x413: 'nl',
            0x41d: 'se',
            0x415: 'pl',
            0x816: 'pt'
            # Weitere Codes nach Bedarf ergänzen
        }
        return lang_map.get(lid, f'unknown({lid})')

    def get_system_language():
        # Systemweite Sprache ermitteln
        lang, _ = locale.getdefaultlocale()
        return lang

    # Voreinstellungen setzen
    DEFAULT_KEYBOARD_LAYOUT = get_keyboard_layout()
    DEFAULT_LANGUAGE = get_system_language()

    print(f"Tastaturlayout erkannt: {DEFAULT_KEYBOARD_LAYOUT}")
    print(f"Systemsprache erkannt: {DEFAULT_LANGUAGE}")

LANGUAGES = ['de', 'en', 'fr', 'es', 'it', 'ru', 'nl', 'se', 'pl', 'pt']

class ModernApp:
    def __init__(self, root):
        self.root = root
        self.lang = 'de'
        self.gif_image = None
        self.gif_frames = []
        self.texture_image = None
        self.frame_count = 0
        self.current_frame = 0
        self.timer = None
        self.image_width = 2048
        self.image_height = 2048
        self.root.title("OSSL2Gif")
        self.root.geometry("1500x1300")
        try:
            self.root.iconbitmap("icon.ico")
        except Exception:
            pass  # Icon laden ignorieren, falls Datei fehlt oder Fehler
        if THEME_AVAILABLE and tb is not None:
            tb.Style("superhero")
        self.build_layout()
        self.update_language()

    def build_layout(self):

        # Haupt-Layout: 2 Spalten, unten Einstellungen
        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True)
        content = ttk.Frame(main)
        content.pack(fill=tk.BOTH, expand=True)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        # Linke Seite: GIF
        left = ttk.Frame(content)
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.gif_label = ttk.Label(left, text="GIF-Vorschau", font=("Segoe UI", 12, "bold"))
        self.gif_label.pack(pady=(0,5))
        self.gif_canvas = tk.Label(left, bg="#222", width=40, height=16, relief=tk.SUNKEN)
        self.gif_canvas.pack(fill=tk.BOTH, expand=True)
        self.gif_settings = self.create_effects_panel(left, prefix="gif")
        self.gif_settings.pack(fill=tk.X, pady=10)

        # Rechte Seite: Textur
        right = ttk.Frame(content)
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.texture_label = ttk.Label(right, text="Textur-Vorschau", font=("Segoe UI", 12, "bold"))
        self.texture_label.pack(pady=(0,5))
        self.texture_canvas = tk.Label(right, bg="#222", width=40, height=16, relief=tk.SUNKEN)
        self.texture_canvas.pack(fill=tk.BOTH, expand=True)
        self.texture_settings = self.create_effects_panel(right, prefix="texture")
        self.texture_settings.pack(fill=tk.X, pady=10)

        # --- Status-Gruppe ist die letzte Gruppe im Programmfenster ---
        self.status_group = ttk.LabelFrame(main, text=tr('status', self.lang) or "Status")
        self.status_group.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(12,8)) # Status Gruppe Gruppenpositionierung?
        self.status = ttk.Label(self.status_group, text=tr('ready', self.lang) or "Bereit", anchor="w")
        self.status.pack(fill=tk.X)

        # --- Datei-Gruppe ist die vorletzte Gruppe im Programmfenster ---
        self.file_group = ttk.LabelFrame(main, text=tr('file', self.lang) or "Datei")
        self.file_group.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(12,2))
        # Exportformat Combobox jetzt in Datei-Gruppe
        export_format_frame = ttk.Frame(self.file_group)
        export_format_frame.pack(side=tk.LEFT, padx=15)
        self.export_format_label = ttk.Label(export_format_frame, text=tr('export_format', self.lang) or "Exportformat:")
        self.export_format_label.pack(side=tk.LEFT)
        self.export_format_var = tk.StringVar(value="PNG")
        self.export_format_combo = ttk.Combobox(export_format_frame, values=["PNG", "JPG", "BMP"], textvariable=self.export_format_var, width=5, state="readonly")
        self.export_format_combo.pack(side=tk.LEFT)
        # Datei-Buttons: Laden, Speichern, Exportieren, Clear
        if THEME_AVAILABLE and tb is not None:
            self.load_btn = tb.Button(self.file_group, text=tr('load_gif', self.lang) or "GIF laden", command=self.load_gif, bootstyle="success")
        else:
            self.load_btn = tk.Button(self.file_group, text=tr('load_gif', self.lang) or "GIF laden", command=self.load_gif, bg="#4CAF50", fg="white", activebackground="#388E3C", activeforeground="white")
        self.load_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.save_gif_btn = ttk.Button(self.file_group, text=tr('save_gif', self.lang) or "GIF speichern", command=self.save_gif)
        self.save_gif_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.save_texture_btn = ttk.Button(self.file_group, text=tr('save_texture', self.lang) or "Textur speichern", command=self.save_texture)
        self.save_texture_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.export_lsl_btn = ttk.Button(self.file_group, text=tr('export_lsl', self.lang) or "LSL exportieren", command=self.export_lsl)
        self.export_lsl_btn.pack(side=tk.LEFT, padx=2, pady=2)
        # Clear Button
        if THEME_AVAILABLE and tb is not None:
            style = tb.Style()
            style.configure("RedClear.TButton", background="#e53935", foreground="white")
            self.clear_btn = tb.Button(self.file_group, text=tr('clear', self.lang) or "", command=self.clear_texture, style="RedClear.TButton")
        else:
            self.clear_btn = tk.Button(self.file_group, text=tr('clear', self.lang) or "", command=self.clear_texture, bg="#e53935", fg="white", activebackground="#b71c1c", activeforeground="white")
        self.clear_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # --- Media Gruppe (vor Master Einstellungen) ---
        self.media_group = ttk.LabelFrame(main, text="Media")
        self.media_group.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(12,2))
        media_row = ttk.Frame(self.media_group)
        media_row.pack(fill=tk.X)
        self.playing = False
        # Media Control Buttons: Rückwärts, Pause, Play, Stop, Vorwärts
        if THEME_AVAILABLE and tb is not None:
            # Eigene Styles für Pastellfarben anlegen
            style = tb.Style()
            style.configure("PastellPrev.TButton", background="#B39DDB", foreground="black")
            style.configure("PastellPause.TButton", background="#90CAF9", foreground="black")
            style.configure("PastellPlay.TButton", background="#A5D6A7", foreground="black")
            style.configure("PastellStop.TButton", background="#EF9A9A", foreground="black")
            style.configure("PastellNext.TButton", background="#FFF59D", foreground="black")
            self.prev_btn = tb.Button(media_row, text="⏮", command=self.step_backward, style="PastellPrev.TButton")
            self.pause_btn = tb.Button(media_row, text="⏸", command=self.pause_animation, style="PastellPause.TButton")
            self.play_btn = tb.Button(media_row, text="▶", command=self.start_animation, style="PastellPlay.TButton")
            self.stop_btn = tb.Button(media_row, text="⏹", command=self.stop_animation, style="PastellStop.TButton")
            self.next_btn = tb.Button(media_row, text="⏭", command=self.step_forward, style="PastellNext.TButton")
        else:
            self.prev_btn = tk.Button(media_row, text="⏮", command=self.step_backward, bg="#B39DDB", fg="black", activebackground="#D1C4E9", activeforeground="black")
            self.pause_btn = tk.Button(media_row, text="⏸", command=self.pause_animation, bg="#90CAF9", fg="black", activebackground="#BBDEFB", activeforeground="black")
            self.play_btn = tk.Button(media_row, text="▶", command=self.start_animation, bg="#A5D6A7", fg="black", activebackground="#C8E6C9", activeforeground="black")
            self.stop_btn = tk.Button(media_row, text="⏹", command=self.stop_animation, bg="#EF9A9A", fg="black", activebackground="#FFCDD2", activeforeground="black")
            self.next_btn = tk.Button(media_row, text="⏭", command=self.step_forward, bg="#FFF59D", fg="black", activebackground="#FFF9C4", activeforeground="black")
        self.prev_btn.pack(side=tk.LEFT, padx=4)
        self.pause_btn.pack(side=tk.LEFT, padx=4)
        self.play_btn.pack(side=tk.LEFT, padx=4)
        self.stop_btn.pack(side=tk.LEFT, padx=4)
        self.next_btn.pack(side=tk.LEFT, padx=4)

        # --- Master Einstellungen ---
        self.master_group = ttk.LabelFrame(main, text=tr('master_settings', self.lang) or "Master Einstellungen")
        self.master_group.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(12,2))
        # Zeile 1
        master_row1 = ttk.Frame(self.master_group)
        master_row1.pack(fill=tk.X)
        # Bildgröße
        # Pastellfarben für Master-Einstellungen
        pastel_master = {
            'size':        "#01988B", # Türkis
            'bg':          "#AF9E03", # Gelb
            'borderless':  "#FE0090", # Rosa
            'framerate':   "#008AFB", # Blau
            'lang':        '#B39DDB', # Lila
            'maxframes':   "#00E308", # Grün
            'reset':       "#EA5151", # Rot
        }

        size_frame = ttk.Frame(master_row1)
        size_frame.pack(side=tk.LEFT, padx=5)
        self.size_label = ttk.Label(size_frame, text="Bildgröße:", background="#e0f7fa", foreground="black", relief=tk.FLAT, borderwidth=1, width=14, anchor="center", font=("Segoe UI", 10))
        self.size_label.pack(side=tk.LEFT, padx=4, pady=4, ipady=6)
        self.width_var = tk.IntVar(value=self.image_width)
        self.height_var = tk.IntVar(value=self.image_height)
        self.width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=5)
        self.width_entry.pack(side=tk.LEFT, padx=2)
        self.height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=5)
        self.height_entry.pack(side=tk.LEFT, padx=2)
        self.width_entry.bind('<FocusOut>', lambda e: self.update_previews())
        self.height_entry.bind('<FocusOut>', lambda e: self.update_previews())

        # Hintergrundfarbe für Textur/GIF
        self.bg_color = "#00000000"
        self.bg_box_color = "#000000"
        bg_frame = ttk.Frame(master_row1)
        bg_frame.pack(side=tk.LEFT, padx=15)
        self.bg_label = ttk.Label(bg_frame, text=tr('bg_color', self.lang) or "Hintergrundfarbe:", background="#fff9c4", foreground="black", relief=tk.FLAT, borderwidth=1, width=18, anchor="center", font=("Segoe UI", 10))
        self.bg_label.pack(side=tk.LEFT, padx=4, pady=4, ipady=6)
        self.bg_color_box = tk.Label(bg_frame, width=3, relief=tk.SUNKEN, bg=self.bg_box_color, cursor="hand2")
        self.bg_color_box.pack(side=tk.LEFT, padx=2)
        self.bg_color_box.bind("<Button-1>", self.choose_bg_color)

        # Randlos-Checkbox
        self.borderless_var = tk.IntVar(value=0)
        self.borderless_var.trace_add('write', lambda *args: self.update_previews())
        self.borderless_chk = ttk.Checkbutton(master_row1, text=tr('borderless', self.lang) or "", variable=self.borderless_var, command=self.update_previews)
        self.borderless_chk.pack(side=tk.LEFT, padx=10)
        try:
            self.borderless_chk.configure(style="PastellBorderless.TCheckbutton")
            style = ttk.Style()
            style.configure("PastellBorderless.TCheckbutton", background=pastel_master['borderless'])
        except Exception:
            pass

        # Standard-Framerate für Textur/GIF (ms/Bild)
        self.framerate_var = tk.IntVar(value=10)
        framerate_frame = ttk.Frame(master_row1)
        framerate_frame.pack(side=tk.LEFT, padx=15)
        self.framerate_label = ttk.Label(framerate_frame, text=tr('framerate', self.lang) or "Framerate:", background="#bbdefb", foreground="black", relief=tk.FLAT, borderwidth=1, width=12, anchor="center", font=("Segoe UI", 10))
        self.framerate_label.pack(side=tk.LEFT, padx=4, pady=4, ipady=6)
        self.framerate_spin = ttk.Spinbox(framerate_frame, from_=1, to=10000, increment=1, textvariable=self.framerate_var, width=6)
        self.framerate_spin.pack(side=tk.LEFT)
        # Zeile 2
        master_row2 = ttk.Frame(self.master_group)
        master_row2.pack(fill=tk.X)
        # Sprache

        spacer = ttk.Frame(self.master_group, height=10)
        spacer.pack(fill=tk.X)
        master_row2 = ttk.Frame(self.master_group)
        master_row2.pack(fill=tk.X)

        lang_frame = ttk.Frame(master_row2)
        lang_frame.pack(side=tk.LEFT, padx=15)
        if not hasattr(self, 'lang_label'):
            self.lang_label = ttk.Label(lang_frame, text=tr('language', self.lang) or "", background="#eeec7d", foreground="black", relief=tk.FLAT, borderwidth=1, width=12, anchor="center", font=("Segoe UI", 10))
        else:
            self.lang_label.config(text=tr('language', self.lang) or "", background="#eeec7d", foreground="black", relief=tk.FLAT, borderwidth=1, width=12, anchor="center", font=("Segoe UI", 10))
        self.lang_label.pack(side=tk.LEFT, padx=4, pady=4, ipady=6)
        self.lang_var = tk.StringVar(value=self.lang)
        self.lang_combo = ttk.Combobox(lang_frame, values=LANGUAGES, textvariable=self.lang_var, width=6, state="readonly")
        self.lang_combo.pack(side=tk.LEFT)
        self.lang_combo.bind("<<ComboboxSelected>>", self.change_language)

        # Bildnummer-Auswahl und Add-Button
        self.frame_select_var = tk.IntVar(value=0)
        self.frame_select_spin = ttk.Spinbox(master_row2, from_=0, to=0, textvariable=self.frame_select_var, width=5, state="readonly")
        self.frame_select_spin.pack(side=tk.LEFT, padx=2)
        self.add_frame_btn = ttk.Button(master_row2, text=tr('add_frame', self.lang) or "", command=self.add_selected_frame_to_texture)
        self.add_frame_btn.pack(side=tk.LEFT, padx=2)

        # Maximale Bildanzahl Spinbox
        maxframes_frame = ttk.Frame(master_row2)
        maxframes_frame.pack(side=tk.LEFT, padx=15)
        self.maxframes_label = ttk.Label(maxframes_frame, text=tr('max_images', self.lang) or "Max. Bilder:", background="#c8e6c9", foreground="black", relief=tk.FLAT, borderwidth=1, width=14, anchor="center", font=("Segoe UI", 10))
        self.maxframes_label.pack(side=tk.LEFT, padx=4, pady=4, ipady=6)
        self.maxframes_var = tk.IntVar(value=64)
        self.maxframes_spin = ttk.Spinbox(maxframes_frame, from_=1, to=1024, increment=1, textvariable=self.maxframes_var, width=5, state="readonly")
        self.maxframes_spin.pack(side=tk.LEFT)
        self.maxframes_spin.bind('<FocusOut>', lambda e: self.on_maxframes_changed())
        self.maxframes_var.trace_add('write', self.on_maxframes_changed)

        # Reset-Button für alle Einstellungen
        if THEME_AVAILABLE and tb is not None:
            style = tb.Style()
            style.configure("RedReset.TButton", background="#e53935", foreground="white")
            self.reset_btn = tb.Button(master_row2, text="Reset", command=self.reset_settings, style="RedReset.TButton")
        else:
            self.reset_btn = tk.Button(master_row2, text="Reset", command=self.reset_settings, bg="#e53935", fg="white", activebackground="#b71c1c", activeforeground="white")
        self.reset_btn.pack(side=tk.LEFT, padx=8)

    def reset_settings(self):
        # Standardwerte
        self.width_var.set(2048)
        self.height_var.set(2048)
        self.bg_color = "#00000000"
        self.bg_box_color = "#000000"
        self.bg_color_box.config(bg=self.bg_box_color)
        self.borderless_var.set(0)
        self.framerate_var.set(10)
        self.export_format_var.set("PNG")
        self.maxframes_var.set(64)
        self.lang_var.set("de")
        # Effekte zurücksetzen
        for prefix in ("gif", "texture"):
            self.__dict__[f'{prefix}_grayscale'].set(0)
            self.__dict__[f'{prefix}_sharpen'].set(0)
            self.__dict__[f'{prefix}_blur'].set(0)
            self.__dict__[f'{prefix}_transparency'].set(0)
            self.__dict__[f'{prefix}_sharpen_value'].set(2.5)
            self.__dict__[f'{prefix}_blur_value'].set(3.5)
            self.__dict__[f'{prefix}_transparency_value'].set(0.5)
            # Farbintensität zurücksetzen
            self.__dict__[f'{prefix}_colorintensity'].set(0.5)
            self.__dict__[f'{prefix}_colorintensity_active'].set(0)
        self.update_language()
        self.current_frame = 0
        self.playing = False
        # GIF und Textur neu laden, falls ein GIF geladen ist
        if self.gif_image and hasattr(self.gif_image, 'filename'):
            file = self.gif_image.filename
            try:
                self.gif_image = Image.open(file)
                self.gif_frames = []
                while True:
                    self.gif_frames.append(self.gif_image.copy())
                    self.gif_image.seek(len(self.gif_frames))
            except EOFError:
                pass
            except Exception:
                self.gif_frames = []
            self.frame_count = len(self.gif_frames)
            self.current_frame = 0
            if self.gif_frames:
                self.show_gif_frame()
        else:
            self.update_previews()

    def on_maxframes_changed(self, *args):
        max_frames = self.maxframes_var.get()
        if hasattr(self, 'gif_frames') and len(self.gif_frames) > max_frames:
            removed = len(self.gif_frames) - max_frames
            self.gif_frames = self.gif_frames[:max_frames]
            self.frame_count = len(self.gif_frames)
            self.status.config(text=f"{removed} Bilder entfernt. Gesamt: {self.frame_count}")
            # Bildnummer-Spinbox updaten
            value = self.frame_select_var.get()
            self.frame_select_spin.destroy()
            self.frame_select_spin = ttk.Spinbox(self.add_frame_btn.master, from_=0, to=max(0, self.frame_count-1), textvariable=self.frame_select_var, width=5, state="readonly")
            self.frame_select_spin.pack(side=tk.LEFT, padx=2, before=self.add_frame_btn)
            self.frame_select_var.set(min(value, self.frame_count-1))
            self.update_previews()

    def choose_bg_color(self, event=None):
        from tkinter import colorchooser
        color = colorchooser.askcolor(color=self.bg_box_color, title="Hintergrundfarbe wählen")
        if color and color[1]:
            self.bg_box_color = color[1]
            # Für das Bild: Wenn Farbe volltransparent gewünscht, dann #00000000, sonst hex ohne Alpha
            if self.bg_box_color.lower() == "#000000":
                self.bg_color = "#00000000"
            else:
                self.bg_color = self.bg_box_color
            self.bg_color_box.config(bg=self.bg_box_color)
            self.update_previews()

    def add_selected_frame_to_texture(self):
        # Einzelbild am Ende der Textur hinzufügen
        idx = self.frame_select_var.get()
        if not self.gif_frames or idx < 0 or idx >= len(self.gif_frames):
            messagebox.showerror("Fehler", "Ungültige Bildnummer.")
            return
        # Prüfe maximale Bildanzahl
        max_frames = self.maxframes_var.get()
        if len(self.gif_frames) >= max_frames:
            messagebox.showerror("Fehler", f"Maximale Bildanzahl ({max_frames}) erreicht.")
            return
        # Das ausgewählte Frame ans Ende der Textur-Liste anhängen
        frame = self.gif_frames[idx].copy()
        self.gif_frames.append(frame)
        self.frame_count = len(self.gif_frames)
        # Spinbox updaten
        # Spinbox immer neu erstellen und ersetzen (maximale Kompatibilität)
        value = self.frame_select_var.get()
        self.frame_select_spin.destroy()
        self.frame_select_spin = ttk.Spinbox(self.add_frame_btn.master, from_=0, to=max(0, self.frame_count-1), textvariable=self.frame_select_var, width=5, state="readonly")
        self.frame_select_spin.pack(side=tk.LEFT, padx=2, before=self.add_frame_btn)
        self.frame_select_var.set(value)
        self.status.config(text=f"Bild {idx} hinzugefügt. Gesamt: {self.frame_count}")
        self.update_previews()



    def start_animation(self):
        if not self.gif_frames:
            return
        self.playing = True
        self._run_animation()

    def _run_animation(self):
        if not self.playing or not self.gif_frames:
            return
        self.current_frame = (self.current_frame + 1) % self.frame_count
        self.show_gif_frame()
        delay = self.framerate_var.get()
        self.root.after(delay, self._run_animation)

    def pause_animation(self):
        self.playing = False
        # Play/Pause-Button immer auf "Abspielen" (Play) setzen, auch sprachabhängig
        self.play_btn.config(text=tr('play', self.lang) or "Play ▶")

    def stop_animation(self):
        self.playing = False
        self.current_frame = 0
        self.show_gif_frame()
        # Play/Pause-Button immer auf "Abspielen" (Play) setzen, auch sprachabhängig
        self.play_btn.config(text=tr('play', self.lang) or "Play ▶")

    def step_forward(self):
        if not self.gif_frames:
            return
        self.current_frame = (self.current_frame + 1) % self.frame_count
        self.show_gif_frame()

    def step_backward(self):
        if not self.gif_frames:
            return
        self.current_frame = (self.current_frame - 1) % self.frame_count
        self.show_gif_frame()



    def create_effects_panel(self, parent, prefix):
        frame = ttk.LabelFrame(parent, text=tr(f'{prefix}_settings', self.lang) or "")
        self.__dict__[f'{prefix}_grayscale'] = tk.IntVar()
        self.__dict__[f'{prefix}_sharpen'] = tk.IntVar()
        self.__dict__[f'{prefix}_blur'] = tk.IntVar()
        self.__dict__[f'{prefix}_transparency'] = tk.IntVar()
        self.__dict__[f'{prefix}_transparency_value'] = tk.DoubleVar(value=0.5)
        self.__dict__[f'{prefix}_sharpen_value'] = tk.DoubleVar(value=2.5)
        self.__dict__[f'{prefix}_blur_value'] = tk.DoubleVar(value=3.5)
        ttk.Checkbutton(frame, text=tr('effect_grayscale', self.lang) or "", variable=self.__dict__[f'{prefix}_grayscale'], command=self.update_previews).pack(anchor="w")
        # Schärfen
        sharpen_row = ttk.Frame(frame)
        sharpen_row.pack(fill=tk.X, pady=1)
        sharpen_row.columnconfigure(0, weight=1)
        sharpen_check = ttk.Checkbutton(sharpen_row, text=tr('effect_sharpen', self.lang) or "", variable=self.__dict__[f'{prefix}_sharpen'], command=self.update_previews)
        sharpen_check.pack(side=tk.LEFT)
        sharpen_value_label = ttk.Label(sharpen_row, textvariable=self.__dict__[f'{prefix}_sharpen_value'], width=4)
        sharpen_value_label.pack(side=tk.LEFT, padx=(5,0))
        sharpen_inner = ttk.Frame(sharpen_row)
        sharpen_inner.pack(anchor="e", pady=(0,2), fill=tk.X)
        sharpen_scale = ttk.Scale(sharpen_inner, from_=0.0, to=10.0, orient=tk.HORIZONTAL, variable=self.__dict__[f'{prefix}_sharpen_value'], command=lambda e: self.update_previews(), length=375)
        sharpen_scale.pack(side=tk.RIGHT, padx=5)
        # Weichzeichnen
        blur_row = ttk.Frame(frame)
        blur_row.pack(fill=tk.X, pady=1)
        blur_row.columnconfigure(0, weight=1)
        blur_check = ttk.Checkbutton(blur_row, text=tr('effect_blur', self.lang) or "", variable=self.__dict__[f'{prefix}_blur'], command=self.update_previews)
        blur_check.pack(side=tk.LEFT)
        blur_value_label = ttk.Label(blur_row, textvariable=self.__dict__[f'{prefix}_blur_value'], width=4)
        blur_value_label.pack(side=tk.LEFT, padx=(5,0))
        blur_inner = ttk.Frame(blur_row)
        blur_inner.pack(anchor="e", pady=(0,2), fill=tk.X)
        blur_scale = ttk.Scale(blur_inner, from_=0.0, to=10.0, orient=tk.HORIZONTAL, variable=self.__dict__[f'{prefix}_blur_value'], command=lambda e: self.update_previews(), length=375)
        blur_scale.pack(side=tk.RIGHT, padx=5)
        # Transparenz
        transparency_row = ttk.Frame(frame)
        transparency_row.pack(fill=tk.X, pady=1)
        transparency_row.columnconfigure(0, weight=1)
        transparency_label = tr('effect_transparency', self.lang)
        if not transparency_label:
            transparency_label = "Transparenz"
        transparency_check = ttk.Checkbutton(transparency_row, text=transparency_label, variable=self.__dict__[f'{prefix}_transparency'], command=self.update_previews)
        transparency_check.pack(side=tk.LEFT)
        transparency_value_label = ttk.Label(transparency_row, textvariable=self.__dict__[f'{prefix}_transparency_value'], width=4)
        transparency_value_label.pack(side=tk.LEFT, padx=(5,0))
        transparency_inner = ttk.Frame(transparency_row)
        transparency_inner.pack(anchor="e", pady=(0,2), fill=tk.X)
        transparency_scale = ttk.Scale(transparency_inner, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.__dict__[f'{prefix}_transparency_value'], command=lambda e: self.update_previews(), length=375)
        transparency_scale.pack(side=tk.RIGHT, padx=5)

        # Farbintensität (Pastell <-> Kräftig) mit Checkbox
        colorint_row = ttk.Frame(frame)
        colorint_row.pack(fill=tk.X, pady=1)
        colorint_row.columnconfigure(0, weight=1)
        colorint_label = tr('effect_colorintensity', self.lang) or "Farbintensität"
        self.__dict__[f'{prefix}_colorintensity'] = tk.DoubleVar(value=0.5)
        self.__dict__[f'{prefix}_colorintensity_active'] = tk.IntVar(value=0)
        colorint_check = ttk.Checkbutton(colorint_row, text=colorint_label, variable=self.__dict__[f'{prefix}_colorintensity_active'], command=self.update_previews)
        colorint_check.pack(side=tk.LEFT)
        colorint_value_label = ttk.Label(colorint_row, textvariable=self.__dict__[f'{prefix}_colorintensity'], width=4)
        colorint_value_label.pack(side=tk.LEFT, padx=(5,0))
        colorint_inner = ttk.Frame(colorint_row)
        colorint_inner.pack(anchor="e", pady=(0,2), fill=tk.X)
        colorint_scale = ttk.Scale(colorint_inner, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.__dict__[f'{prefix}_colorintensity'], command=lambda e: self.update_previews(), length=375)
        colorint_scale.pack(side=tk.RIGHT, padx=5)
        return frame


    def update_language(self):
        l = self.lang
        self.gif_label.config(text=tr('gif_preview', l) or "")
        self.gif_settings.config(text=tr('gif_settings', l) or "")
        self.texture_label.config(text=tr('texture_preview', l) or "")
        self.texture_settings.config(text=tr('texture_settings', l) or "")
        self.size_label.config(text=tr('image_size', l) or "")
        self.lang_label.config(text=tr('language', l) or "")
        self.load_btn.config(text=tr('load_gif', l) or "")
        self.save_gif_btn.config(text=tr('save_gif', l) or "")
        self.save_texture_btn.config(text=tr('save_texture', l) or "")
        self.export_lsl_btn.config(text=tr('export_lsl', l) or "")
        self.status.config(text=tr('ready', l) or "")
        # Gruppenüberschriften
        self.master_group.config(text=tr('master_settings', l) or "")
        self.file_group.config(text=tr('file', l) or "")
        self.status_group.config(text=tr('status', l) or "")
        # Buttons
        self.clear_btn.config(text=tr('clear', l) or "")
        self.borderless_chk.config(text=tr('borderless', l) or "")
        self.play_btn.config(text=tr('play', l) if not self.playing else tr('pause', l) or "")
        self.add_frame_btn.config(text=tr('add_frame', l) or "")
        # Effekte-Labels aktualisieren
        for prefix in ("gif", "texture"):
            panel = getattr(self, f"{prefix}_settings")
            panel.config(text=tr(f'{prefix}_settings', l) or "")
            children = panel.winfo_children()
            idx = 0
            # Graustufen-Checkbutton
            if idx < len(children) and isinstance(children[idx], ttk.Checkbutton):
                children[idx].config(text=tr('effect_grayscale', l) or "")
            idx += 1
            # Schärfe-Frame (enthält Checkbutton und Slider)
            if idx < len(children):
                sharpen_row = children[idx]
                sharpen_btn = sharpen_row.winfo_children()[0]
                if isinstance(sharpen_btn, ttk.Checkbutton):
                    sharpen_btn.config(text=tr('effect_sharpen', l) or "")
            idx += 1
            # Blur-Frame (enthält Checkbutton und Slider)
            if idx < len(children):
                blur_row = children[idx]
                blur_btn = blur_row.winfo_children()[0]
                if isinstance(blur_btn, ttk.Checkbutton):
                    blur_btn.config(text=tr('effect_blur', l) or "")
            idx += 1
            # Transparenz-Frame (enthält Checkbutton und Slider)
            if idx < len(children):
                transparency_row = children[idx]
                transparency_btn = transparency_row.winfo_children()[0]
                if isinstance(transparency_btn, ttk.Checkbutton):
                    transparency_btn.config(text=tr('effect_transparency', l) or "")
            idx += 1
            # Farbintensität-Frame (enthält Checkbutton und Slider)
            if idx < len(children):
                colorint_row = children[idx]
                colorint_btn = colorint_row.winfo_children()[0]
                if isinstance(colorint_btn, ttk.Checkbutton):
                    colorint_btn.config(text=tr('effect_colorintensity', l) or "")
                    self.bg_label.config(text=tr('bg_color', l) or "Hintergrundfarbe:")
        # Neue Funktionen in Master Einstellungen
        self.framerate_label.config(text=tr('framerate', l) or "Framerate:")
        self.export_format_label.config(text=tr('export_format', l) or "Exportformat:")
        self.maxframes_label.config(text=tr('max_images', l) or "Max. Bilder:")


    def change_language(self, event=None):
        self.lang = self.lang_var.get()
        self.update_language()
        self.update_previews()


    def load_gif(self):
        file = filedialog.askopenfilename(filetypes=[("GIF", "*.gif")])
        if not file:
            return
        self.gif_image = Image.open(file)
        self.gif_frames = []
        # Clear Textur-Vorschau
        self.texture_image = None
        self.texture_canvas.config(image="")
        try:
            while True:
                self.gif_frames.append(self.gif_image.copy())
                self.gif_image.seek(len(self.gif_frames))
        except EOFError:
            pass
        self.frame_count = len(self.gif_frames)
        self.current_frame = 0
        self.playing = False
        # Play/Pause-Button immer auf "Abspielen" (Play) setzen, auch sprachabhängig
        self.play_btn.config(text=tr('play', self.lang) or "Play ▶")
        # Max. Bilder automatisch auf Frame-Anzahl setzen
        self.maxframes_var.set(self.frame_count)
        # Spinbox für Bildnummern-Auswahl updaten
        # Spinbox immer neu erstellen und ersetzen (maximale Kompatibilität)
        value = 0
        self.frame_select_spin.destroy()
        self.frame_select_spin = ttk.Spinbox(self.add_frame_btn.master, from_=0, to=max(0, self.frame_count-1), textvariable=self.frame_select_var, width=5, state="readonly")
        self.frame_select_spin.pack(side=tk.LEFT, padx=2, before=self.add_frame_btn)
        self.frame_select_var.set(value)
        self.update_previews()
        self.status.config(text=f"{tr('frame_count', self.lang)}: {self.frame_count}")


    def clear_texture(self):
        self.texture_image = None
        self.texture_canvas.config(image="")
        self.gif_image = None
        self.gif_frames = []
        self.frame_count = 0
        self.current_frame = 0
        self.gif_canvas.config(image="")
        self._gif_img_ref = None


    def show_gif_frame(self):
        if not self.gif_frames:
            self.gif_canvas.config(image="")
            self.show_texture()
            return
        frame = self.gif_frames[self.current_frame]
        # Canvas-Größe bestimmen
        self.gif_canvas.update_idletasks()
        canvas_w = self.gif_canvas.winfo_width()
        canvas_h = self.gif_canvas.winfo_height()
        # Textur-Canvas-Größe holen
        self.texture_canvas.update_idletasks()
        texture_w = self.texture_canvas.winfo_width()
        texture_h = self.texture_canvas.winfo_height()
        # Maximalgröße: Textur-Canvas
        max_w = min(canvas_w, texture_w) if texture_w > 10 else canvas_w
        max_h = min(canvas_h, texture_h) if texture_h > 10 else canvas_h
        if max_w < 10 or max_h < 10:
            max_w, max_h = 256, 256
        frame = frame.resize((max_w, max_h), Image.Resampling.LANCZOS)
        frame = self.apply_effects(frame, prefix="gif")
        img = ImageTk.PhotoImage(frame)
        self._gif_img_ref = img
        self.gif_canvas.config(image=img)
        self.show_texture()


    def show_texture(self):
        if not self.gif_frames:
            self.texture_canvas.config(image="")
            return
        import math, os
        tex_w = self.width_var.get() if self.width_var.get() > 0 else 2048
        tex_h = self.height_var.get() if self.height_var.get() > 0 else 2048
        frame_count = self.frame_count
        tiles_x = math.ceil(math.sqrt(frame_count))
        tiles_y = math.ceil(frame_count / tiles_x)
        # Kachelgröße berechnen, damit alle Tiles in tex_w x tex_h passen
        tile_w = tex_w // tiles_x
        tile_h = tex_h // tiles_y
        # Hintergrundfarbe übernehmen
        from PIL import ImageColor
        bg_rgba = (0,0,0,0)
        try:
            bg_rgba = ImageColor.getcolor(self.bg_color, "RGBA")
        except Exception:
            pass
        sheet = Image.new("RGBA", (tex_w, tex_h), bg_rgba)
        for idx, frame in enumerate(self.gif_frames):
            tx = idx % tiles_x
            ty = idx // tiles_x
            f = frame.resize((tile_w, tile_h), Image.Resampling.LANCZOS)
            f = self.apply_effects(f, prefix="texture")
            x = tx * tile_w
            y = ty * tile_h
            sheet.paste(f, (x, y))
        # Randlos: Transparente Ränder rechts/unten entfernen
        if hasattr(self, 'borderless_var') and self.borderless_var.get():
            bbox = sheet.getbbox()
            if bbox:
                sheet = sheet.crop(bbox)
        self.texture_image = sheet
        # Canvas-Größe bestimmen
        self.texture_canvas.update_idletasks()
        canvas_w = self.texture_canvas.winfo_width()
        canvas_h = self.texture_canvas.winfo_height()
        if canvas_w < 10 or canvas_h < 10:
            canvas_w, canvas_h = 256, 256
        # Vorschau immer auf Canvas-Größe skalieren, unabhängig von tex_w/tex_h
        preview = sheet.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(preview)
        self._texture_img_ref = img
        self.texture_canvas.config(image=img)


    def update_previews(self):
        self.show_gif_frame()


    def apply_effects(self, img, prefix):
        from PIL import ImageEnhance, ImageFilter
        # Graustufen
        if self.__dict__[f'{prefix}_grayscale'].get():
            img = img.convert("L").convert("RGBA")
        else:
            if img.mode != "RGBA":
                img = img.convert("RGBA")
        # Schärfen
        if self.__dict__[f'{prefix}_sharpen'].get():
            factor = self.__dict__[f'{prefix}_sharpen_value'].get()
            img = ImageEnhance.Sharpness(img).enhance(factor)
        # Blur
        if self.__dict__[f'{prefix}_blur'].get():
            radius = self.__dict__[f'{prefix}_blur_value'].get()
            if radius > 0:
                img = img.filter(ImageFilter.GaussianBlur(radius))
        # Transparenz
        if self.__dict__[f'{prefix}_transparency'].get():
            value = self.__dict__[f'{prefix}_transparency_value'].get()
            # value: 0.0 (voll transparent) bis 1.0 (keine Änderung)
            alpha = img.split()[-1].point(lambda p: int(p * value))
            img.putalpha(alpha)

        # Farbintensität (Pastell <-> Kräftig) nur wenn Checkbox aktiv
        if self.__dict__[f'{prefix}_colorintensity_active'].get():
            colorint = self.__dict__[f'{prefix}_colorintensity'].get()
            # colorint: 0.0 = Pastell, 1.0 = Kräftig, 0.5 = neutral
            if colorint != 0.5:
                if colorint < 0.5:
                    # Pastell: Interpolieren zu Weiß
                    import numpy as np
                    arr = np.array(img).astype(float)
                    factor = colorint * 2  # 0.0...1.0
                    arr[..., :3] = arr[..., :3] * factor + 255 * (1 - factor)
                    if img.mode == "RGBA" or (arr.shape[-1] == 4):
                        img = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), "RGBA")
                    else:
                        img = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), "RGB")
                else:
                    # Kräftig: Pillow-Optimierung
                    from PIL import ImageEnhance
                    # colorint 0.5...1.0 → Faktor 1.0...2.0
                    factor = 1.0 + (colorint - 0.5) * 2
                    img = ImageEnhance.Color(img).enhance(factor)
        return img


    def save_gif(self):
        if not self.gif_frames:
            messagebox.showerror("Fehler", "Kein GIF geladen.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF", "*.gif")])
        if not file:
            return
        # Speichere animiertes GIF mit Pillow
        try:
            frames = [self.apply_effects(f.resize((self.width_var.get(), self.height_var.get())), "gif") for f in self.gif_frames]
            # Framerate aus Spinbox übernehmen (ms/Bild)
            duration = self.framerate_var.get()
            frames[0].save(file, save_all=True, append_images=frames[1:], loop=0, duration=duration)
            messagebox.showinfo("Info", "GIF gespeichert.")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))


    def save_texture(self):
        if self.texture_image is None:
            messagebox.showerror("Fehler", "Keine Textur vorhanden.")
            return
        name = "texture"
        if self.gif_image and hasattr(self.gif_image, 'filename'):
            import os
            name = os.path.splitext(os.path.basename(self.gif_image.filename))[0]
        frame_count = self.frame_count
        tiles_x = math.ceil(math.sqrt(frame_count))
        tiles_y = math.ceil(frame_count / tiles_x)
        # Geschwindigkeit aus Framerate übernehmen (ms/Bild als float mit Komma)
        speed_val = self.framerate_var.get()
        # Format wie '10;0' für 10sec
        speed = f"{speed_val};0"
        # Dateiendung und Filetype passend zum gewählten Exportformat
        ext = self.export_format_var.get().lower()
        defext = f".{ext}"
        filetypes = [(ext.upper(), f"*.{ext}") for ext in ["png", "jpg", "bmp"]]
        file = filedialog.asksaveasfilename(defaultextension=defext, initialfile=f"{name};{tiles_x};{tiles_y};{speed}.{ext}", filetypes=filetypes)
        if not file:
            return
        # Exportformat aus Combobox übernehmen
        fmt = self.export_format_var.get().upper()
        if fmt == "JPG":
            fmt = "JPEG"
        try:
            img = self.texture_image
            if fmt == "JPEG":
                img = img.convert("RGB")
            img.save(file, format=fmt)
            messagebox.showinfo("Info", "Textur gespeichert.")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))


    def export_lsl(self):
        if not self.gif_frames:
            messagebox.showerror("Fehler", "Kein GIF geladen.")
            return
        import math, os
        frame_count = self.frame_count
        tiles_x = math.ceil(math.sqrt(frame_count))
        tiles_y = math.ceil(frame_count / tiles_x)
        name = "texture"
        if self.gif_image and hasattr(self.gif_image, 'filename'):
            name = os.path.splitext(os.path.basename(self.gif_image.filename))[0]
        speed = 10.0
        lsl = self.generate_lsl_script(name, tiles_x, tiles_y, speed)
        file = filedialog.asksaveasfilename(defaultextension=".lsl", initialfile=f"{name}.lsl", filetypes=[("LSL", "*.lsl"), ("Text", "*.txt")])
        if not file:
            return
        try:
            with open(file, "w", encoding="utf-8") as f:
                f.write(lsl)
            messagebox.showinfo("Info", "LSL-Skript exportiert.")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def generate_lsl_script(self, name, tiles_x, tiles_y, speed):
        return f'''// LSL Texture Animation Script\n// Generated by OSSL2Gif\n// Texture: {name};{tiles_x};{tiles_y};{speed}\n\ninteger animOn = TRUE;\nlist effects = [LOOP];\ninteger movement = 0;\ninteger face = ALL_SIDES;\ninteger sideX = {tiles_x};\ninteger sideY = {tiles_y};\nfloat start = 0.0;\nfloat length = 0.0;\nfloat speed = {speed};\n\ninitAnim() {{\n    if(animOn) {{\n        integer effectBits;\n        integer i;\n        for(i = 0; i < llGetListLength(effects); i++) {{\n            effectBits = (effectBits | llList2Integer(effects,i));\n        }}\n        integer params = (effectBits|movement);\n        llSetTextureAnim(ANIM_ON|params,face,sideX,sideY,start,length,speed);\n    }}\n    else {{\n        llSetTextureAnim(0,face,sideX,sideY,start,length,speed);\n    }}\n}}\n\nfetch() {{\n     string texture = llGetInventoryName(INVENTORY_TEXTURE,0);\n            llSetTexture(texture,face);\n            list data  = llParseString2List(texture,";",[]);\n            string X = llList2String(data,1);\n            string Y = llList2String(data,2);\n            string Z = llList2String(data,3);\n            sideX = (integer) X;\n            sideY = (integer) Y;\n            speed = (float) Z;\n            if (speed) \n                initAnim();\n}}\n\ndefault\n{{\n    state_entry()\n    {{\n        llSetTextureAnim(FALSE, face, 0, 0, 0.0, 0.0, 1.0);\n        fetch();\n    }}\n    changed(integer what)\n    {{\n        if (what & CHANGED_INVENTORY)\n        {{\n            fetch();\n        }}\n    }}\n}}\n'''


if __name__ == "__main__":
    if THEME_AVAILABLE and tb is not None:
        root = tb.Window(themename="superhero")
    else:
        root = tk.Tk()
    app = ModernApp(root)
    root.mainloop()
