import customtkinter as CTk
import os

class FileList(CTk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.app = self.master.master.master.app

        self.checkboxes = {}

    def update(self):
        for checkbox in self.checkboxes:
            checkbox.destroy()

        for file_path, status in self.app.selected_folder_files.items():
            file_name = os.path.basename(file_path)
            self.checkboxes[file_path] = CTk.CTkCheckBox(self, text=file_name, command=self.checkboxEvent)
            self.checkboxes[file_path].grid(row=0, column=0, padx=5, pady=(5, 0))
            if status:
                self.checkboxes[file_path].select()

    def checkboxEvent(self):
        new_states = {}
        for path, checkbox in self.checkboxes.items():
            if checkbox.get():
                new_states[path] = True
            else:
                new_states[path] = False
        self.app.selected_folder_files = new_states
