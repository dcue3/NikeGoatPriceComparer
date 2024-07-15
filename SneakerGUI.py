import csv
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import pandas as pd
import subprocess

# Class contains implementation of program GUI, allows URL input and data display.
class SneakerScraperApp:
    def __init__(self, root):  # Initialize GUI
        self.root = root
        self.root.title("Nike X Goat Price Comparison")

        self.sort_column = None
        self.sort_order = None

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=1, fill='both')

        self.create_scraper_tab()
        self.create_ml_tab()

    def create_scraper_tab(self):
        self.scraper_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.scraper_tab, text="Scraper")

        self.url_label = tk.Label(self.scraper_tab, text="Enter URL:")
        self.url_label.pack(pady=5)
        self.url_entry = tk.Entry(self.scraper_tab, width=50)
        self.url_entry.pack(pady=5)

        self.parser_var = tk.StringVar(value="Nike")
        self.nike_radio = tk.Radiobutton(self.scraper_tab, text="Nike Link", variable=self.parser_var, value="Nike")
        self.goat_radio = tk.Radiobutton(self.scraper_tab, text="Goat Link", variable=self.parser_var, value="Goat")
        self.nike_radio.pack(pady=5)
        self.goat_radio.pack(pady=5)

        self.filter_profit_var = tk.BooleanVar()
        self.filter_profit_checkbox = tk.Checkbutton(self.scraper_tab, text="Filter for profit?", variable=self.filter_profit_var)
        self.filter_profit_checkbox.pack(pady=5)

        self.overwrite_csv_var = tk.BooleanVar()
        self.overwrite_csv_checkbox = tk.Checkbutton(self.scraper_tab, text="Overwrite existing CSV?", variable=self.overwrite_csv_var)
        self.overwrite_csv_checkbox.pack(pady=5)

        self.run_button = tk.Button(self.scraper_tab, text="Run Parser", command=self.run_parser)
        self.run_button.pack(pady=10)

        self.load_button = tk.Button(self.scraper_tab, text="Load CSV", command=self.load_csv)
        self.load_button.pack(pady=10)

        self.columns = ['SKU', 'Name', 'Profit ($)', 'Profit (%)', 'Retail Price ($)', 'Resale Price ($)', 'Year', 'Nike Link', 'Goat Link']
        self.tree = ttk.Treeview(self.scraper_tab, columns=self.columns, show='headings')

        for column in self.columns:
            self.tree.heading(column, text=column, command=lambda _col=column: self.sort_treeview(_col))
            self.tree.column(column, width=150, anchor='center')

        self.tree.pack(pady=20)
        self.tree.bind("<ButtonRelease-1>", self.copy_to_clipboard)

    def create_ml_tab(self):
        self.ml_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.ml_tab, text="ML Model")

        self.file_label = tk.Label(self.ml_tab, text="Select CSV file for training:")
        self.file_label.pack(pady=5)
        self.file_button = tk.Button(self.ml_tab, text="Browse", command=self.browse_file)
        self.file_button.pack(pady=5)

        self.train_button = tk.Button(self.ml_tab, text="Train Model", command=self.train_model)
        self.train_button.pack(pady=10)

        self.stats_label = tk.Label(self.ml_tab, text="")
        self.stats_label.pack(pady=10)

        self.name_label = tk.Label(self.ml_tab, text="Shoe Name:")
        self.name_label.pack(pady=5)
        self.name_entry = tk.Entry(self.ml_tab, width=30)
        self.name_entry.pack(pady=5)

        self.retail_price_label = tk.Label(self.ml_tab, text="Retail Price ($):")
        self.retail_price_label.pack(pady=5)
        self.retail_price_entry = tk.Entry(self.ml_tab, width=30)
        self.retail_price_entry.pack(pady=5)

        self.year_label = tk.Label(self.ml_tab, text="Year:")
        self.year_label.pack(pady=5)
        self.year_entry = tk.Entry(self.ml_tab, width=30)
        self.year_entry.pack(pady=5)

        self.predict_button = tk.Button(self.ml_tab, text="Predict Resale Price", command=self.predict_resale_price)
        self.predict_button.pack(pady=10)

        self.prediction_label = tk.Label(self.ml_tab, text="")
        self.prediction_label.pack(pady=10)

    def run_parser(self):  # Pass URL and run appropriate parser script
        url = self.url_entry.get()
        filter_profit = self.filter_profit_var.get()
        overwrite_csv = self.overwrite_csv_var.get()
        parser = self.parser_var.get()

        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return

        script_name = "NikeParser.py" if parser == "Nike" else "GoatParser.py"
        command = ["python3", script_name, url]
        if filter_profit:
            command.append("--filter-profit")
        if overwrite_csv:
            command.append("--overwrite-csv")

        try:
            subprocess.run(command, check=True)
            messagebox.showinfo("Success", "Data obtained successfully. Now loading the results.")
            self.load_csv()  # Load the resulting CSV file
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to run parser: {e}")

    def load_csv(self):  # Open CSV file created by parser script
        file_path = "NikeParserResults.csv"
        try:
            df = pd.read_csv(file_path, dtype={'Year': str})
            self.process_data(df)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file: {e}")

    def process_data(self, df):  # Add data to view
        required_columns = ['SKU', 'Name', 'Profit ($)', 'Profit (%)', 'Retail Price ($)', 'Resale Price ($)', 'Year', 'Nike Link', 'Goat Link']
        if not all(column in df.columns for column in required_columns):
            messagebox.showerror("Error", "CSV file does not contain required columns")
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        for _, row in df.iterrows():
            self.tree.insert('', tk.END, values=(
                row['SKU'], row['Name'], row['Profit ($)'], row['Profit (%)'], row['Retail Price ($)'], row['Resale Price ($)'],
                row['Year'], row['Nike Link'], row['Goat Link']))

    def copy_to_clipboard(self, event):  # Copy cell when clicked
        region = self.tree.identify("region", event.x, event.y)
        if region == "heading":
            return

        item = self.tree.identify('item', event.x, event.y)
        column = self.tree.identify_column(event.x)
        if item and column:
            cell_value = self.tree.item(item, "values")[int(column[1:]) - 1]
            self.root.clipboard_clear()
            self.root.clipboard_append(cell_value)
            messagebox.showinfo("Copied", f"Copied to clipboard: {cell_value}")

    def sort_treeview(self, col):  # Sort data when column header is clicked
        data_list = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]

        if col in ['Profit ($)', 'Profit (%)', 'Retail Price ($)', 'Resale Price ($)']:
            data_list = [(float(v[0].replace('$', '').replace('%', '')), v[1]) for v in data_list]

        data_list.sort(reverse=self.sort_order != "ASC")

        for index, (_, k) in enumerate(data_list):
            self.tree.move(k, '', index)

        self.sort_order = "ASC" if self.sort_order != "ASC" else "DESC"
        self.sort_column = col

    def browse_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        self.file_label.config(text=f"Selected file: {self.file_path}")

    def train_model(self):
        if not hasattr(self, 'file_path') or not self.file_path:
            messagebox.showerror("Error", "Please select a CSV file")
            return

        command = ["python3", "NikeGoatML.py", self.file_path]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            self.stats_label.config(text=result.stdout)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to train model: {e}")

    def predict_resale_price(self):
        name = self.name_entry.get()
        try:
            retail_price = float(self.retail_price_entry.get())
            year = int(self.year_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for retail price and year")
            return

        command = ["python3", "predict_resale.py", name, str(retail_price), str(year)]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            self.prediction_label.config(text=result.stdout)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to predict resale price: {e}")


if __name__ == "__main__":  # Main
    root = tk.Tk()
    app = SneakerScraperApp(root)
    root.mainloop()
