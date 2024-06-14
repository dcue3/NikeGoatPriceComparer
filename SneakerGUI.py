import csv
import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import subprocess

# Class contains implementation of program GUI, allows URL input and data display.
class SneakerScraperApp:
    def __init__(self, root): # Initialize GUI
        self.root = root
        self.root.title("Nike X Goat Price Comparison")

        self.sort_column = None
        self.sort_order = None

        self.create_widgets()

    def create_widgets(self):
        # URL Entry
        self.url_label = tk.Label(self.root, text="Enter Nike URL:")
        self.url_label.pack(pady=5)
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.pack(pady=5)

        # Run Parser Button
        self.run_button = tk.Button(self.root, text="Run Parser", command=self.run_parser)
        self.run_button.pack(pady=10)

        # Load CSV Button
        self.load_button = tk.Button(self.root, text="Load CSV", command=self.load_csv)
        self.load_button.pack(pady=10)

        # Treeview for displaying data
        self.columns = ['SKU', 'Profit ($)', 'Profit (%)', 'Retail Price ($)', 'Resale Price ($)', 'Nike Link',
                        'Goat Link']
        self.tree = ttk.Treeview(self.root, columns=self.columns, show='headings')

        for column in self.columns:
            self.tree.heading(column, text=column, command=lambda _col=column: self.sort_treeview(_col))
            self.tree.column(column, width=150, anchor='center')

        self.tree.pack(pady=20)
        self.tree.bind("<ButtonRelease-1>", self.copy_to_clipboard)

    def run_parser(self): # Pass URL and run NikeParser.py
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return

        # Run the NikeParser.py script with the provided URL
        try:
            subprocess.run(["python", "NikeParser.py", url], check=True)
            messagebox.showinfo("Success", "Data obtained successfully. Now loading the results.")
            self.load_csv()  # Load the resulting CSV file
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to run parser: {e}")

    def load_csv(self): # Open CSV file created by NikeParser.py
        file_path = "NikeParserResults.csv"
        try:
            df = pd.read_csv(file_path)
            self.process_data(df)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file: {e}")

    def process_data(self, df): #Add data to view
        # Check if required columns are present
        required_columns = ['SKU', 'Profit ($)', 'Profit (%)', 'Retail Price ($)', 'Resale Price ($)', 'Nike Link',
                            'Goat Link']
        if not all(column in df.columns for column in required_columns):
            messagebox.showerror("Error", "CSV file does not contain required columns")
            return

        # Clear the treeview
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Insert data into the treeview
        for _, row in df.iterrows():
            self.tree.insert('', tk.END, values=(
            row['SKU'], row['Profit ($)'], row['Profit (%)'], row['Retail Price ($)'], row['Resale Price ($)'],
            row['Nike Link'], row['Goat Link']))

    def copy_to_clipboard(self, event): # Copy cell when clicked
        # Check if the click was on the heading (for sorting)
        region = self.tree.identify("region", event.x, event.y)
        if region == "heading":
            return

        item = self.tree.identify('item', event.x, event.y)
        column = self.tree.identify_column(event.x)
        if item and column:
            cell_value = self.tree.item(item, "values")[int(column[1:]) - 1]
            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(cell_value)
            messagebox.showinfo("Copied", f"Copied to clipboard: {cell_value}")

    def sort_treeview(self, col): # Sort data when column header is clicked
        data_list = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]

        # Determine if the column should be sorted as a number
        if col in ['Profit ($)', 'Profit (%)', 'Retail Price ($)', 'Resale Price ($)']:
            data_list = [(float(v[0].replace('$', '').replace('%', '')), v[1]) for v in data_list]

        data_list.sort(reverse=self.sort_order != "ASC")

        for index, (_, k) in enumerate(data_list):
            self.tree.move(k, '', index)

        self.sort_order = "ASC" if self.sort_order != "ASC" else "DESC"
        self.sort_column = col


if __name__ == "__main__": #Main
    root = tk.Tk()
    app = SneakerScraperApp(root)
    root.mainloop()
