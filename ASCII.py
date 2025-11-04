import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import numpy as np
import os
from PIL import Image, ImageTk
import threading


class ASCIIVideoConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCII Video Converter")
        self.root.geometry("800x600")

        self._input_path = ""
        self._output_path = ""
        self.is_processing = False
        self.preview_frame = None

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        title_label = ttk.Label(main_frame, text="ASCII Video Converter",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        ttk.Label(main_frame, text="Входное видео:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.input_entry = ttk.Entry(main_frame, width=50)
        self.input_entry.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(main_frame, text="Обзор", command=self.browse_input).grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(main_frame, text="Выходное видео:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_entry = ttk.Entry(main_frame, width=50)
        self.output_entry.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(main_frame, text="Обзор", command=self.browse_output).grid(row=2, column=2, padx=5, pady=5)

        settings_frame = ttk.LabelFrame(main_frame, text="Настройки", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(settings_frame, text="Ширина ASCII (символов):").grid(row=0, column=0, sticky=tk.W)
        self.width_var = tk.StringVar(value="150")
        ttk.Entry(settings_frame, textvariable=self.width_var, width=10).grid(row=0, column=1, padx=5)

        ttk.Label(settings_frame, text="Набор символов:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.chars_var = tk.StringVar(value="@%#*+=-:. ")
        ttk.Entry(settings_frame, textvariable=self.chars_var, width=20).grid(row=1, column=1, padx=5)

        ttk.Label(settings_frame, text="Размер шрифта:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.font_size_var = tk.StringVar(value="6")
        ttk.Entry(settings_frame, textvariable=self.font_size_var, width=10).grid(row=2, column=1, padx=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)

        ttk.Button(button_frame, text="Предпросмотр", command=self.preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Конвертировать", command=self.start_conversion).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Остановить", command=self.stop_conversion).pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        self.status_var = tk.StringVar(value="Готов к работе")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=6, column=0, columnspan=3)

        preview_frame = ttk.LabelFrame(main_frame, text="Предпросмотр", padding="10")
        preview_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        self.preview_label = ttk.Label(preview_frame, text="Предпросмотр появится здесь",
                                       background="white", anchor="center")
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Выберите видео файл",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        )
        if filename:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, filename)
            self._input_path = filename

    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Сохранить как",
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("All files", "*.*")]
        )
        if filename:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, filename)
            self._output_path = filename

    def image_to_ascii(self, image, width=150, chars="@%#*+=-:. "):
        original_height, original_width = image.shape[:2]
        aspect_ratio = original_height / original_width

        height = int(width * aspect_ratio / 1.8)

        resized = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        normalized = gray / 255.0
        char_indices = (normalized * (len(chars) - 1)).astype(int)

        ascii_art = []
        for row in char_indices:
            ascii_row = ''.join(chars[pixel] for pixel in row)
            ascii_art.append(ascii_row)

        return ascii_art

    def ascii_to_image(self, ascii_art, font_size=6):
        height = len(ascii_art)
        width = len(ascii_art[0])

        from PIL import Image, ImageDraw, ImageFont

        try:
            font = ImageFont.truetype("Courier New", font_size)
        except:
            try:
                font = ImageFont.truetype("DejaVuSansMono", font_size)
            except:
                font = ImageFont.load_default()

        bbox = font.getbbox("A")
        char_width = bbox[2] - bbox[0]
        char_height = bbox[3] - bbox[1]

        img_width = char_width * width
        img_height = char_height * height

        image = Image.new('RGB', (img_width, img_height), color='black')
        draw = ImageDraw.Draw(image)

        y = 0
        for line in ascii_art:
            draw.text((0, y), line, fill='white', font=font)
            y += char_height

        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    def preview(self):
        if not self.input_entry.get():
            messagebox.showerror("Ошибка", "Выберите входной файл")
            return

        try:
            cap = cv2.VideoCapture(self.input_entry.get())
            ret, frame = cap.read()
            if ret:
                ascii_art = self.image_to_ascii(
                    frame,
                    width=int(self.width_var.get()),
                    chars=self.chars_var.get()
                )
                preview_img = self.ascii_to_image(ascii_art, font_size=int(self.font_size_var.get()))

                preview_img_rgb = cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB)
                preview_pil = Image.fromarray(preview_img_rgb)

                preview_pil.thumbnail((400, 300), Image.Resampling.LANCZOS)
                preview_tk = ImageTk.PhotoImage(preview_pil)

                self.preview_label.configure(image=preview_tk)
                self.preview_label.image = preview_tk

            cap.release()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при предпросмотре: {str(e)}")

    def start_conversion(self):
        if not self.input_entry.get():
            messagebox.showerror("Ошибка", "Выберите входной файл")
            return

        if not self.output_entry.get():
            messagebox.showerror("Ошибка", "Выберите выходной файл")
            return

        if self.is_processing:
            messagebox.showwarning("Внимание", "Конвертация уже выполняется")
            return

        self.is_processing = True
        self.status_var.set("Конвертация начата...")

        thread = threading.Thread(target=self.convert_video)
        thread.daemon = True
        thread.start()

    def stop_conversion(self):
        self.is_processing = False
        self.status_var.set("Конвертация остановлена")

    def convert_video(self):
        try:
            cap = cv2.VideoCapture(self._input_path)
            if not cap.isOpened():
                raise Exception("Не удалось открыть видео файл")

            input_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            ascii_width = int(self.width_var.get())
            chars = self.chars_var.get()
            font_size = int(self.font_size_var.get())

            ret, frame = cap.read()
            if not ret:
                raise Exception("Не удалось прочитать первый кадр")

            ascii_art = self.image_to_ascii(frame, ascii_width, chars)
            preview_img = self.ascii_to_image(ascii_art, font_size=font_size)
            height, width = preview_img.shape[:2]

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(self._output_path, fourcc, input_fps, (width, height))

            frame_count = 0
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            while self.is_processing and frame_count < total_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                ascii_art = self.image_to_ascii(frame, ascii_width, chars)
                ascii_frame = self.ascii_to_image(ascii_art, font_size=font_size)

                out.write(ascii_frame)

                frame_count += 1
                progress = (frame_count / total_frames) * 100

                self.root.after(0, self.update_progress, progress, frame_count, total_frames)

            cap.release()
            out.release()

            if self.is_processing:
                self.root.after(0, self.conversion_complete)
            else:
                self.root.after(0, self.conversion_stopped)

        except Exception as e:
            self.root.after(0, self.conversion_error, str(e))

    def update_progress(self, progress, current, total):
        self.progress['value'] = progress
        self.status_var.set(f"Обработано: {current}/{total} кадров ({progress:.1f}%)")

    def conversion_complete(self):
        self.is_processing = False
        self.status_var.set("Конвертация завершена!")
        messagebox.showinfo("Успех", "Видео успешно сконвертировано!")
        self.progress['value'] = 0

    def conversion_stopped(self):
        self.is_processing = False
        self.status_var.set("Конвертация остановлена")
        self.progress['value'] = 0

    def conversion_error(self, error_msg):
        self.is_processing = False
        self.status_var.set("Ошибка конвертации")
        messagebox.showerror("Ошибка", f"Ошибка при конвертации: {error_msg}")
        self.progress['value'] = 0


def main():
    root = tk.Tk()
    app = ASCIIVideoConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
