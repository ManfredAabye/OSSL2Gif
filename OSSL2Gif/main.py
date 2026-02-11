
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

LANGUAGES = ['de', 'en', 'fr', 'es']

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
        self.root.geometry("1280x1050")
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
        self.status_group.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(2,8)) # Status Gruppe Gruppenpositionierung?
        self.status = ttk.Label(self.status_group, text=tr('ready', self.lang) or "Bereit", anchor="w")
        self.status.pack(fill=tk.X)

        # --- Datei-Gruppe ist die vorletzte Gruppe im Programmfenster ---
        self.file_group = ttk.LabelFrame(main, text=tr('file', self.lang) or "Datei")
        self.file_group.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(2,2))
        self.load_btn = ttk.Button(self.file_group, text=tr('load_gif', self.lang) or "GIF laden", command=self.load_gif)
        self.load_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.save_gif_btn = ttk.Button(self.file_group, text=tr('save_gif', self.lang) or "GIF speichern", command=self.save_gif)
        self.save_gif_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.save_texture_btn = ttk.Button(self.file_group, text=tr('save_texture', self.lang) or "Textur speichern", command=self.save_texture)
        self.save_texture_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.export_lsl_btn = ttk.Button(self.file_group, text=tr('export_lsl', self.lang) or "LSL exportieren", command=self.export_lsl)
        self.export_lsl_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # --- Master Einstellungen ---
        self.master_group = ttk.LabelFrame(main, text=tr('master_settings', self.lang) or "Master Einstellungen")
        self.master_group.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(8,2)) # Master Einstellung Gruppenpositionierung?
        # Bildgröße
        size_frame = ttk.Frame(self.master_group)
        size_frame.pack(side=tk.LEFT, padx=5)
        self.size_label = ttk.Label(size_frame, text="Bildgröße:")
        self.size_label.pack(side=tk.LEFT)
        self.width_var = tk.IntVar(value=self.image_width)
        self.height_var = tk.IntVar(value=self.image_height)
        self.width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=5)
        self.width_entry.pack(side=tk.LEFT, padx=2)
        self.height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=5)
        self.height_entry.pack(side=tk.LEFT, padx=2)
        self.width_entry.bind('<FocusOut>', lambda e: self.update_previews()) # Bildgröße-Änderung automatisch Vorschau aktualisieren
        self.height_entry.bind('<FocusOut>', lambda e: self.update_previews()) # Bildgröße-Änderung automatisch Vorschau aktualisieren
        # Randlos-Checkbox
        self.borderless_var = tk.IntVar(value=0)
        self.borderless_var.trace_add('write', lambda *args: self.update_previews()) # Randlos-Änderung automatisch Vorschau aktualisieren
        self.borderless_chk = ttk.Checkbutton(self.master_group, text=tr('borderless', self.lang) or "", variable=self.borderless_var, command=self.update_previews)
        self.borderless_chk.pack(side=tk.LEFT, padx=10)
        # Clear Button
        self.clear_btn = ttk.Button(size_frame, text=tr('clear', self.lang) or "", command=self.clear_texture)
        self.clear_btn.pack(side=tk.LEFT, padx=8)
        # Sprache
        lang_frame = ttk.Frame(self.master_group)
        lang_frame.pack(side=tk.LEFT, padx=15)
        self.lang_label = ttk.Label(lang_frame, text=tr('language', self.lang) or "")
        self.lang_label.pack(side=tk.LEFT)
        self.lang_var = tk.StringVar(value=self.lang)
        self.lang_combo = ttk.Combobox(lang_frame, values=LANGUAGES, textvariable=self.lang_var, width=6, state="readonly")
        self.lang_combo.pack(side=tk.LEFT)
        self.lang_combo.bind("<<ComboboxSelected>>", self.change_language)
        # Play Button
        self.playing = False
        self.play_btn = ttk.Button(self.master_group, text=tr('play', self.lang) or "", command=self.toggle_play)
        self.play_btn.pack(side=tk.LEFT, padx=8)
        # Bildnummer-Auswahl und Add-Button
        self.frame_select_var = tk.IntVar(value=0)
        self.frame_select_spin = ttk.Spinbox(self.master_group, from_=0, to=0, textvariable=self.frame_select_var, width=5, state="readonly")
        self.frame_select_spin.pack(side=tk.LEFT, padx=2)
        self.add_frame_btn = ttk.Button(self.master_group, text=tr('add_frame', self.lang) or "", command=self.add_selected_frame_to_texture)
        self.add_frame_btn.pack(side=tk.LEFT, padx=2)

        
    def add_selected_frame_to_texture(self):
        # Einzelbild am Ende der Textur hinzufügen
        idx = self.frame_select_var.get()
        if not self.gif_frames or idx < 0 or idx >= len(self.gif_frames):
            messagebox.showerror("Fehler", "Ungültige Bildnummer.")
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


    def toggle_play(self):
        self.playing = not self.playing
        self.play_btn.config(text=(tr('pause', self.lang) or "") if self.playing else (tr('play', self.lang) or ""))
        if self.playing:
            self.start_animation()


    def start_animation(self):
        if not self.playing or not self.gif_frames:
            return
        self.current_frame = (self.current_frame + 1) % self.frame_count
        self.show_gif_frame()
        # Versuche Delay aus GIF zu lesen, sonst Standard 100ms
        delay = 100
        if self.gif_image is not None and hasattr(self.gif_image, 'info') and 'duration' in self.gif_image.info:
            try:
                delay = int(self.gif_image.info['duration'])
            except Exception:
                delay = 100
        self.root.after(delay, self.start_animation)


    def create_effects_panel(self, parent, prefix):
        frame = ttk.LabelFrame(parent, text=tr(f'{prefix}_settings', self.lang) or "")
        self.__dict__[f'{prefix}_grayscale'] = tk.IntVar()
        self.__dict__[f'{prefix}_sharpen'] = tk.IntVar()
        self.__dict__[f'{prefix}_blur'] = tk.IntVar()
        self.__dict__[f'{prefix}_transparency'] = tk.IntVar()
        self.__dict__[f'{prefix}_sharpen_value'] = tk.DoubleVar(value=1.0)
        self.__dict__[f'{prefix}_blur_value'] = tk.DoubleVar(value=0.0)
        ttk.Checkbutton(frame, text=tr('effect_grayscale', self.lang) or "", variable=self.__dict__[f'{prefix}_grayscale'], command=self.update_previews).pack(anchor="w")
        # Schärfen
        sharpen_row = ttk.Frame(frame)
        sharpen_row.pack(fill=tk.X, pady=1)
        ttk.Checkbutton(sharpen_row, text=tr('effect_sharpen', self.lang) or "", variable=self.__dict__[f'{prefix}_sharpen'], command=self.update_previews).pack(side=tk.LEFT)
        ttk.Scale(sharpen_row, from_=0.5, to=5.0, orient=tk.HORIZONTAL, variable=self.__dict__[f'{prefix}_sharpen_value'], command=lambda e: self.update_previews(), length=200).pack(side=tk.LEFT, padx=5)
        # Weichzeichnen
        blur_row = ttk.Frame(frame)
        blur_row.pack(fill=tk.X, pady=1)
        ttk.Checkbutton(blur_row, text=tr('effect_blur', self.lang) or "", variable=self.__dict__[f'{prefix}_blur'], command=self.update_previews).pack(side=tk.LEFT)
        ttk.Scale(blur_row, from_=0.0, to=10.0, orient=tk.HORIZONTAL, variable=self.__dict__[f'{prefix}_blur_value'], command=lambda e: self.update_previews(), length=200).pack(side=tk.LEFT, padx=5)
        # Transparenz
        ttk.Checkbutton(frame, text=tr('effect_transparency', self.lang) or "", variable=self.__dict__[f'{prefix}_transparency'], command=self.update_previews).pack(anchor="w")
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
            # Nur Checkbuttons direkt updaten, keine Slider/Frames
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
            # Transparenz-Checkbutton
            if idx < len(children) and isinstance(children[idx], ttk.Checkbutton):
                children[idx].config(text=tr('effect_transparency', l) or "")


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
        self.play_btn.config(text="▶")
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
        sheet = Image.new("RGBA", (tex_w, tex_h), (0,0,0,0))
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
            # Rechts
            bbox = sheet.getbbox()
            if bbox:
                sheet = sheet.crop(bbox)
        self.texture_image = sheet
        preview = sheet.copy()
        # Canvas-Größe bestimmen
        self.texture_canvas.update_idletasks()
        canvas_w = self.texture_canvas.winfo_width()
        canvas_h = self.texture_canvas.winfo_height()
        if canvas_w < 10 or canvas_h < 10:
            canvas_w, canvas_h = 256, 256
        preview = preview.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(preview)
        self._texture_img_ref = img
        self.texture_canvas.config(image=img)


    def update_previews(self):
        import threading
        def worker():
            self.show_gif_frame()
            self.show_texture()
        threading.Thread(target=worker, daemon=True).start()


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
            alpha = img.split()[-1].point(lambda p: p//2)
            img.putalpha(alpha)
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
            frames[0].save(file, save_all=True, append_images=frames[1:], loop=0, duration=100)
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
        # Geschwindigkeit als '10;0' statt '10.0' im Dateinamen
        speed = "10;0"
        file = filedialog.asksaveasfilename(defaultextension=".png", initialfile=f"{name};{tiles_x};{tiles_y};{speed}.png", filetypes=[("PNG", "*.png"), ("JPG", "*.jpg"), ("BMP", "*.bmp")])
        if not file:
            return
        ext = file.split('.')[-1].lower()
        fmt = {"png": "PNG", "jpg": "JPEG", "jpeg": "JPEG", "bmp": "BMP"}.get(ext, "PNG")
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
