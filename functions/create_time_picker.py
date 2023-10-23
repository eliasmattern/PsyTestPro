from tktimepicker import AnalogPicker, AnalogThemes
from tktimepicker import constants
import tkinter as tk

def create_time_picker(hour, minute, tranlsateService):
    def save_time():
        root.quit()  # Close the window
        root.destroy()

    def close_window(event):
        root.quit()
        root.destroy()

    root = tk.Tk()
    root.configure(background = "black")

    time_picker = AnalogPicker(root, type=constants.HOURS24)
    time_picker.setHours(hour)
    time_picker.setMinutes(minute)

    time_picker.hours_picker.setHours(int(hour))
    time_picker.minutes_picker.setMinutes(int(minute))
    
    time_picker.pack(expand=True, fill="both")
   

    theme = AnalogThemes(time_picker)
    theme.setDracula()

    save_button = tk.Button(root, text=tranlsateService.get_translation("saveTime"), command=save_time)
    save_button.pack()

    root.bind('<Escape>', close_window)  # Bind the Escape key to the close_window function

    root.mainloop()
    return time_picker