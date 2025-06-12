import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from matplotlib.widgets import Cursor

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
        self.crypto_currencies = ['BTC', 'ETH', 'XRP', 'LTC', 'BCH', 'ADA', 'DOT', 'DOGE']

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

        chart_btn = ttk.Button(self.root, text="Графики", command=self.show_chart_options)
        chart_btn.pack(pady=5)

    def update_currencies(self):
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
            data = response.json()
            currencies = list(data["rates"].keys()) + self.crypto_currencies
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

            if from_curr in self.crypto_currencies or to_curr in self.crypto_currencies:
                if from_curr in self.crypto_currencies and to_curr in self.crypto_currencies:
                    response1 = requests.get(
                        f"https://api.coingecko.com/api/v3/simple/price?ids={self.get_coin_id(from_curr)}&vs_currencies=usd")
                    response2 = requests.get(
                        f"https://api.coingecko.com/api/v3/simple/price?ids={self.get_coin_id(to_curr)}&vs_currencies=usd")
                    rate1 = response1.json()[self.get_coin_id(from_curr)]['usd']
                    rate2 = response2.json()[self.get_coin_id(to_curr)]['usd']
                    rate = rate1 / rate2
                elif from_curr in self.crypto_currencies:
                    response = requests.get(
                        f"https://api.coingecko.com/api/v3/simple/price?ids={self.get_coin_id(from_curr)}&vs_currencies=usd")
                    crypto_rate = response.json()[self.get_coin_id(from_curr)]['usd']
                    usd_to_curr = requests.get(f"https://api.exchangerate-api.com/v4/latest/USD").json()["rates"][
                        to_curr]
                    rate = crypto_rate * usd_to_curr
                else:
                    usd_to_curr = \
                    requests.get(f"https://api.exchangerate-api.com/v4/latest/{from_curr}").json()["rates"]["USD"]
                    response = requests.get(
                        f"https://api.coingecko.com/api/v3/simple/price?ids={self.get_coin_id(to_curr)}&vs_currencies=usd")
                    crypto_rate = response.json()[self.get_coin_id(to_curr)]['usd']
                    rate = (1 / usd_to_curr) * (1 / crypto_rate)
            else:
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

    def get_coin_id(self, symbol):
        coin_ids = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'XRP': 'ripple',
            'LTC': 'litecoin',
            'BCH': 'bitcoin-cash',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'DOGE': 'dogecoin'
        }
        return coin_ids.get(symbol, 'bitcoin')

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("История конвертаций")
        history_window.geometry("400x300")

        text = tk.Text(history_window, bg="#2d2d2d", fg="white", font=("Consolas", 10))
        text.pack(fill="both", expand=True)

        for entry in self.history:
            text.insert("end", entry + "\n")
        text.config(state="disabled")

    def show_chart_options(self):
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Настройки графика")
        chart_window.geometry("400x300")
        chart_window.configure(bg="#2d2d2d")

        ttk.Label(chart_window, text="Выберите период:").pack(pady=10)

        period_var = tk.StringVar(value="all")

        periods = [
            ("За день", "day"),
            ("За неделю", "week"),
            ("За месяц", "month"),
            ("За год", "year"),
            ("Все время", "all")
        ]

        for text, mode in periods:
            ttk.Radiobutton(
                chart_window,
                text=text,
                variable=period_var,
                value=mode
            ).pack(anchor="w", padx=50)

        ttk.Label(chart_window, text="Выберите валюту:").pack(pady=10)
        currency_var = tk.StringVar()
        currency_combobox = ttk.Combobox(chart_window, textvariable=currency_var)
        currency_combobox["values"] = list(self.rates_history.keys()) + self.crypto_currencies
        currency_combobox.pack()

        ttk.Label(chart_window, text="Курс к:").pack(pady=5)
        to_currency_var = tk.StringVar(value="USD")
        to_currency_combobox = ttk.Combobox(chart_window, textvariable=to_currency_var)
        to_currency_combobox["values"] = list(self.rates_history.keys()) + self.crypto_currencies
        to_currency_combobox.pack()

        def show_selected_chart():
            currency = currency_var.get()
            to_currency = to_currency_var.get()
            period = period_var.get()

            if not currency or not to_currency:
                messagebox.showwarning("Ошибка", "Выберите валюту и целевую валюту")
                return

            chart_window.destroy()
            self.show_chart(currency, to_currency, period)

        ttk.Button(
            chart_window,
            text="Показать график",
            command=show_selected_chart
        ).pack(pady=20)

    def show_chart(self, from_curr, to_curr, period="all"):
        try:
            end_date = datetime.now()

            if period == "day":
                start_date = end_date - timedelta(days=1)
            elif period == "week":
                start_date = end_date - timedelta(weeks=1)
            elif period == "month":
                start_date = end_date - timedelta(days=30)
            elif period == "year":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=365 * 5)

            if from_curr in self.crypto_currencies:
                coin_id = self.get_coin_id(from_curr)
                vs_currency = to_curr.lower() if to_curr not in self.crypto_currencies else 'usd'

                days = (end_date - start_date).days
                url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency={vs_currency}&days={days}"
                response = requests.get(url)
                data = response.json()

                dates = [datetime.fromtimestamp(item[0] / 1000) for item in data['prices']]
                prices = [item[1] for item in data['prices']]

                if to_curr in self.crypto_currencies and from_curr != to_curr:
                    coin_id2 = self.get_coin_id(to_curr)
                    url2 = f"https://api.coingecko.com/api/v3/coins/{coin_id2}/market_chart?vs_currency=usd&days={days}"
                    response2 = requests.get(url2)
                    data2 = response2.json()
                    prices2 = [item[1] for item in data2['prices']]
                    prices = [p1 / p2 for p1, p2 in zip(prices, prices2)]
            else:
                dates = []
                prices = []
                for i in range((end_date - start_date).days + 1):
                    date = start_date + timedelta(days=i)
                    try:
                        response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{from_curr}")
                        data = response.json()
                        rate = data["rates"][to_curr]
                        dates.append(date)
                        prices.append(rate)
                    except:
                        continue

            if not dates or not prices:
                messagebox.showwarning("Ошибка", "Недостаточно данных для построения графика")
                return

            fig = plt.figure(figsize=(8, 5), facecolor="#2d2d2d")
            ax = fig.add_subplot(111)
            line, = ax.plot(dates, prices, marker='o', color='#4CAF50', markersize=4)

            if period == "day":
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            elif period == "week":
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
            elif period == "month":
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
            elif period == "year":
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

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

            annot = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="#3d3d3d", ec="#4CAF50", lw=2),
                                arrowprops=dict(arrowstyle="->"))
            annot.set_visible(False)
            annot.set_color('white')

            def update_annot(ind):
                x, y = line.get_data()
                annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
                text = f"{x[ind['ind'][0]].strftime('%Y-%m-%d %H:%M')}\n{y[ind['ind'][0]]:.4f} {to_curr}"
                annot.set_text(text)
                annot.get_bbox_patch().set_alpha(0.8)

            def hover(event):
                vis = annot.get_visible()
                if event.inaxes == ax:
                    cont, ind = line.contains(event)
                    if cont:
                        update_annot(ind)
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                    else:
                        if vis:
                            annot.set_visible(False)
                            fig.canvas.draw_idle()

            fig.canvas.mpl_connect("motion_notify_event", hover)

            chart_window = tk.Toplevel(self.root)
            chart_window.title(f"График курса {from_curr} к {to_curr}")
            chart_window.geometry("800x600")

            canvas = FigureCanvasTkAgg(fig, master=chart_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            toolbar_frame = ttk.Frame(chart_window)
            toolbar_frame.pack(fill=tk.X)

            save_btn = ttk.Button(toolbar_frame, text="Сохранить график",
                                  command=lambda: self.save_figure(fig))
            save_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось построить график: {e}")

    def save_figure(self, fig):
        try:
            filename = f"currency_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            fig.savefig(filename, dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
            messagebox.showinfo("Успех", f"График сохранен как {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить график: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
