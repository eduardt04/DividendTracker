import json
import sqlite3
import numpy as np
import tkinter as tk

from code.stock_data import get_stock_data
from tkinter import ttk, messagebox, simpledialog


class NewPositionDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Stock:").grid(row=0, sticky="e")
        tk.Label(master, text="Quantity:").grid(row=1, sticky="e")
        tk.Label(master, text="Avg. Open:").grid(row=2, sticky="e")

        self.entry1 = tk.Entry(master)
        self.entry2 = tk.Entry(master)
        self.entry3 = tk.Entry(master)

        self.entry1.grid(row=0, column=1)
        self.entry2.grid(row=1, column=1)
        self.entry3.grid(row=2, column=1)

        self.result = None

    def apply(self):
        input1 = self.entry1.get().upper()
        input2 = self.entry2.get()
        input3 = self.entry3.get()

        self.result = {}
        self.result["stock_name"] = input1
        self.result["quantity"] = input2
        self.result["avg_open"] = input3


# Function to add a new position to the database
def add_new_position():
    dialog = NewPositionDialog(app, "Add new position")
    input = dialog.result

    # Check if input was bad
    if input is not None:
        cursor.execute(
            "INSERT INTO entries (name, quantity, avg_open) VALUES (?, ?, ?)",
            (
                input["stock_name"],
                input["quantity"],
                input["avg_open"],
            ),
        )
        conn.commit()
        populate_table()
        update_statistics()


# Edit quantity entry
def edit_quantity_entry():
    selected_item = table.selection()
    if selected_item:
        quantity = simpledialog.askfloat("Edit Quantity", "Enter the New Quantity:")
        if quantity is not None:
            entry_id = table.item(selected_item)["text"]
            cursor.execute(
                "UPDATE entries SET quantity=? WHERE id=?", (quantity, entry_id)
            )
            conn.commit()
            populate_table()
            update_statistics()
    else:
        messagebox.showinfo("No Selection", "Please select an entry to edit.")


# Edit average open entry
def edit_avg_open_entry():
    selected_item = table.selection()
    if selected_item:
        avg_open = simpledialog.askfloat(
            "Edit Average Open", "Enter the New Average Open Price:"
        )
        if avg_open is not None:
            entry_id = table.item(selected_item)["text"]
            cursor.execute(
                "UPDATE entries SET avg_open=? WHERE id=?", (avg_open, entry_id)
            )
            conn.commit()
            populate_table()
            update_statistics()
    else:
        messagebox.showinfo("No Selection", "Please select an entry to edit.")


# Remove Entry
def remove_entry():
    selected_item = table.selection()
    if selected_item:
        confirmation = messagebox.askyesno(
            "Confirmation", "Are you sure you want to remove this entry?"
        )
        if confirmation:
            entry_id = table.item(selected_item)["text"]
            cursor.execute("DELETE FROM entries WHERE id=?", (entry_id,))
            conn.commit()
            populate_table()
            update_statistics()
    else:
        messagebox.showinfo("No Selection", "Please select an entry to remove.")


# Function to populate the table
def populate_table():
    # Clear existing data
    table.delete(*table.get_children())

    # Retrieve data from database
    cursor.execute("SELECT * FROM entries")
    rows = cursor.fetchall()

    # Populate table with data
    for row in rows:
        output = row

        # Data from the database
        stock_name = row[1]
        stock_quantity = row[2]
        stock_avg_open = row[3]

        # Access stock market data with the API
        stock_data = get_stock_data(stock_name)
        if stock_data is not None:
            stock_price = round(stock_data[0], 3)
            profit = round((stock_price - stock_avg_open) * stock_quantity, 3)
            value = round(stock_quantity * stock_price, 3)
            stock_dividend = round(stock_data[1], 3)
            stock_div_frequency = stock_data[3]
            stock_div_last_date = stock_data[2]
            stock_total_div_yearly = round(
                (stock_div_frequency * stock_dividend * stock_quantity), 3
            )
            output += (
                stock_price,
                profit,
                value,
                stock_dividend,
                stock_div_frequency,
                stock_total_div_yearly,
                stock_div_last_date,
            )
            table.insert("", "end", text=output[0], values=output[1:])


def get_column_values(column_index):
    values = []
    for item in table.get_children():
        item_values = table.item(item)["values"]
        if item_values:
            column_data = item_values[
                column_index
            ]  # Replace 'column_index' with the actual index of the desired column
            values.append(float(column_data))
    return values


def calculate_yearly_dividends():
    data = np.array(get_column_values(8))
    return np.sum(data)


def calculate_total_profit():
    data = np.array(get_column_values(4))
    return np.sum(data)


def calculate_total_value():
    data = np.array(get_column_values(5))
    return round(np.sum(data), 3)


def update_statistics():
    yearly_dividends = round(calculate_yearly_dividends(), 3)
    label_yearly_dividends.config(text=f"Yearly: {yearly_dividends}")
    label_monthly_dividends.config(text=f"Monthly: {round(yearly_dividends / 12, 3)}")
    label_weekly_dividends.config(text=f"Weekly: {round(yearly_dividends / 52, 3)}")
    label_daily_dividends.config(text=f"Daily: {round(yearly_dividends / 365, 3)}")
    label_total_profit.config(text=f"Total profit: {calculate_total_profit()}")
    label_total_value.config(text=f"Total value: {calculate_total_value()}")


if __name__ == "__main__":
    # Database Connection
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Create Table if not exists
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS entries (\
            id INTEGER PRIMARY KEY AUTOINCREMENT, \
            name STRING, \
            quantity REAL, \
            avg_open REAL\
        )"
    )

    # Tkinter App
    app = tk.Tk()
    app.title("Dividend Tracker")

    # Configure width and height of the application
    width = json.load(open("design.json"))["width"]
    height = json.load(open("design.json"))["height"]
    app.geometry(f"{width}x{height}")

    # Create labels for dividend statistics
    label_description = tk.Label(app, text="Dividend breakdown", font=("Helvetica", 16))
    label_yearly_dividends = tk.Label(app, text="")
    label_monthly_dividends = tk.Label(app, text="")
    label_weekly_dividends = tk.Label(app, text="")
    label_daily_dividends = tk.Label(app, text="")
    label_total_profit = tk.Label(app, text="")
    label_total_value = tk.Label(app, text="")

    # Pack them to display in the app
    label_description.pack()
    label_yearly_dividends.pack()
    label_monthly_dividends.pack()
    label_weekly_dividends.pack()
    label_daily_dividends.pack()
    label_total_profit.pack()
    label_total_value.pack()

    # Create Table
    table = ttk.Treeview(
        app,
        columns=(
            "Name",
            "Quantity",
            "AvgOpen",
            "Price",
            "Profit",
            "Value",
            "Dividend",
            "DividendFrequency",
            "TotalYear",
            "LastPaymentDate",
        ),
    )
    table.heading("#0", text="ID")
    table.heading("Name", text="Name")
    table.heading("Quantity", text="Quantity")
    table.heading("AvgOpen", text="Avg. Open")
    table.heading("Price", text="Price")
    table.heading("Profit", text="Profit")
    table.heading("Value", text="Value")
    table.heading("Dividend", text="Dividend")
    table.heading("DividendFrequency", text="Frequency")
    table.heading("TotalYear", text="Yearly divs.")
    table.heading("LastPaymentDate", text="Last payment date")

    # Configure the style for the headings
    style = ttk.Style()
    style.configure("Treeview.Heading", foreground="black")

    # Center the text in the columns
    table.column("#0", anchor="s", width=25)
    table.column("Name", anchor="s", width=75)
    table.column("Quantity", anchor="s", width=50)
    table.column("AvgOpen", anchor="s", width=75)
    table.column("Price", anchor="s", width=75)
    table.column("Profit", anchor="s", width=75)
    table.column("Value", anchor="s", width=75)
    table.column("Dividend", anchor="s", width=75)
    table.column("DividendFrequency", anchor="s", width=75)
    table.column("TotalYear", anchor="s", width=75)
    table.column("LastPaymentDate", anchor="s", width=125)
    table.pack(pady=20)

    add_button = tk.Button(
        app, text="Add new position", command=add_new_position, foreground="black"
    )
    add_button.pack()

    edit_quantity_button = tk.Button(
        app,
        text="Edit selected quantity",
        command=edit_quantity_entry,
        foreground="black",
    )
    edit_quantity_button.pack()

    edit_avg_open_button = tk.Button(
        app,
        text="Edit selected average open price",
        command=edit_avg_open_entry,
        foreground="black",
    )
    edit_avg_open_button.pack()

    remove_button = tk.Button(
        app, text="Remove selected position", command=remove_entry, foreground="black"
    )
    remove_button.pack()

    # Populate Table
    populate_table()
    update_statistics()

    # Run the Tkinter event loop
    app.mainloop()

    # Close Database Connection
    cursor.close()
    conn.close()
