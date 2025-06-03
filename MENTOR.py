import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, filedialog, simpledialog
import requests
import sympy as sp
import webbrowser
import subprocess
from fractions import Fraction
import qrcode
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from datetime import datetime
import random
import json
from PIL import Image, ImageTk, ImageDraw
import os
import time
import math
import string
import secrets
import re


class ChatBotApp:
    def open_game_selector(self):
        game_window = tk.Toplevel(self.root)
        game_window.title("Games" if self.current_language == "en" else "Игры")

        ttk.Button(game_window,
                   text="Snake Game" if self.current_language == "en" else "Змейка",
                   command=lambda: self.start_game("snake")).pack(pady=5)

        ttk.Button(game_window,
                   text="Ping Pong" if self.current_language == "en" else "Пинг-понг",
                   command=lambda: self.start_game("pong")).pack(pady=5)

        ttk.Button(game_window,
                   text="Memory Game" if self.current_language == "en" else "Игра на память",
                   command=lambda: self.start_game("memory")).pack(pady=5)

    def start_game(self, game_type):
        if self.game_window and tk.Toplevel.winfo_exists(self.game_window):
            self.game_window.destroy()

        self.game_window = tk.Toplevel(self.root)
        self.game_window.title(game_type.capitalize())
        self.game_type = game_type
        self.game_running = True

        if game_type == "snake":
            self.setup_snake_game()
        elif game_type == "pong":
            self.setup_pong_game()
        elif game_type == "memory":
            self.setup_memory_game()

        self.game_window.protocol("WM_DELETE_WINDOW", self.stop_game)

    def stop_game(self):
        self.game_running = False
        if self.game_window:
            self.game_window.destroy()
        self.game_window = None

    def setup_snake_game(self):
        self.canvas = tk.Canvas(self.game_window, width=400, height=400, bg='black')
        self.canvas.pack()

        self.snake = [(200, 200), (210, 200), (220, 200)]
        self.snake_direction = "Left"
        self.food = self.create_food()
        self.score = 0

        self.score_label = ttk.Label(self.game_window,
                                     text=f"Score: {self.score}" if self.current_language == "en"
                                     else f"Счет: {self.score}")
        self.score_label.pack()

        self.game_window.bind("<KeyPress>", self.change_snake_direction)
        self.update_snake()

    def create_food(self):
        x = random.randint(0, 39) * 10
        y = random.randint(0, 39) * 10
        self.food_pos = (x, y)
        return self.canvas.create_oval(x, y, x + 10, y + 10, fill='red')

    def change_snake_direction(self, event):
        if event.keysym in ["Up", "Down", "Left", "Right"]:
            self.snake_direction = event.keysym

    def update_snake(self):
        if not self.game_running:
            return

        head_x, head_y = self.snake[0]

        if self.snake_direction == "Up":
            new_head = (head_x, head_y - 10)
        elif self.snake_direction == "Down":
            new_head = (head_x, head_y + 10)
        elif self.snake_direction == "Left":
            new_head = (head_x - 10, head_y)
        elif self.snake_direction == "Right":
            new_head = (head_x + 10, head_y)

        if (new_head in self.snake or
                new_head[0] < 0 or new_head[0] >= 400 or
                new_head[1] < 0 or new_head[1] >= 400):
            self.game_over()
            return

        self.snake.insert(0, new_head)

        # Check if food eaten
        if new_head == self.food_pos:
            self.score += 1
            self.score_label.config(
                text=f"Score: {self.score}" if self.current_language == "en"
                else f"Счет: {self.score}")
            self.canvas.delete(self.food)
            self.food = self.create_food()
        else:
            self.snake.pop()

        self.canvas.delete("snake")
        for segment in self.snake:
            self.canvas.create_rectangle(
                segment[0], segment[1], segment[0] + 10, segment[1] + 10,
                fill='green', tags="snake")

        self.game_window.after(100, self.update_snake)

    def game_over(self):
        self.game_running = False
        self.canvas.create_text(200, 200, text="GAME OVER" if self.current_language == "en" else "ИГРА ОКОНЧЕНА",
                                fill='white', font=('Helvetica', 20))

    def setup_pong_game(self):
        self.canvas = tk.Canvas(self.game_window, width=400, height=400, bg='black')
        self.canvas.pack()

        self.paddle_a = self.canvas.create_rectangle(0, 150, 10, 250, fill='white')
        self.paddle_b = self.canvas.create_rectangle(390, 150, 400, 250, fill='white')
        self.ball = self.canvas.create_oval(195, 195, 205, 205, fill='white')

        self.ball_dx = 2
        self.ball_dy = 2
        self.score_a = 0
        self.score_b = 0

        self.score_label = ttk.Label(self.game_window,
                                     text=f"Player A: {self.score_a}  Player B: {self.score_b}")
        self.score_label.pack()

        self.game_window.bind("<KeyPress>", self.move_paddles)
        self.update_pong()

    def move_paddles(self, event):
        if event.keysym == "w":
            self.canvas.move(self.paddle_a, 0, -20)
        elif event.keysym == "s":
            self.canvas.move(self.paddle_a, 0, 20)
        elif event.keysym == "Up":
            self.canvas.move(self.paddle_b, 0, -20)
        elif event.keysym == "Down":
            self.canvas.move(self.paddle_b, 0, 20)

    def update_pong(self):
        if not self.game_running:
            return

        self.canvas.move(self.ball, self.ball_dx, self.ball_dy)
        ball_pos = self.canvas.coords(self.ball)
        paddle_a_pos = self.canvas.coords(self.paddle_a)
        paddle_b_pos = self.canvas.coords(self.paddle_b)

        if ball_pos[1] <= 0 or ball_pos[3] >= 400:
            self.ball_dy = -self.ball_dy

        if (ball_pos[0] <= paddle_a_pos[2] and
                ball_pos[1] >= paddle_a_pos[1] and
                ball_pos[3] <= paddle_a_pos[3]):
            self.ball_dx = -self.ball_dx
        elif (ball_pos[2] >= paddle_b_pos[0] and
              ball_pos[1] >= paddle_b_pos[1] and
              ball_pos[3] <= paddle_b_pos[3]):
            self.ball_dx = -self.ball_dx

        if ball_pos[0] <= 0:
            self.score_b += 1
            self.reset_ball()
        elif ball_pos[2] >= 400:
            self.score_a += 1
            self.reset_ball()

        self.score_label.config(text=f"Player A: {self.score_a}  Player B: {self.score_b}")
        self.game_window.after(10, self.update_pong)

    def reset_ball(self):
        self.canvas.coords(self.ball, 195, 195, 205, 205)
        self.ball_dx = -self.ball_dx if random.random() > 0.5 else self.ball_dx
        self.ball_dy = -self.ball_dy if random.random() > 0.5 else self.ball_dy

    def setup_memory_game(self):
        self.canvas = tk.Canvas(self.game_window, width=400, height=400, bg='white')
        self.canvas.pack()

        self.tiles = []
        self.colors = ['red', 'blue', 'green', 'yellow',
                       'purple', 'orange', 'cyan', 'magenta',
                       'red', 'blue', 'green', 'yellow',
                       'purple', 'orange', 'cyan', 'magenta']
        random.shuffle(self.colors)

        self.flipped = []
        self.matched = []
        self.moves = 0

        for i in range(16):
            row = i // 4
            col = i % 4
            tile = self.canvas.create_rectangle(
                col * 100, row * 100,
                (col + 1) * 100, (row + 1) * 100,
                fill='gray', outline='black')
            self.tiles.append(tile)
            self.canvas.tag_bind(tile, '<Button-1>', lambda e, idx=i: self.flip_tile(idx))

        self.score_label = ttk.Label(self.game_window,
                                     text=f"Moves: {self.moves}" if self.current_language == "en"
                                     else f"Ходы: {self.moves}")
        self.score_label.pack()

    def flip_tile(self, idx):
        if idx in self.flipped or idx in self.matched or len(self.flipped) >= 2:
            return

        self.flipped.append(idx)
        self.canvas.itemconfig(self.tiles[idx], fill=self.colors[idx])

        if len(self.flipped) == 2:
            self.moves += 1
            self.score_label.config(
                text=f"Moves: {self.moves}" if self.current_language == "en"
                else f"Ходы: {self.moves}")

            if self.colors[self.flipped[0]] == self.colors[self.flipped[1]]:
                self.matched.extend(self.flipped)
                self.flipped = []
                if len(self.matched) == 16:
                    self.game_window.after(500, self.game_won)
            else:
                self.game_window.after(1000, self.hide_tiles)

    def hide_tiles(self):
        for idx in self.flipped:
            self.canvas.itemconfig(self.tiles[idx], fill='gray')
        self.flipped = []

    def game_won(self):
        self.canvas.create_text(200, 200,
                                text=f"You won in {self.moves} moves!" if self.current_language == "en"
                                else f"Вы выиграли за {self.moves} ходов!",
                                fill='black', font=('Helvetica', 16))
        self.game_running = False

    def __init__(self, root):
        self.root = root
        self.root.title("Mentor")
        self.root.state('zoomed')
        self.current_language = "en"
        self.current_theme = "light"
        self.current_font = ("Arial", 12)
        self.proxy_enabled = False
        self.setup_ui()

        self.paint_window = None
        self.drawing = False
        self.last_x = None
        self.last_y = None
        self.pen_color = "black"
        self.pen_size = 5

        self.code_editor_window = None
        self.code_language = "python"

        self.game_window = None
        self.canvas = None
        self.game_running = False
        self.game_type = None

    def setup_ui(self):
        self.create_widgets()
        self.apply_theme()

    def create_widgets(self):
        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_area.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        self.entry_field = ttk.Entry(self.root, width=60)
        self.entry_field.pack(padx=10, pady=5)
        self.entry_field.bind("<Return>", self.send_message_on_enter)

        settings_button = ttk.Button(self.root, text="Настройки" if self.current_language == "ru" else "Settings",
                                     command=self.open_settings)
        settings_button.pack(pady=5)

    def update_ui_language(self):
        self.root.title("Чат-бот" if self.current_language == "ru" else "Chat Bot")

    def apply_theme(self):
        bg_color = "white" if self.current_theme == "light" else "#2d2d2d"
        fg_color = "black" if self.current_theme == "light" else "white"

        self.root.configure(bg=bg_color)
        self.chat_area.configure(bg=bg_color, fg=fg_color)
        self.entry_field.configure(background=bg_color, foreground=fg_color)

    def send_message_on_enter(self, event):
        self.send_message()

    def send_message(self):
        user_message = self.entry_field.get()
        if user_message:
            self.chat_area.config(state=tk.NORMAL)
            self.chat_area.insert(tk.END, f"{'Вы' if self.current_language == 'ru' else 'You'}: {user_message}\n")

            self.current_language = self.detect_language(user_message)
            self.update_ui_language()

            if any(word in user_message.lower() for word in ["привет", "здравствуй", "hello", "hi"]):
                self.bot_response("Привет!" if self.current_language == "ru" else "Hello!")
            elif any(word in user_message.lower() for word in ["пока", "до свидания", "bye", "goodbye"]):
                self.bot_response("Пока!" if self.current_language == "ru" else "Goodbye!")
            elif "джарвис" in user_message.lower():
                self.bot_response("Да, сэр?" if self.current_language == "ru" else "Yes, sir?")
            elif "exe" in user_message.lower():
                self.generate_exe()
            elif "qr" in user_message.lower():
                self.generate_qr_code(user_message)
            elif "прокси" in user_message.lower() or "proxy" in user_message.lower():
                self.toggle_proxy()
            elif "помощь" in user_message.lower() or "help" in user_message.lower():
                self.show_help()
            elif "калькулятор" in user_message.lower() or "calc" in user_message.lower():
                self.open_calculator()
            elif "факт" in user_message.lower() or "fact" in user_message.lower():
                self.get_random_fact()
            elif "задача" in user_message.lower() or "task" in user_message.lower():
                self.solve_problem(user_message)
            elif "найди" in user_message.lower() or "search" in user_message.lower():
                self.search_web(user_message)
            elif "биржа" in user_message.lower() or "exchange" in user_message.lower():
                self.show_exchange_rates()
            elif "рисовать" in user_message.lower() or "paint" in user_message.lower():
                self.open_paint()
            elif "редактор кода" in user_message.lower() or "code editor" in user_message.lower():
                self.open_code_editor()
            elif "крипто" in user_message.lower() or "crypto" in user_message.lower():
                self.crypto_tools()
            elif "бизнес" in user_message.lower() or "business" in user_message.lower():
                self.business_tools()
            elif "игра" in user_message.lower() or "game" in user_message.lower():
                self.open_game_selector()
            elif "пароль" in user_message.lower() or "password" in user_message.lower():
                self.open_password_tools()
            else:
                self.bot_response(
                    "Не понимаю вашего запроса. Попробуйте еще раз." if self.current_language == "ru" else "I do not understand your request. Please try again.")

            self.chat_area.config(state=tk.DISABLED)
            self.entry_field.delete(0, tk.END)
            self.chat_area.see(tk.END)

    def bot_response(self, message):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"{'Бот' if self.current_language == 'ru' else 'Bot'}: {message}\n")
        self.chat_area.config(state=tk.DISABLED)

    def detect_language(self, message):
        return "ru" if any(cyrillic in message for cyrillic in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя") else "en"

    def generate_exe(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
            if file_path:
                subprocess.run(["pyinstaller", "--onefile", "--windowed", file_path])
                self.bot_response(
                    "Исполняемый файл успешно создан." if self.current_language == "ru" else "Executable file created successfully.")
        except Exception as e:
            self.bot_response(
                "Не удалось создать исполняемый файл." if self.current_language == "ru" else "Failed to create executable file.")

    def generate_qr_code(self, message):
        data = message.lower().replace("qr", "").strip()

        if data.startswith(("http://", "https://")):
            url = data
        elif "." in data and " " not in data:
            url = f"http://{data}"
        else:
            url = None

        if not data:
            self.bot_response(
                "Пожалуйста, укажите данные для QR-кода." if self.current_language == "ru" else "Please specify data for the QR code.")
            return

        try:
            qr = qrcode.QRCode(
                version=1,
                box_size=10,
                border=5,
            )
            qr.add_data(url if url else data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            filename = f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            img.save(filename)

            self.bot_response(
                f"QR-код успешно создан и сохранен как {filename}" if self.current_language == "ru"
                else f"QR code successfully created and saved as {filename}")

            self.show_image(filename)
        except Exception as e:
            self.bot_response(
                f"Не удалось создать QR-код: {str(e)}" if self.current_language == "ru"
                else f"Failed to create QR code: {str(e)}")

    def show_image(self, filename):
        img_window = tk.Toplevel(self.root)
        img_window.title("QR Code" if self.current_language == "en" else "QR код")

        img = Image.open(filename)
        photo = ImageTk.PhotoImage(img)

        label = tk.Label(img_window, image=photo)
        label.image = photo
        label.pack()

        ttk.Button(img_window,
                   text="Закрыть" if self.current_language == "ru" else "Close",
                   command=img_window.destroy).pack(pady=5)

    def toggle_proxy(self):
        self.proxy_enabled = not self.proxy_enabled
        self.bot_response(
            "Прокси включен." if self.proxy_enabled and self.current_language == "ru" else "Прокси выключен." if not self.proxy_enabled and self.current_language == "ru" else "Proxy enabled." if self.proxy_enabled else "Proxy disabled.")

    def show_help(self):
        help_text_ru = """
1. Приветствие: "привет", "здравствуй"
2. Прощание: "пока", "до свидания"
3. Создание EXE: "exe"
4. QR-код: "qr [данные/ссылка]"
5. Прокси: "прокси"
6. Помощь: "помощь"
7. Калькулятор: "калькулятор"
8. Случайный факт: "факт"
9. Решение задачи: "задача [ваша задача]"
10. Поиск в интернете: "найди [запрос]"
11. Курсы валют: "биржа"
12. Рисование: "рисовать"
13. Редактор кода: "редактор кода"
14. Криптовалюты: "крипто"
15. Бизнес-инструменты: "бизнес"
16. Игры: "игра"
17. Генератор пароля: "пароль"
18. Проверка пароля: "проверить пароль"
"""
        help_text_en = """
1. Greeting: "hello", "hi"
2. Farewell: "bye", "goodbye"
3. Create EXE: "exe"
4. QR code: "qr [data/url]"
5. Proxy: "proxy"
6. Help: "help"
7. Calculator: "calc"
8. Random fact: "fact"
9. Solve problem: "task [your problem]"
10. Search the web: "search [query]"
11. Exchange rates: "exchange"
12. Drawing: "paint"
13. Code editor: "code editor"
14. Cryptocurrency: "crypto"
15. Business tools: "business"
16. Games: "game"
17. Password generator: "password"
18. Password check: "check password"
"""

        if self.current_language == "ru":
            self.bot_response(help_text_ru)
        else:
            self.bot_response(help_text_en)

    def open_password_tools(self):
        password_window = tk.Toplevel(self.root)
        password_window.title("Пароли" if self.current_language == "ru" else "Password Tools")

        ttk.Button(password_window,
                   text="Сгенерировать пароль" if self.current_language == "ru" else "Generate password",
                   command=self.generate_password).pack(pady=5)

        ttk.Button(password_window,
                   text="Проверить надежность" if self.current_language == "ru" else "Check password strength",
                   command=self.check_password_strength).pack(pady=5)

    def generate_password(self):
        def generate():
            length = int(length_var.get())
            use_upper = upper_var.get()
            use_digits = digits_var.get()
            use_special = special_var.get()

            chars = string.ascii_lowercase
            if use_upper:
                chars += string.ascii_uppercase
            if use_digits:
                chars += string.digits
            if use_special:
                chars += string.punctuation

            password = ''.join(secrets.choice(chars) for _ in range(length))
            password_var.set(password)

            strength = self.check_password(password, silent=True)
            strength_label.config(text=strength)

        gen_window = tk.Toplevel(self.root)
        gen_window.title("Генератор пароля" if self.current_language == "ru" else "Password Generator")

        ttk.Label(gen_window, text="Длина:" if self.current_language == "ru" else "Length:").pack()
        length_var = tk.IntVar(value=12)
        ttk.Entry(gen_window, textvariable=length_var).pack()

        upper_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(gen_window,
                        text="Заглавные буквы" if self.current_language == "ru" else "Uppercase letters",
                        variable=upper_var).pack()

        digits_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(gen_window,
                        text="Цифры" if self.current_language == "ru" else "Digits",
                        variable=digits_var).pack()

        special_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(gen_window,
                        text="Спецсимволы" if self.current_language == "ru" else "Special characters",
                        variable=special_var).pack()

        ttk.Button(gen_window,
                   text="Сгенерировать" if self.current_language == "ru" else "Generate",
                   command=generate).pack(pady=5)

        password_var = tk.StringVar()
        ttk.Entry(gen_window, textvariable=password_var, state="readonly").pack()

        strength_label = ttk.Label(gen_window, text="")
        strength_label.pack()

    def check_password_strength(self):
        def check():
            password = password_entry.get()
            result = self.check_password(password)
            result_label.config(text=result)

        check_window = tk.Toplevel(self.root)
        check_window.title("Проверка пароля" if self.current_language == "ru" else "Password Check")

        ttk.Label(check_window,
                  text="Введите пароль:" if self.current_language == "ru" else "Enter password:").pack()

        password_entry = ttk.Entry(check_window, show="*")
        password_entry.pack()

        ttk.Button(check_window,
                   text="Проверить" if self.current_language == "ru" else "Check",
                   command=check).pack(pady=5)

        result_label = ttk.Label(check_window, text="")
        result_label.pack()

    def check_password(self, password, silent=False):
        if not password:
            return "Пустой пароль" if self.current_language == "ru" else "Empty password"

        strength = 0
        feedback = []

        if len(password) >= 12:
            strength += 2
        elif len(password) >= 8:
            strength += 1
        else:
            feedback.append("Слишком короткий" if self.current_language == "ru" else "Too short")

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)

        if has_upper and has_lower:
            strength += 1
        if has_digit:
            strength += 1
        if has_special:
            strength += 1

        if not has_upper or not has_lower:
            feedback.append(
                "Нужны заглавные и строчные буквы" if self.current_language == "ru" else "Need upper and lower case")
        if not has_digit:
            feedback.append("Добавьте цифры" if self.current_language == "ru" else "Add digits")
        if not has_special:
            feedback.append("Добавьте спецсимволы" if self.current_language == "ru" else "Add special chars")

        if strength >= 5:
            rating = "Отличный" if self.current_language == "ru" else "Excellent"
        elif strength >= 3:
            rating = "Хороший" if self.current_language == "ru" else "Good"
        elif strength >= 1:
            rating = "Слабый" if self.current_language == "ru" else "Weak"
        else:
            rating = "Очень слабый" if self.current_language == "ru" else "Very weak"

        if silent:
            return rating

        feedback_text = f"{rating} ({strength}/5)"
        if feedback:
            feedback_text += "\n" + "\n".join(feedback)

        return feedback_text

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки" if self.current_language == "ru" else "Settings")

        theme_label = ttk.Label(settings_window, text="Тема:" if self.current_language == "ru" else "Theme:")
        theme_label.pack(padx=10, pady=5, anchor='w')

        theme_var = tk.StringVar(value="Светлая" if self.current_theme == "light" else "Темная")
        theme_dropdown = ttk.Combobox(settings_window, values=["Светлая", "Темная"], textvariable=theme_var,
                                      state='readonly')
        theme_dropdown.pack(padx=10, pady=5, anchor='w')

        def apply_settings():
            self.current_theme = "light" if theme_var.get() == "Светлая" else "dark"
            self.apply_theme()
            settings_window.destroy()
            self.bot_response("Настройки применены." if self.current_language == "ru" else "Settings applied.")

        ttk.Button(settings_window, text="Применить" if self.current_language == "ru" else "Apply",
                   command=apply_settings).pack(pady=10)

    def open_calculator(self):
        calculator_window = tk.Toplevel(self.root)
        calculator_window.title("Калькулятор" if self.current_language == "ru" else "Calculator")

        self.numerator1 = tk.StringVar()
        self.denominator1 = tk.StringVar()
        self.numerator2 = tk.StringVar()
        self.denominator2 = tk.StringVar()
        self.operation = tk.StringVar(value="+")
        self.result = tk.StringVar()

        frame1 = ttk.Frame(calculator_window)
        frame1.pack(pady=5)

        ttk.Label(frame1, text="Числитель 1:").grid(row=0, column=0)
        ttk.Entry(frame1, textvariable=self.numerator1, width=10).grid(row=1, column=0)

        ttk.Label(frame1, text="Знаменатель 1:").grid(row=2, column=0)
        ttk.Entry(frame1, textvariable=self.denominator1, width=10).grid(row=3, column=0)

        frame_op = ttk.Frame(calculator_window)
        frame_op.pack(pady=5)

        ttk.Label(frame_op, text="Операция:").pack()
        ttk.Combobox(frame_op, textvariable=self.operation,
                     values=["+", "-", "*", "/"], state="readonly", width=5).pack()

        frame2 = ttk.Frame(calculator_window)
        frame2.pack(pady=5)

        ttk.Label(frame2, text="Числитель 2:").grid(row=0, column=0)
        ttk.Entry(frame2, textvariable=self.numerator2, width=10).grid(row=1, column=0)

        ttk.Label(frame2, text="Знаменатель 2:").grid(row=2, column=0)
        ttk.Entry(frame2, textvariable=self.denominator2, width=10).grid(row=3, column=0)

        ttk.Button(calculator_window, text="Вычислить", command=self.calculate_fraction).pack(pady=10)

        ttk.Label(calculator_window, text="Результат:").pack()
        ttk.Label(calculator_window, textvariable=self.result).pack()

        standard_frame = ttk.Frame(calculator_window)
        standard_frame.pack(pady=10)

        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            'C', '0', '=', '+',
            '%', '^'
        ]

        for i, btn in enumerate(buttons):
            row = i // 4
            col = i % 4
            ttk.Button(standard_frame, text=btn, width=5,
                       command=lambda b=btn: self.standard_calculator_click(b)).grid(row=row, column=col, padx=2,
                                                                                     pady=2)

        self.calc_entry = ttk.Entry(calculator_window, width=20)
        self.calc_entry.pack(pady=5)

    def calculate_fraction(self):
        try:
            num1 = Fraction(int(self.numerator1.get()), int(self.denominator1.get()))
            num2 = Fraction(int(self.numerator2.get()), int(self.denominator2.get()))

            op = self.operation.get()
            if op == "+":
                result = num1 + num2
            elif op == "-":
                result = num1 - num2
            elif op == "*":
                result = num1 * num2
            elif op == "/":
                result = num1 / num2

            self.result.set(str(result))
        except Exception as e:
            self.result.set(f"Ошибка: {str(e)}" if self.current_language == "ru" else f"Error: {str(e)}")

    def standard_calculator_click(self, button):
        current = self.calc_entry.get()

        if button == 'C':
            self.calc_entry.delete(0, tk.END)
        elif button == '=':
            try:
                expr = current.replace('^', '**')
                result = eval(expr)
                self.calc_entry.delete(0, tk.END)
                self.calc_entry.insert(0, str(result))
            except Exception as e:
                self.calc_entry.delete(0, tk.END)
                self.calc_entry.insert(0, "Error")
        elif button == '%':
            try:
                value = float(current) / 100
                self.calc_entry.delete(0, tk.END)
                self.calc_entry.insert(0, str(value))
            except:
                self.calc_entry.delete(0, tk.END)
                self.calc_entry.insert(0, "Error")
        else:
            self.calc_entry.insert(tk.END, button)

    def solve_problem(self, message):
        try:
            problem = message.lower().replace("задача", "").replace("task", "").strip()
            if not problem:
                self.bot_response(
                    "Пожалуйста, укажите задачу." if self.current_language == "ru" else "Please specify a problem.")
                return

            if "=" in problem:
                x, y = sp.symbols('x y')
                solution = sp.solve(problem, x)
                self.bot_response(
                    f"Решение уравнения: {solution}" if self.current_language == "ru" else f"Solution to the equation: {solution}")
            else:
                result = eval(problem)
                self.bot_response(f"Результат: {result}" if self.current_language == "ru" else f"Result: {result}")
        except Exception as e:
            self.bot_response(
                f"Ошибка при решении задачи: {str(e)}" if self.current_language == "ru" else f"Error solving the problem: {str(e)}")

    def get_random_fact(self):
        try:
            if self.current_language == "ru":
                facts_ru = [
                    "Крокодилы не могут высовывать язык.",
                    "Сердце кита бьется всего 9 раз в минуту.",
                    "В Японии есть остров, населенный только кроликами.",
                    "Мед никогда не портится.",
                    "Кошки могут издавать более 100 различных звуков.",
                    "Человеческое тело содержит достаточно углерода, чтобы изготовить 900 карандашей.",
                    "Осьминоги имеют три сердца.",
                    "Венера - единственная планета, которая вращается по часовой стрелке.",
                    "Бананы - это ягоды, а клубника - нет.",
                    "В Швейцарии запрещено иметь только одну морскую свинку, так как они скучают в одиночестве."
                ]
                fact = random.choice(facts_ru)
            else:
                facts_en = [
                    "Crocodiles can't stick out their tongues.",
                    "A whale's heart beats only 9 times per minute.",
                    "There is an island in Japan populated only by rabbits.",
                    "Honey never spoils.",
                    "Cats can make over 100 different sounds.",
                    "The human body contains enough carbon to make 900 pencils.",
                    "Octopuses have three hearts.",
                    "Venus is the only planet that rotates clockwise.",
                    "Bananas are berries, but strawberries aren't.",
                    "In Switzerland, it's illegal to own just one guinea pig because they get lonely."
                ]
                fact = random.choice(facts_en)

            self.bot_response(f"Случайный факт: {fact}" if self.current_language == "ru" else f"Random fact: {fact}")
        except Exception as e:
            self.bot_response("Ошибка при запросе факта." if self.current_language == "ru" else "Error fetching fact.")

    def search_web(self, message):
        query = message.lower().replace("найди", "").replace("search", "").strip()
        if not query:
            self.bot_response(
                "Пожалуйста, укажите запрос для поиска." if self.current_language == "ru" else "Please specify a search query.")
            return

        webbrowser.open(f"https://www.google.com/search?q={query}")
        self.bot_response(
            f"Результаты поиска для '{query}' открыты в браузере." if self.current_language == "ru" else f"Search results for '{query}' opened in the browser.")

    def show_exchange_rates(self):
        try:
            crypto_response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd")

            currency_response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")

            if crypto_response.status_code == 200 and currency_response.status_code == 200:
                crypto_data = crypto_response.json()
                currency_data = currency_response.json()

                exchange_message = "Курсы криптовалют:\n"
                exchange_message += f"Bitcoin: ${crypto_data['bitcoin']['usd']}\n"
                exchange_message += f"Ethereum: ${crypto_data['ethereum']['usd']}\n\n"

                exchange_message += "Курсы валют (к USD):\n"
                currencies = ['EUR', 'GBP', 'JPY', 'RUB', 'CNY']
                for currency in currencies:
                    if currency in currency_data['rates']:
                        rate = currency_data['rates'][currency]
                        exchange_message += f"1 USD = {rate:.2f} {currency}\n"

                self.bot_response(exchange_message)
            else:
                self.bot_response(
                    "Не удалось получить данные о курсах." if self.current_language == "ru" else "Failed to fetch exchange rates.")
        except Exception as e:
            self.bot_response(
                f"Ошибка при запросе курсов: {str(e)}" if self.current_language == "ru" else f"Error fetching exchange rates: {str(e)}")

    def open_paint(self):
        if self.paint_window and tk.Toplevel.winfo_exists(self.paint_window):
            self.paint_window.lift()
            return

        self.paint_window = tk.Toplevel(self.root)
        self.paint_window.title("Paint" if self.current_language == "en" else "Рисование")

        self.canvas = tk.Canvas(self.paint_window, width=600, height=400, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        controls = ttk.Frame(self.paint_window)
        controls.pack(fill=tk.X)

        colors = ['black', 'red', 'green', 'blue', 'yellow', 'white']
        for color in colors:
            btn = ttk.Button(controls, width=3, command=lambda c=color: self.set_pen_color(c))
            btn.configure(style=f"{color.capitalize()}.TButton")
            btn.pack(side=tk.LEFT, padx=2)

        ttk.Label(controls, text="Size:" if self.current_language == "en" else "Размер:").pack(side=tk.LEFT)
        self.size_slider = ttk.Scale(controls, from_=1, to=20, value=self.pen_size)
        self.size_slider.pack(side=tk.LEFT)

        ttk.Button(controls, text="Clear" if self.current_language == "en" else "Очистить",
                   command=self.clear_canvas).pack(side=tk.RIGHT)

        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

    def set_pen_color(self, color):
        self.pen_color = color

    def start_drawing(self, event):
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y

    def draw(self, event):
        if self.drawing:
            x, y = event.x, event.y
            self.canvas.create_line(self.last_x, self.last_y, x, y,
                                    width=self.size_slider.get(),
                                    fill=self.pen_color,
                                    capstyle=tk.ROUND, smooth=True)
            self.last_x = x
            self.last_y = y

    def stop_drawing(self, event):
        self.drawing = False

    def clear_canvas(self):
        self.canvas.delete("all")

    def open_code_editor(self):
        if self.code_editor_window and tk.Toplevel.winfo_exists(self.code_editor_window):
            self.code_editor_window.lift()
            return

        self.code_editor_window = tk.Toplevel(self.root)
        self.code_editor_window.title("Code Editor" if self.current_language == "en" else "Редактор кода")

        lang_frame = ttk.Frame(self.code_editor_window)
        lang_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(lang_frame, text="Language:" if self.current_language == "en" else "Язык:").pack(side=tk.LEFT)

        self.lang_var = tk.StringVar(value="python")
        lang_menu = ttk.Combobox(lang_frame, textvariable=self.lang_var,
                                 values=["python", "c++"], state="readonly")
        lang_menu.pack(side=tk.LEFT, padx=5)

        self.code_text = scrolledtext.ScrolledText(self.code_editor_window, wrap=tk.WORD)
        self.code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        btn_frame = ttk.Frame(self.code_editor_window)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(btn_frame, text="Run" if self.current_language == "en" else "Запуск",
                   command=self.run_code).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Save" if self.current_language == "en" else "Сохранить",
                   command=self.save_code).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear" if self.current_language == "en" else "Очистить",
                   command=self.clear_code).pack(side=tk.LEFT)

    def run_code(self):
        code = self.code_text.get("1.0", tk.END)
        lang = self.lang_var.get()

        try:
            if lang == "python":
                with open("temp_code.py", "w") as f:
                    f.write(code)
                result = subprocess.run(["python", "temp_code.py"], capture_output=True, text=True)

                if result.returncode == 0:
                    self.bot_response(f"Output:\n{result.stdout}")
                else:
                    self.bot_response(f"Error:\n{result.stderr}")
            elif lang == "c++":
                self.bot_response(
                    "C++ execution not implemented yet." if self.current_language == "en" else "Запуск C++ пока не реализован.")
        except Exception as e:
            self.bot_response(f"Error: {str(e)}" if self.current_language == "en" else f"Ошибка: {str(e)}")

    def save_code(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py" if self.lang_var.get() == "python" else ".cpp",
            filetypes=[("Python Files", "*.py"), ("C++ Files", "*.cpp"), ("All Files", "*.*")])

        if file_path:
            with open(file_path, "w") as f:
                f.write(self.code_text.get("1.0", tk.END))
            self.bot_response(
                f"File saved: {file_path}" if self.current_language == "en" else f"Файл сохранен: {file_path}")

    def clear_code(self):
        self.code_text.delete("1.0", tk.END)

    def crypto_tools(self):
        crypto_window = tk.Toplevel(self.root)
        crypto_window.title("Crypto Tools" if self.current_language == "en" else "Крипто инструменты")

        ttk.Button(crypto_window, text="Check Crypto Prices" if self.current_language == "en" else "Проверить цены",
                   command=self.show_exchange_rates).pack(pady=5)

        ttk.Button(crypto_window, text="Crypto Converter" if self.current_language == "en" else "Конвертер криптовалют",
                   command=self.open_crypto_converter).pack(pady=5)

    def open_crypto_converter(self):
        converter_window = tk.Toplevel(self.root)
        converter_window.title("Crypto Converter" if self.current_language == "en" else "Конвертер криптовалют")

        ttk.Label(converter_window, text="From:" if self.current_language == "en" else "Из:").grid(row=0, column=0)
        from_var = tk.StringVar(value="BTC")
        ttk.Combobox(converter_window, textvariable=from_var,
                     values=["BTC", "ETH", "USD", "EUR"], state="readonly").grid(row=0, column=1)

        ttk.Label(converter_window, text="To:" if self.current_language == "en" else "В:").grid(row=1, column=0)
        to_var = tk.StringVar(value="USD")
        ttk.Combobox(converter_window, textvariable=to_var,
                     values=["BTC", "ETH", "USD", "EUR"], state="readonly").grid(row=1, column=1)

        ttk.Label(converter_window, text="Amount:" if self.current_language == "en" else "Сумма:").grid(row=2, column=0)
        amount_var = tk.StringVar(value="1")
        ttk.Entry(converter_window, textvariable=amount_var).grid(row=2, column=1)

        result_var = tk.StringVar()
        ttk.Label(converter_window, textvariable=result_var).grid(row=3, columnspan=2)

        def convert():
            try:
                from_curr = from_var.get()
                to_curr = to_var.get()
                amount = float(amount_var.get())

                rates = {
                    "BTC": {"USD": 50000, "ETH": 15, "EUR": 45000},
                    "ETH": {"USD": 3000, "BTC": 0.066, "EUR": 2700},
                    "USD": {"BTC": 0.00002, "ETH": 0.00033, "EUR": 0.9},
                    "EUR": {"BTC": 0.000022, "ETH": 0.00037, "USD": 1.1}
                }

                if from_curr == to_curr:
                    result = amount
                else:
                    result = amount * rates[from_curr][to_curr]

                result_var.set(f"{amount} {from_curr} = {result:.8f} {to_curr}")
            except Exception as e:
                result_var.set("Error" if self.current_language == "en" else "Ошибка")

        ttk.Button(converter_window, text="Convert" if self.current_language == "en" else "Конвертировать",
                   command=convert).grid(row=4, columnspan=2, pady=5)

    def business_tools(self):
        business_window = tk.Toplevel(self.root)
        business_window.title("Business Tools" if self.current_language == "en" else "Бизнес инструменты")

        ttk.Button(business_window, text="ROI Calculator" if self.current_language == "en" else "Калькулятор ROI",
                   command=self.open_roi_calculator).pack(pady=5)

        ttk.Button(business_window, text="Business Plan" if self.current_language == "en" else "Бизнес план",
                   command=self.generate_business_plan).pack(pady=5)

        ttk.Button(business_window,
                   text="Marketing Tools" if self.current_language == "en" else "Маркетинговые инструменты",
                   command=self.open_marketing_tools).pack(pady=5)

    def open_roi_calculator(self):
        roi_window = tk.Toplevel(self.root)
        roi_window.title("ROI Calculator" if self.current_language == "en" else "Калькулятор ROI")

        ttk.Label(roi_window, text="Investment:" if self.current_language == "en" else "Инвестиции:").grid(row=0,
                                                                                                           column=0)
        investment_var = tk.StringVar(value="1000")
        ttk.Entry(roi_window, textvariable=investment_var).grid(row=0, column=1)

        ttk.Label(roi_window, text="Return:" if self.current_language == "en" else "Возврат:").grid(row=1, column=0)
        return_var = tk.StringVar(value="1200")
        ttk.Entry(roi_window, textvariable=return_var).grid(row=1, column=1)

        roi_var = tk.StringVar()
        ttk.Label(roi_window, textvariable=roi_var).grid(row=2, columnspan=2)

        def calculate_roi():
            try:
                investment = float(investment_var.get())
                return_amt = float(return_var.get())
                roi = ((return_amt - investment) / investment) * 100
                roi_var.set(f"ROI: {roi:.2f}%")
            except:
                roi_var.set("Error" if self.current_language == "en" else "Ошибка")

        ttk.Button(roi_window, text="Calculate" if self.current_language == "en" else "Рассчитать",
                   command=calculate_roi).grid(row=3, columnspan=2, pady=5)

    def generate_business_plan(self):
        plan_window = tk.Toplevel(self.root)
        plan_window.title("Business Plan" if self.current_language == "en" else "Бизнес план")

        ttk.Label(plan_window, text="Business Name:" if self.current_language == "en" else "Название бизнеса:").pack()
        name_var = tk.StringVar()
        ttk.Entry(plan_window, textvariable=name_var).pack()

        ttk.Label(plan_window, text="Industry:" if self.current_language == "en" else "Отрасль:").pack()
        industry_var = tk.StringVar()
        ttk.Combobox(plan_window, textvariable=industry_var,
                     values=["Technology", "Retail", "Food", "Services"] if self.current_language == "en"
                     else ["Технологии", "Розница", "Еда", "Услуги"]).pack()

        def generate():
            name = name_var.get() or ("Your Business" if self.current_language == "en" else "Ваш бизнес")
            industry = industry_var.get() or ("Technology" if self.current_language == "en" else "Технологии")

            plan_text = f"""
            {name} - Business Plan
            Industry: {industry}

            1. Executive Summary:
            - Overview of the business
            - Mission statement
            - Business objectives

            2. Company Description:
            - Legal structure
            - Location
            - History

            3. Market Analysis:
            - Target market
            - Competitive analysis
            - Market trends

            4. Organization & Management:
            - Organizational structure
            - Management team

            5. Service or Product Line:
            - Description of products/services
            - Competitive advantage

            6. Marketing & Sales:
            - Marketing strategy
            - Sales strategy

            7. Funding Request:
            - Current funding requirements
            - Future funding requirements

            8. Financial Projections:
            - Projected profit and loss
            - Cash flow projections
            """

            if self.current_language == "ru":
                plan_text = f"""
                {name} - Бизнес план
                Отрасль: {industry}

                1. Краткое описание:
                - Обзор бизнеса
                - Миссия компании
                - Цели бизнеса

                2. Описание компании:
                - Организационно-правовая форма
                - Местоположение
                - История

                3. Анализ рынка:
                - Целевая аудитория
                - Анализ конкурентов
                - Тренды рынка

                4. Организация и управление:
                - Организационная структура
                - Команда управления

                5. Продукт или услуга:
                - Описание продуктов/услуг
                - Конкурентные преимущества

                6. Маркетинг и продажи:
                - Маркетинговая стратегия
                - Стратегия продаж

                7. Финансирование:
                - Текущие потребности в финансировании
                - Будущие потребности в финансировании

                8. Финансовые прогнозы:
                - Прогноз прибылей и убытков
                - Прогноз денежных потоков
                """

            plan_display = scrolledtext.ScrolledText(plan_window, wrap=tk.WORD)
            plan_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            plan_display.insert(tk.END, plan_text)
            plan_display.config(state=tk.DISABLED)

            def save_plan():
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])

                if file_path:
                    with open(file_path, "w") as f:
                        f.write(plan_text)
                    self.bot_response(
                        f"Business plan saved: {file_path}" if self.current_language == "en"
                        else f"Бизнес план сохранен: {file_path}")

            ttk.Button(plan_window,
                       text="Save Plan" if self.current_language == "en" else "Сохранить план",
                       command=save_plan).pack(pady=5)

        ttk.Button(plan_window,
                   text="Generate" if self.current_language == "en" else "Сгенерировать",
                   command=generate).pack(pady=10)

    def open_marketing_tools(self):
        marketing_window = tk.Toplevel(self.root)
        marketing_window.title("Marketing Tools" if self.current_language == "en" else "Маркетинговые инструменты")

        ttk.Button(marketing_window,
                   text="Social Media Planner" if self.current_language == "en" else "Планировщик соцсетей",
                   command=self.open_social_media_planner).pack(pady=5)

        ttk.Button(marketing_window,
                   text="Ad Campaign Calculator" if self.current_language == "en" else "Калькулятор рекламной кампании",
                   command=self.open_ad_campaign_calculator).pack(pady=5)

        ttk.Button(marketing_window,
                   text="Content Calendar" if self.current_language == "en" else "Контент-календарь",
                   command=self.open_content_calendar).pack(pady=5)

    def open_social_media_planner(self):
        planner_window = tk.Toplevel(self.root)
        planner_window.title("Social Media Planner" if self.current_language == "en" else "Планировщик соцсетей")

        ttk.Label(planner_window,
                  text="Select Platforms:" if self.current_language == "en" else "Выберите платформы:").pack()

        platforms = ["Facebook", "Instagram", "Twitter", "LinkedIn", "YouTube"]
        platform_vars = []

        for platform in platforms:
            var = tk.IntVar()
            ttk.Checkbutton(planner_window, text=platform, variable=var).pack(anchor='w')
            platform_vars.append((platform, var))

        ttk.Label(planner_window,
                  text="Content Ideas:" if self.current_language == "en" else "Идеи контента:").pack()

        content_text = scrolledtext.ScrolledText(planner_window, height=10)
        content_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def generate_ideas():
            selected_platforms = [p for p, v in platform_vars if v.get() == 1]
            if not selected_platforms:
                messagebox.showwarning(
                    "Warning" if self.current_language == "en" else "Предупреждение",
                    "Please select at least one platform" if self.current_language == "en"
                    else "Выберите хотя бы одну платформу")
                return

            ideas = []
            for platform in selected_platforms:
                platform_ideas = [
                    f"Post a behind-the-scenes photo on {platform}",
                    f"Share a customer testimonial on {platform}",
                    f"Create a poll or survey on {platform}",
                    f"Post a promotional offer on {platform}",
                    f"Share an industry news article on {platform}"
                ]
                if self.current_language == "ru":
                    platform_ideas = [
                        f"Опубликуйте фото за кулисами в {platform}",
                        f"Поделитесь отзывом клиента в {platform}",
                        f"Создайте опрос в {platform}",
                        f"Опубликуйте специальное предложение в {platform}",
                        f"Поделитесь новостями отрасли в {platform}"
                    ]
                ideas.extend(random.sample(platform_ideas, 2))

            content_text.delete(1.0, tk.END)
            content_text.insert(tk.END, "\n".join(ideas))

        ttk.Button(planner_window,
                   text="Generate Ideas" if self.current_language == "en" else "Сгенерировать идеи",
                   command=generate_ideas).pack(pady=5)

    def open_ad_campaign_calculator(self):
        calculator_window = tk.Toplevel(self.root)
        calculator_window.title(
            "Ad Campaign Calculator" if self.current_language == "en" else "Калькулятор рекламной кампании")

        ttk.Label(calculator_window,
                  text="Budget:" if self.current_language == "en" else "Бюджет:").grid(row=0, column=0)
        budget_var = tk.StringVar(value="1000")
        ttk.Entry(calculator_window, textvariable=budget_var).grid(row=0, column=1)

        ttk.Label(calculator_window,
                  text="Duration (days):" if self.current_language == "en" else "Длительность (дни):").grid(row=1,
                                                                                                            column=0)
        duration_var = tk.StringVar(value="30")
        ttk.Entry(calculator_window, textvariable=duration_var).grid(row=1, column=1)

        ttk.Label(calculator_window,
                  text="Expected CTR (%):" if self.current_language == "en" else "Ожидаемый CTR (%):").grid(row=2,
                                                                                                            column=0)
        ctr_var = tk.StringVar(value="2")
        ttk.Entry(calculator_window, textvariable=ctr_var).grid(row=2, column=1)

        ttk.Label(calculator_window,
                  text="Conversion Rate (%):" if self.current_language == "en" else "Конверсия (%):").grid(row=3,
                                                                                                           column=0)
        conversion_var = tk.StringVar(value="5")
        ttk.Entry(calculator_window, textvariable=conversion_var).grid(row=3, column=1)

        result_var = tk.StringVar()
        ttk.Label(calculator_window, textvariable=result_var).grid(row=4, columnspan=2)

        def calculate_campaign():
            try:
                budget = float(budget_var.get())
                duration = int(duration_var.get())
                ctr = float(ctr_var.get()) / 100
                conversion = float(conversion_var.get()) / 100

                daily_budget = budget / duration
                estimated_clicks = budget * ctr
                estimated_conversions = estimated_clicks * conversion

                result_text = (
                    f"Daily Budget: ${daily_budget:.2f}\n"
                    f"Estimated Clicks: {estimated_clicks:.0f}\n"
                    f"Estimated Conversions: {estimated_conversions:.0f}"
                )

                if self.current_language == "ru":
                    result_text = (
                        f"Ежедневный бюджет: ${daily_budget:.2f}\n"
                        f"Ожидаемое количество кликов: {estimated_clicks:.0f}\n"
                        f"Ожидаемое количество конверсий: {estimated_conversions:.0f}"
                    )
                result_var.set(result_text)
            except Exception as e:
                result_var.set("Error" if self.current_language == "en" else "Ошибка")

        ttk.Button(calculator_window,
                   text="Calculate" if self.current_language == "en" else "Рассчитать",
                   command=calculate_campaign).grid(row=5, columnspan=2, pady=5)

    def open_content_calendar(self):
        calendar_window = tk.Toplevel(self.root)
        calendar_window.title("Content Calendar" if self.current_language == "en" else "Контент-календарь")

        sample_content = """
                Monday:
                - Facebook: Industry news post
                - Instagram: Product photo

                Tuesday:
                - Twitter: Poll or question
                - LinkedIn: Article share

                Wednesday:
                - YouTube: New video
                - Instagram: Story update

                Thursday:
                - Facebook: Customer testimonial
                - Twitter: Promotional offer

                Friday:
                - LinkedIn: Company update
                - Instagram: Behind-the-scenes
                """
        if self.current_language == "ru":
            sample_content = """
                    Понедельник:
                    - Facebook: Новости отрасли
                    - Instagram: Фото продукта

                    Вторник:
                    - Twitter: Опрос или вопрос
                    - LinkedIn: Поделиться статьей

                    Среда:
                    - YouTube: Новое видео
                    - Instagram: Обновление в сторис

                    Четверг:
                    - Facebook: Отзыв клиента
                    - Twitter: Специальное предложение

                    Пятница:
                    - LinkedIn: Новости компании
                    - Instagram: Закулисье
                    """

        content_text = scrolledtext.ScrolledText(calendar_window, wrap=tk.WORD)
        content_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        content_text.insert(tk.END, sample_content)

        def save_calendar():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])

            if file_path:
                with open(file_path, "w") as f:
                    f.write(content_text.get(1.0, tk.END))
                self.bot_response(
                    f"Content calendar saved: {file_path}" if self.current_language == "en"
                    else f"Контент-календарь сохранен: {file_path}")

                ttk.Button(calendar_window,
                           text="Save Calendar" if self.current_language == "en" else "Сохранить календарь",
                           command=save_calendar).pack(pady=5)

            def open_game_selector(self):
                game_window = tk.Toplevel(self.root)
                game_window.title("Games" if self.current_language == "en" else "Игры")

                ttk.Button(game_window,
                           text="Snake Game" if self.current_language == "en" else "Змейка",
                           command=lambda: self.start_game("snake")).pack(pady=5)

                ttk.Button(game_window,
                           text="Ping Pong" if self.current_language == "en" else "Пинг-понг",
                           command=lambda: self.start_game("pong")).pack(pady=5)

                ttk.Button(game_window,
                           text="Memory Game" if self.current_language == "en" else "Игра на память",
                           command=lambda: self.start_game("memory")).pack(pady=5)

            def start_game(self, game_type):
                if self.game_window and tk.Toplevel.winfo_exists(self.game_window):
                    self.game_window.destroy()

                self.game_window = tk.Toplevel(self.root)
                self.game_window.title(game_type.capitalize())
                self.game_type = game_type
                self.game_running = True

                if game_type == "snake":
                    self.setup_snake_game()
                elif game_type == "pong":
                    self.setup_pong_game()
                elif game_type == "memory":
                    self.setup_memory_game()

                self.game_window.protocol("WM_DELETE_WINDOW", self.stop_game)

            def stop_game(self):
                self.game_running = False
                if self.game_window:
                    self.game_window.destroy()
                self.game_window = None

            def setup_snake_game(self):
                self.canvas = tk.Canvas(self.game_window, width=400, height=400, bg='black')
                self.canvas.pack()

                self.snake = [(200, 200), (210, 200), (220, 200)]
                self.snake_direction = "Left"
                self.food = self.create_food()
                self.score = 0

                self.score_label = ttk.Label(self.game_window,
                                             text=f"Score: {self.score}" if self.current_language == "en"
                                             else f"Счет: {self.score}")
                self.score_label.pack()

                self.game_window.bind("<KeyPress>", self.change_snake_direction)
                self.update_snake()

            def create_food(self):
                x = random.randint(0, 39) * 10
                y = random.randint(0, 39) * 10
                self.food_pos = (x, y)
                return self.canvas.create_oval(x, y, x + 10, y + 10, fill='red')

            def change_snake_direction(self, event):
                if event.keysym in ["Up", "Down", "Left", "Right"]:
                    self.snake_direction = event.keysym

            def update_snake(self):
                if not self.game_running:
                    return

                head_x, head_y = self.snake[0]

                if self.snake_direction == "Up":
                    new_head = (head_x, head_y - 10)
                elif self.snake_direction == "Down":
                    new_head = (head_x, head_y + 10)
                elif self.snake_direction == "Left":
                    new_head = (head_x - 10, head_y)
                elif self.snake_direction == "Right":
                    new_head = (head_x + 10, head_y)

                if (new_head in self.snake or
                        new_head[0] < 0 or new_head[0] >= 400 or
                        new_head[1] < 0 or new_head[1] >= 400):
                    self.game_over()
                    return

                self.snake.insert(0, new_head)

                if new_head == self.food_pos:
                    self.score += 1
                    self.score_label.config(
                        text=f"Score: {self.score}" if self.current_language == "en"
                        else f"Счет: {self.score}")
                    self.canvas.delete(self.food)
                    self.food = self.create_food()
                else:
                    self.snake.pop()

                self.canvas.delete("snake")
                for segment in self.snake:
                    self.canvas.create_rectangle(
                        segment[0], segment[1], segment[0] + 10, segment[1] + 10,
                        fill='green', tags="snake")

                self.game_window.after(100, self.update_snake)

            def game_over(self):
                self.game_running = False
                self.canvas.create_text(200, 200,
                                        text="GAME OVER" if self.current_language == "en" else "ИГРА ОКОНЧЕНА",
                                        fill='white', font=('Helvetica', 20))

            def setup_pong_game(self):
                self.canvas = tk.Canvas(self.game_window, width=400, height=400, bg='black')
                self.canvas.pack()

                self.paddle_a = self.canvas.create_rectangle(0, 150, 10, 250, fill='white')
                self.paddle_b = self.canvas.create_rectangle(390, 150, 400, 250, fill='white')
                self.ball = self.canvas.create_oval(195, 195, 205, 205, fill='white')

                self.ball_dx = 2
                self.ball_dy = 2
                self.score_a = 0
                self.score_b = 0

                self.score_label = ttk.Label(self.game_window,
                                             text=f"Player A: {self.score_a}  Player B: {self.score_b}")
                self.score_label.pack()

                self.game_window.bind("<KeyPress>", self.move_paddles)
                self.update_pong()

            def move_paddles(self, event):
                if event.keysym == "w":
                    self.canvas.move(self.paddle_a, 0, -20)
                elif event.keysym == "s":
                    self.canvas.move(self.paddle_a, 0, 20)
                elif event.keysym == "Up":
                    self.canvas.move(self.paddle_b, 0, -20)
                elif event.keysym == "Down":
                    self.canvas.move(self.paddle_b, 0, 20)

            def update_pong(self):
                if not self.game_running:
                    return

                self.canvas.move(self.ball, self.ball_dx, self.ball_dy)
                ball_pos = self.canvas.coords(self.ball)
                paddle_a_pos = self.canvas.coords(self.paddle_a)
                paddle_b_pos = self.canvas.coords(self.paddle_b)

                if ball_pos[1] <= 0 or ball_pos[3] >= 400:
                    self.ball_dy = -self.ball_dy

                if (ball_pos[0] <= paddle_a_pos[2] and
                        ball_pos[1] >= paddle_a_pos[1] and
                        ball_pos[3] <= paddle_a_pos[3]):
                    self.ball_dx = -self.ball_dx
                elif (ball_pos[2] >= paddle_b_pos[0] and
                      ball_pos[1] >= paddle_b_pos[1] and
                      ball_pos[3] <= paddle_b_pos[3]):
                    self.ball_dx = -self.ball_dx

                if ball_pos[0] <= 0:
                    self.score_b += 1
                    self.reset_ball()
                elif ball_pos[2] >= 400:
                    self.score_a += 1
                    self.reset_ball()

                self.score_label.config(text=f"Player A: {self.score_a}  Player B: {self.score_b}")
                self.game_window.after(10, self.update_pong)

            def reset_ball(self):
                self.canvas.coords(self.ball, 195, 195, 205, 205)
                self.ball_dx = -self.ball_dx if random.random() > 0.5 else self.ball_dx
                self.ball_dy = -self.ball_dy if random.random() > 0.5 else self.ball_dy

            def setup_memory_game(self):
                self.canvas = tk.Canvas(self.game_window, width=400, height=400, bg='white')
                self.canvas.pack()

                self.tiles = []
                self.colors = ['red', 'blue', 'green', 'yellow',
                               'purple', 'orange', 'cyan', 'magenta',
                               'red', 'blue', 'green', 'yellow',
                               'purple', 'orange', 'cyan', 'magenta']
                random.shuffle(self.colors)

                self.flipped = []
                self.matched = []
                self.moves = 0

                for i in range(16):
                    row = i // 4
                    col = i % 4
                    tile = self.canvas.create_rectangle(
                        col * 100, row * 100,
                        (col + 1) * 100, (row + 1) * 100,
                        fill='gray', outline='black')
                    self.tiles.append(tile)
                    self.canvas.tag_bind(tile, '<Button-1>', lambda e, idx=i: self.flip_tile(idx))

                self.score_label = ttk.Label(self.game_window,
                                             text=f"Moves: {self.moves}" if self.current_language == "en"
                                             else f"Ходы: {self.moves}")
                self.score_label.pack()

            def flip_tile(self, idx):
                if idx in self.flipped or idx in self.matched or len(self.flipped) >= 2:
                    return

                self.flipped.append(idx)
                self.canvas.itemconfig(self.tiles[idx], fill=self.colors[idx])

                if len(self.flipped) == 2:
                    self.moves += 1
                    self.score_label.config(
                        text=f"Moves: {self.moves}" if self.current_language == "en"
                        else f"Ходы: {self.moves}")

                    if self.colors[self.flipped[0]] == self.colors[self.flipped[1]]:
                        self.matched.extend(self.flipped)
                        self.flipped = []
                        if len(self.matched) == 16:
                            self.game_window.after(500, self.game_won)
                    else:
                        self.game_window.after(1000, self.hide_tiles)

            def hide_tiles(self):
                for idx in self.flipped:
                    self.canvas.itemconfig(self.tiles[idx], fill='gray')
                self.flipped = []

            def game_won(self):
                self.canvas.create_text(200, 200,
                                        text=f"You won in {self.moves} moves!" if self.current_language == "en"
                                        else f"Вы выиграли за {self.moves} ходов!",
                                        fill='black', font=('Helvetica', 16))
                self.game_running = False

if __name__ == "__main__":
        root = tk.Tk()
        app = ChatBotApp(root)
        root.mainloop() 
