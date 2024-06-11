import customtkinter as CTk
import os

class FileList(CTk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.app = self.master.master.master.app

        self.checkboxes = {}

    def update(self):
        for path, checkbox in self.checkboxes.items():
            # I hate this, but its late and for now it works so I don't care.
            try:
                checkbox.destroy()
            except:
                continue
            try:
                del checkbox
            except:
                continue
        self.checkboxes = {}

        for i, file_path in enumerate(self.app.selected_files):
            file_name = os.path.basename(file_path)
            self.checkboxes[file_path] = CTk.CTkCheckBox(self, text=file_name, command=self.checkboxEvent)
            self.checkboxes[file_path].grid(row=i, column=0, padx=5, pady=(5, 0), sticky="w")
            self.checkboxes[file_path].select()

        self.master.master.master.title_files.configure(text=f"Files: {len(self.app.selected_files)}")

    def checkboxEvent(self):
        for i, (path, checkbox) in enumerate(self.checkboxes.items()):
            if checkbox.get() == 0:
                self.app.selected_files.pop(i)
        self.update()
