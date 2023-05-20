import json
import sqlite3
import numpy as np
import tkinter as tk

from code.stock_data import Stock
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
        stock = Stock(input["stock_name"])

        # Check if stock info is available
        if stock.last_price is None:
            return
        cursor.execute(
            "INSERT INTO entries (name, current_price, avg_open, quantity, dividend, last_payment_date) VALUES (?, ?, ?, ?, ?, ?)",
            (
                input["stock_name"],
                stock.last_price,
                input["avg_open"],
                input["quantity"],
                stock.last_payment_ammount,
                stock.last_payment_date,
            ),
        )
        conn.commit()
        populate_table()
        update_statistics()


# Edit Entry
def edit_entry():
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
        row = (
            row[0],
            row[1],
            row[4],
            row[5],
            round(row[2], 3),
            row[3],
            round((row[2] - row[3]) * row[4], 3),
            round(row[2] * row[4], 3),
            row[6],
        )
        table.insert("", "end", text=row[0], values=row[1:])


def calculate_yearly_dividends():
    # Retrieve data from database
    cursor.execute("SELECT quantity, dividend FROM entries")
    rows = np.array(cursor.fetchall())
    try:
        return np.sum(rows[:, 0] * rows[:, 1]) * 4
    except:
        return 0.0


def calculate_total_profit():
    cursor.execute("SELECT current_price, avg_open, quantity FROM entries")
    rows = np.array(cursor.fetchall())
    try:
        return round(np.sum((rows[:, 0] - rows[:, 1]) * rows[:, 2]), 3)
    except:
        return 0.0


def update_statistics():
    yearly_dividends = round(calculate_yearly_dividends(), 3)
    label_yearly_dividends.config(text=f"Yearly: {yearly_dividends}")
    label_monthly_dividends.config(text=f"Monthly: {round(yearly_dividends / 12, 3)}")
    label_weekly_dividends.config(text=f"Weekly: {round(yearly_dividends / 52, 3)}")
    label_daily_dividends.config(text=f"Daily: {round(yearly_dividends / 365, 3)}")
    label_total_profit.config(text=f"Total profit: {calculate_total_profit()}")


if __name__ == "__main__":
    # Database Connection
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Create Table if not exists
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS entries (\
            id INTEGER PRIMARY KEY AUTOINCREMENT, \
            name STRING, \
            current_price REAL, \
            avg_open REAL, \
            quantity REAL, \
            dividend FLOAT, \
            last_payment_date STRING \
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

    # Pack them to display in the app
    label_description.pack()
    label_yearly_dividends.pack()
    label_monthly_dividends.pack()
    label_weekly_dividends.pack()
    label_daily_dividends.pack()
    label_total_profit.pack()
    update_statistics()

    # Create Table
    table = ttk.Treeview(
        app,
        columns=(
            "Name",
            "Quantity",
            "Dividend",
            "Price",
            "AvgOpen",
            "Profit",
            "Value",
            "LastPaymentDate",
        ),
    )
    table.heading("#0", text="ID")
    table.heading("Name", text="Name")
    table.heading("Price", text="Price")
    table.heading("AvgOpen", text="Avg. Open")
    table.heading("Profit", text="Profit")
    table.heading("Quantity", text="Quantity")
    table.heading("Dividend", text="Dividend")
    table.heading("LastPaymentDate", text="Last payment date")
    table.heading("Value", text="Value")

    # Configure the style for the headings
    style = ttk.Style()
    style.configure("Treeview.Heading", foreground="black")

    # Center the text in the columns
    table.column("#0", anchor="s", width=25)
    table.column("Name", anchor="s", width=75)
    table.column("Price", anchor="s", width=75)
    table.column("AvgOpen", anchor="s", width=75)
    table.column("Profit", anchor="s", width=75)
    table.column("Quantity", anchor="s", width=50)
    table.column("Dividend", anchor="s", width=75)
    table.column("LastPaymentDate", anchor="s", width=100)
    table.column("Value", anchor="s", width=75)
    table.pack(pady=20)

    add_button = tk.Button(
        app, text="Add new position", command=add_new_position, foreground="black"
    )
    add_button.pack()

    edit_button = tk.Button(
        app,
        text="Edit quantity for selected position",
        command=edit_entry,
        foreground="black",
    )
    edit_button.pack()

    remove_button = tk.Button(
        app, text="Remove selected position", command=remove_entry, foreground="black"
    )
    remove_button.pack()

    # Populate Table
    populate_table()

    # Run the Tkinter event loop
    app.mainloop()

    # Close Database Connection
    cursor.close()
    conn.close()
