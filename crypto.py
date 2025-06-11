import requests
import tkinter as tk
from tkinter import ttk

class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Tracker")
        self.root.geometry("600x400")

        self.setup_ui()
        self.fetch_data()

    def setup_ui(self):
        self.tree = ttk.Treeview(self.root, columns=("Name", "Price", "Change"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Price", text="Price (USD)")
        self.tree.heading("Change", text="24h Change")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.refresh_button = tk.Button(self.root, text="Refresh", command=self.fetch_data)
        self.refresh_button.pack(pady=10)

    def fetch_data(self):
        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc")
            data = response.json()
            self.update_tree(data)
        except Exception as e:
            print(f"Error fetching data: {e}")

    def update_tree(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for coin in data[:20]:
            name = coin['name']
            price = coin['current_price']
            change = coin['price_change_percentage_24h']

            self.tree.insert("", tk.END, values=(name, f"${price:,.2f}", f"{change:.2f}%"))


if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()
