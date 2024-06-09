import customtkinter as CTk
from tkinter import filedialog
import json

class SelectSettings(CTk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        # label "settings file"
        self.label = CTk.CTkLabel(self, text="Select a settings file to start.")
        self.label.grid(row=0, column=0, padx=15, pady=(8, 15), sticky="s")

        # button "Select file"
        self.button_select_settings = CTk.CTkButton(self, text="Select settings file", command=self.selectsettings)
        self.button_select_settings.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nesw")


    def selectsettings(self):
        file = filedialog.askopenfilename(
            initialdir = ".",
            title = "Select settings File",
            filetypes = (("json file","*.json"),("json file","*.json"))
        )
        with open(file) as f:
            self.master.settings = json.load(f)
        self.master.settings_path = file
        self.master.changeWindow("Main")