import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Крутой Конвертер Валют 💰")
        self.root.geometry("600x600")
        self.root.configure(bg="#2d2d2d")

        self.amount_var = tk.DoubleVar()
        self.from_currency_var = tk.StringVar()
        self.to_currency_var = tk.StringVar()
        self.result_var = tk.StringVar()
        self.history = []
        self.rates_history = {}

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#2d2d2d")
        self.style.configure("TLabel", background="#2d2d2d", foreground="white")
        self.style.configure("TButton", background="#3d3d3d", foreground="white")
        self.style.configure("TEntry", fieldbackground="#3d3d3d", foreground="white")

        self.create_widgets()
        self.update_currencies()

    def create_widgets(self):
        title = ttk.Label(self.root, text="Конвертер Валют", font=("Helvetica", 20, "bold"))
        title.pack(pady=10)

        frame = ttk.Frame(self.root)
        frame.pack(pady=20)

        ttk.Label(frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        amount_entry = ttk.Entry(frame, textvariable=self.amount_var, width=15)
        amount_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Из:").grid(row=1, column=0, padx=5, pady=5)
        self.from_combobox = ttk.Combobox(frame, textvariable=self.from_currency_var, width=12)
        self.from_combobox.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="В:").grid(row=2, column=0, padx=5, pady=5)
        self.to_combobox = ttk.Combobox(frame, textvariable=self.to_currency_var, width=12)
        self.to_combobox.grid(row=2, column=1, padx=5, pady=5)

        convert_btn = ttk.Button(frame, text="Конвертировать", command=self.convert)
        convert_btn.grid(row=3, columnspan=2, pady=10)

        result_frame = ttk.Frame(self.root)
        result_frame.pack(pady=10)

        ttk.Label(result_frame, text="Результат:").pack()
        result_label = ttk.Label(result_frame, textvariable=self.result_var, font=("Helvetica", 14, "bold"))
        result_label.pack()

        history_btn = ttk.Button(self.root, text="Показать историю", command=self.show_history)
        history_btn.pack(pady=5)

        chart_btn = ttk.Button(self.root, text="Показать график", command=self.show_chart)
        chart_btn.pack(pady=5)

    def update_currencies(self):
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
            data = response.json()
            currencies = list(data["rates"].keys())
            self.from_combobox["values"] = currencies
            self.to_combobox["values"] = currencies
            self.from_currency_var.set("USD")
            self.to_currency_var.set("RUB")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить валюты: {e}")

    def convert(self):
        try:
            amount = self.amount_var.get()
            from_curr = self.from_currency_var.get()
            to_curr = self.to_currency_var.get()

            if not amount or not from_curr or not to_curr:
                messagebox.showwarning("Ошибка", "Заполните все поля!")
                return

            response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{from_curr}")
            data = response.json()
            rate = data["rates"][to_curr]
            result = round(amount * rate, 2)

            self.result_var.set(f"{amount} {from_curr} = {result} {to_curr}")

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.history.append(f"{timestamp}: {amount} {from_curr} → {result} {to_curr}")

            if from_curr not in self.rates_history:
                self.rates_history[from_curr] = {}
            if to_curr not in self.rates_history[from_curr]:
                self.rates_history[from_curr][to_curr] = []
            self.rates_history[from_curr][to_curr].append((timestamp, rate))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось конвертировать: {e}")

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("История конвертаций")
        history_window.geometry("400x300")

        text = tk.Text(history_window, bg="#2d2d2d", fg="white", font=("Consolas", 10))
        text.pack(fill="both", expand=True)

        for entry in self.history:
            text.insert("end", entry + "\n")
        text.config(state="disabled")

    def show_chart(self):
        from_curr = self.from_currency_var.get()
        to_curr = self.to_currency_var.get()

        if from_curr not in self.rates_history or to_curr not in self.rates_history[from_curr]:
            messagebox.showwarning("Ошибка", "Недостаточно данных для построения графика")
            return

        data = self.rates_history[from_curr][to_curr]
        dates = [datetime.strptime(item[0], "%Y-%m-%d %H:%M:%S") for item in data]
        rates = [item[1] for item in data]

        fig = plt.figure(figsize=(6, 4), facecolor="#2d2d2d")
        ax = fig.add_subplot(111)
        ax.plot(dates, rates, marker='o', color='#4CAF50')
        ax.set_title(f"Курс {from_curr} к {to_curr}", color='white')
        ax.set_xlabel("Дата", color='white')
        ax.set_ylabel("Курс", color='white')
        ax.set_facecolor("#2d2d2d")
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')

        chart_window = tk.Toplevel(self.root)
        chart_window.title("График курса")
        chart_window.geometry("600x500")

        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
