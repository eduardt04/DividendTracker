import json
import tkinter as tk
from dividend import show_dividend_info

def main_app_loop():
    # Create the main Tkinter window
    window = tk.Tk()
    window.title("Dividend Tracker")

    # Set the width and height of the window
    width = json.load(open("design.json"))["width"]
    height = json.load(open("design.json"))["height"]
    window.geometry(f"{width}x{height}")

    # Load the main color from the configuration file
    main_color = json.load(open("design.json"))["main-color"]

    # Configure the window to have a light blue background
    window.configure(background=main_color)

    # # Create a label and entry for entering the stock name
    # label = tk.Label(window, text="Enter stock name to find information: ", font=("Helvetica", 14),
    #                  background="white", foreground="black")
    # label.pack(pady=20)

    # stock_entry = tk.Entry(window, font=("Helvetica", 14), background="white", foreground="black")
    # stock_entry.pack(padx=20)

    # # Create a button to trigger the dividend information
    # button = tk.Button(window, text="Find Information", command=show_dividend_info(window, stock_entry), 
    #                     background="white")
    # button.pack(pady=20)

    # Start the Tkinter event loop
    window.mainloop()