import os
import pygame
import keyboard
import mouse
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import threading
import time

class SoundpadApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python Soundpad")
        self.geometry("800x500")
        self.sounds = {}
        self.current_binding = None
        self.volume = 0.7
        self.setup_ui()

        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        self.check_audio_devices()

        self.check_hotkeys_running = True
        self.hotkey_thread = threading.Thread(target=self.check_hotkeys, daemon=True)
        self.hotkey_thread.start()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def check_audio_devices(self):
        try:
            if pygame.mixer.get_init() is None:
                messagebox.showerror("Ошибка", "Аудиоустройство не найдено!")
            else:
                print("Аудиоустройство инициализировано:", pygame.mixer.get_init())
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось инициализировать аудио: {str(e)}")

    def setup_ui(self):
        toolbar = tk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        add_btn = tk.Button(toolbar, text="Добавить звук", command=self.add_sound)
        add_btn.pack(side=tk.LEFT, padx=5)

        bind_btn = tk.Button(toolbar, text="Привязать клавишу", command=self.start_binding)
        bind_btn.pack(side=tk.LEFT, padx=5)

        volume_frame = tk.Frame(toolbar)
        volume_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(volume_frame, text="Громкость:").pack(side=tk.LEFT)
        self.volume_scale = tk.Scale(
            volume_frame, from_=0, to=100, orient=tk.HORIZONTAL,
            command=self.set_volume, showvalue=True
        )
        self.volume_scale.set(70)
        self.volume_scale.pack(side=tk.LEFT)

        frame = tk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            frame, columns=("key", "path"), show="headings",
            yscrollcommand=scrollbar.set
        )
        self.tree.heading("key", text="Клавиша/Кнопка")
        self.tree.heading("path", text="Файл")
        self.tree.column("key", width=150)
        self.tree.column("path", width=500)
        self.tree.pack(fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.tree.yview)

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Проиграть", command=self.play_selected)
        self.context_menu.add_command(label="Привязать клавишу", command=self.start_binding)
        self.context_menu.add_command(label="Привязать кнопку мыши", command=self.start_mouse_binding)
        self.context_menu.add_command(label="Удалить", command=self.remove_selected)
        self.context_menu.add_command(label="Проверить звук", command=self.test_sound)

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.play_selected)

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)

    def set_volume(self, val):
        self.volume = float(val) / 100
        for sound_data in self.sounds.values():
            if "sound" in sound_data:
                sound_data["sound"].set_volume(self.volume)

    def test_sound(self):
        try:
            test_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "test.wav"))
            test_sound.play()
            messagebox.showinfo("Проверка", "Тестовый звук воспроизведен")
        except:
            messagebox.showerror("Ошибка", "Не удалось воспроизвести тестовый звук")

    def handle_drop(self, event):
        files = self.tk.splitlist(event.data)
        for file in files:
            if file.lower().endswith(('.mp3', '.wav', '.ogg')):
                self.add_sound_file(file)

    def add_sound(self):
        files = filedialog.askopenfilenames(
            title="Выберите звуковые файлы",
            filetypes=(("Аудио файлы", "*.mp3 *.wav *.ogg"), ("Все файлы", "*.*"))
        )
        for file in files:
            self.add_sound_file(file)

    def add_sound_file(self, file_path):
        try:
            sound = pygame.mixer.Sound(file_path)
            sound.set_volume(self.volume)

            file_name = os.path.basename(file_path)
            item = self.tree.insert("", tk.END, values=("Не назначено", file_name))
            self.sounds[item] = {
                "path": file_path,
                "key": None,
                "mouse_button": None,
                "sound": sound,
                "channel": None
            }
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл {file_path}\n{str(e)}")

    def start_binding(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите звук для привязки")
            return

        self.current_binding = selected[0]
        self.bind("<Key>", self.finish_binding)
        messagebox.showinfo("Привязка клавиши", "Нажмите любую клавишу для привязки")

    def start_mouse_binding(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите звук для привязки")
            return

        self.current_binding = selected[0]
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Левая кнопка", command=lambda: self.finish_mouse_binding("left"))
        menu.add_command(label="Правая кнопка", command=lambda: self.finish_mouse_binding("right"))
        menu.add_command(label="Средняя кнопка", command=lambda: self.finish_mouse_binding("middle"))
        menu.post(self.winfo_pointerx(), self.winfo_pointery())

    def finish_binding(self, event):
        self.unbind("<Key>")

        if not self.current_binding:
            return

        key_name = event.keysym

        if len(key_name) == 1 or key_name in [
            'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
            'Escape', 'Tab', 'Caps_Lock', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R',
            'Alt_L', 'Alt_R', 'space', 'Return', 'BackSpace', 'Delete', 'Insert',
            'Home', 'End', 'Page_Up', 'Page_Down', 'Left', 'Right', 'Up', 'Down',
            'Num_Lock', 'Scroll_Lock', 'Print', 'Pause'
        ]:
            for item, data in self.sounds.items():
                if data["key"] == key_name:
                    data["key"] = None
                    self.tree.item(item, values=("Не назначено", data["path"]))

            self.sounds[self.current_binding]["key"] = key_name
            self.sounds[self.current_binding]["mouse_button"] = None
            self.tree.item(self.current_binding,
                           values=(f"Клавиша: {key_name}", self.sounds[self.current_binding]["path"]))
        else:
            messagebox.showwarning("Ошибка", f"Клавиша '{key_name}' не поддерживается")

        self.current_binding = None

    def finish_mouse_binding(self, button):
        if not self.current_binding:
            return

        for item, data in self.sounds.items():
            if data["mouse_button"] == button:
                data["mouse_button"] = None
                self.tree.item(item, values=("Не назначено", data["path"]))

        self.sounds[self.current_binding]["mouse_button"] = button
        self.sounds[self.current_binding]["key"] = None
        self.tree.item(self.current_binding, values=(f"Мышь: {button}", self.sounds[self.current_binding]["path"]))
        self.current_binding = None

    def play_selected(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        item = selected[0]
        self.play_sound(item)

    def play_sound(self, item):
        if item not in self.sounds:
            return

        sound_data = self.sounds[item]
        try:
            if "channel" in sound_data and sound_data["channel"] is not None:
                sound_data["channel"].stop()

            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(sound_data["sound"])
                sound_data["channel"] = channel
            else:
                sound_data["sound"].play()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось воспроизвести звук\n{str(e)}")

    def remove_selected(self):
        selected = self.tree.selection()
        if not selected:
            return

        item = selected[0]
        if item in self.sounds:
            del self.sounds[item]
        self.tree.delete(item)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def check_hotkeys(self):
        while self.check_hotkeys_running:
            try:
                for item, data in self.sounds.items():
                    try:
                        if data["key"]:
                            try:
                                if keyboard.is_pressed(data["key"]):
                                    self.play_sound(item)
                                    while keyboard.is_pressed(data["key"]):
                                        time.sleep(0.01)
                            except ValueError:
                                data["key"] = None
                                self.tree.item(item, values=("Не назначено", data["path"]))
                                continue

                        if data["mouse_button"]:
                            if data["mouse_button"] == "left" and mouse.is_pressed(button="left"):
                                self.play_sound(item)
                                while mouse.is_pressed(button="left"):
                                    time.sleep(0.01)
                            elif data["mouse_button"] == "right" and mouse.is_pressed(button="right"):
                                self.play_sound(item)
                                while mouse.is_pressed(button="right"):
                                    time.sleep(0.01)
                            elif data["mouse_button"] == "middle" and mouse.is_pressed(button="middle"):
                                self.play_sound(item)
                                while mouse.is_pressed(button="middle"):
                                    time.sleep(0.01)
                    except Exception as e:
                        print(f"Error checking hotkey for item {item}: {str(e)}")
                        continue

                time.sleep(0.05)
            except Exception as e:
                print(f"Error in hotkey thread: {str(e)}")
                time.sleep(1)

    def on_close(self):
        self.check_hotkeys_running = False
        self.destroy()


if __name__ == "__main__":
    try:
        app = SoundpadApp()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Критическая ошибка", f"Программа завершилась с ошибкой:\n{str(e)}")
