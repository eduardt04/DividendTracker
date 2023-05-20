import json
import sqlite3
import tkinter as tk

from tkinter import ttk, messagebox, simpledialog


class CustomTreeview(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tag_configure("center", anchor="center")

    def set_cell_center_alignment(self, item, column):
        self.item(item, tags=tk.S)
        self.column(column, anchor=tk.S)


class NewPositionDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Stock:").grid(row=0, sticky="e")
        tk.Label(master, text="Quantity:").grid(row=1, sticky="e")

        self.entry1 = tk.Entry(master)
        self.entry2 = tk.Entry(master)

        self.entry1.grid(row=0, column=1)
        self.entry2.grid(row=1, column=1)

        self.result = None

    def apply(self):
        input1 = self.entry1.get()
        input2 = self.entry2.get()

        self.result = (input1, input2)


# Function to add a new position to the database
def add_new_position():
    dialog = NewPositionDialog(app, "Add new position")
    result = dialog.result
    if result is not None:
        cursor.execute("INSERT INTO entries (name, quantity) VALUES (?, ?)", result)
        conn.commit()
        populate_table()


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
        table.insert("", "end", text=row[0], values=row[1:])


if __name__ == "__main__":
    # Database Connection
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Create Table if not exists
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, quantity REAL)"
    )

    # Tkinter App
    app = tk.Tk()
    app.title("Dividend Tracker")

    # Configure width and height of the application
    width = json.load(open("design.json"))["width"]
    height = json.load(open("design.json"))["height"]
    app.geometry(f"{width}x{height}")

    # Create Table
    table = ttk.Treeview(app, columns=("Name", "Quantity"))
    table.heading("#0", text="Position ID")
    table.heading("Name", text="Name")
    table.heading("Quantity", text="Quantity")

    # Configure the style for the headings
    style = ttk.Style()
    style.configure("Treeview.Heading", foreground="black")

    # Center the text in the columns
    table.column("Name", anchor="s")
    table.column("Quantity", anchor="s")
    table.pack()

    add_button = tk.Button(
        app, text="Add new position", command=add_new_position, foreground="black"
    )
    add_button.pack()

    edit_button = tk.Button(
        app, text="Edit selected position", command=edit_entry, foreground="black"
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
