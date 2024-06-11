import customtkinter as CTk
from logic.classes.Printer import Printer

class PrinterList(CTk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.app = self.master.master.master.app

        self.checkboxes = {}

        for i, printer in enumerate(self.app.settings["printers"]):
            self.app.printers[printer["name"]] = Printer(
                name = printer["name"],
                group = printer["group"],
                ip = printer["ip"],
                pw = printer["pw"]
            )
            self.checkboxes[printer['name']] = CTk.CTkCheckBox(self, text=printer['name'], command=self.checkboxEvent)
            self.checkboxes[printer['name']].grid(row=i, column=0, padx=5, pady=(5, 0))

    def checkboxEvent(self):
        new_states = {}
        for name, checkbox in self.checkboxes.items():
            if checkbox.get():
                new_states[name] = self.app.printers[name]
        self.app.printers_selected = new_states

    def update(self):
        for name, checkbox in self.checkboxes.items():
            if name in self.app.printers_selected:
                checkbox.select()
            else:
                checkbox.deselect()