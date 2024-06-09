import customtkinter as CTk
from typing import Literal
from gui.SelectSettings import SelectSettings
from gui.Main import Main

class App(CTk.CTk):

    ## design GUI (https://excalidraw.com/#json=_gYLOEMIdrXcCb3VUiZ8-,gJ0XoeU5ao8QGx4KIrMM5Q)

    def __init__(self):
        super().__init__()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.title("Farm Upload")
        self._current_window = ""

        self.main_window = None
        self.printers: dict = {}
        self.printers_selected: dict = {}
        self.settings_path: str = None
        self.settings: dict = None
        self.selected_folder: str = None
        self.selected_folder_files: dict = {}

        self.changeWindow("SelectSettings")


    def changeWindow(self, window_name: Literal["SelectSettings", "Main"]): # find better name to 'main'
        """Select what page to show to the user.

        Args:
            window_name (str): page to open

        Raises:
            NotImplementedError: if the page is not implemented
        """
        if self.main_window:
            self.main_window.destroy()

        if window_name == "SelectSettings":
            self.main_window = SelectSettings(self)
            self.main_window.grid(row=0, column=0, padx=25, pady=(12, 25), sticky="nsew")

        elif window_name == "Main":

            self.main_window = Main(self)
            self.main_window.grid(row=0, column=0, padx=25, pady=(12, 25), sticky="nsew")
            self._current_window = window_name

        else:
            raise NotImplementedError(f"{window_name} window does not exist")


if __name__ == "__main__":
    app = App()

    app.mainloop()