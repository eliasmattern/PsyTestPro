from datetime import datetime
import tkinter as tk
from tkcalendar import Calendar

def create_date_picker(year, month, day):
    def save_date():
        root.quit()  # Close the window
        root.destroy()

    def close_window(event):
        root.quit()
        root.destroy()

    root = tk.Tk()
    root.title("Dark Mode Date Picker Example")

    # Set a dark color scheme
    root.configure(bg="#333333")
    root.option_add("*TButton*highlightBackground", "#333333")
    root.option_add("*TButton*highlightColor", "#333333")
    root.option_add("*TButton*background", "#555555")
    root.option_add("*TButton*foreground", "#ffffff")
    root.option_add("*TLabel*background", "#333333")
    root.option_add("*TLabel*foreground", "#ffffff")
    root.option_add("*TFrame*background", "#333333")

    cal = Calendar(root, selectmode="day", year=year, month=month, day=day, background="#555555", foreground="#ffffff", bordercolor="#333333")
    cal.pack(padx=10, pady=10)

    button = tk.Button(root, text="Get Selected Date", command=save_date, bg="#555555", fg="#ffffff", relief=tk.FLAT)
    button.pack(pady=10)
    root.bind('<Escape>', close_window)  # Bind the Escape key to the close_window function

    root.mainloop()
    selected_date_str = cal.get_date()
    selected_date = datetime.strptime(selected_date_str, "%m/%d/%y")
    formatted_date = selected_date.strftime("%d/%m/%Y")
    return formatted_date