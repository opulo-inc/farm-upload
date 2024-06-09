import customtkinter as CTk
from tkinter import filedialog
from logic.classes.Logger import Logger
from logic.classes.Printer import Printer
from gui.main.FileList import FileList
from gui.main.PrinterList import PrinterList
import os, glob, threading


class Main(CTk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.grid_rowconfigure(6, weight=100)

        self.app = self.master

        # label "settings file name in cool font"
        self.title = CTk.CTkLabel(self, text=f"{os.path.basename(self.app.settings_path)}", justify="center", font=("Arial", 18))
        self.title.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="w")

        ## PRINTERS
        # label "printers"
        self.title_printer = CTk.CTkLabel(self, text="Select Printes", justify="center", font=("Arial", 15))
        self.title_printer.grid(row=1, column=0, padx=20, pady=10, sticky="n")

        # printer list (selection)
        self.printer_list = PrinterList(self)
        self.printer_list.grid(row=3, column=0, padx=20, pady=10, sticky="nesw")

        # select group (make this a pop up with ceckbox?)
        options = ["*Select a Group", "*Select All Printers", "*Unselect All Printers"] + self.printer_group_options
        self.printer_group_selection = CTk.CTkOptionMenu(self, values=options, command=self.selectGroup)
        self.printer_group_selection.grid(row=2, column=0, padx=20, pady=10, sticky="nesw")
        self.printer_group_selection.set("*Select a Group")

        # button "manipulate printers"
        self.conferma_button = CTk.CTkButton(self, text="Manipulate Printers", command=self.manipulatePrinters, state="disabled")
        self.conferma_button.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="nesw")

        # button "Send to Printers"
        self.conferma_button = CTk.CTkButton(self, text="Send to Printers", command=self.sendToPrinters)
        self.conferma_button.grid(row=4, column=1, padx=20, pady=(10, 0), sticky="nesw")

        ## FOLDERS
        # label "folder"
        self.title_folder = CTk.CTkLabel(self, text=f"Folder: {None}", justify="center", font=("Arial", 15))
        self.title_folder.grid(row=1, column=1, padx=20, pady=10, sticky="n")

        # button "select folder"
        self.conferma_button = CTk.CTkButton(self, text="Select folder", command=self.selectFolder)
        self.conferma_button.grid(row=2, column=1, padx=20, pady=(10, 0), sticky="nesw")

        # file list (selection)
        self.file_list = FileList(self)
        self.file_list.grid(row=3, column=1, columnspan=2, padx=20, pady=10, sticky="nesw")

        ## LOGS
        # label "logs"
        self.title_logs = CTk.CTkLabel(self, text="Logs:", anchor="w", font=("Arial", 15))
        self.title_logs.grid(row=5, column=0, padx=20, pady=10, sticky="nesw")

        # progress_bar
        #self.progressbar = CTk.CTkProgressBar(self, orientation="horizontal")
        #self.progressbar.grid(row=5, column=1, padx=20, pady=10)

        # scrollable logs
        self.logs_textbox = CTk.CTkTextbox(self)
        self.logs_textbox.grid(row=6, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="nesw")
        self.logger = Logger(self.logs_textbox)

    @property
    def printer_group_options(self) -> list:
        result = []
        if self.app.printers:
            for name, printer in self.app.printers.items():
                if printer.group not in result:
                    result.append(printer.group)
        return result

    def manipulatePrinters(self):
        pass

    def selectFolder(self):
        self.app.selected_folder = filedialog.askdirectory()
        files = glob.glob(os.path.join(self.app.selected_folder, '*.3mf'))
        self.app.selected_folder_files = {item: True for item in files}
        self.file_list.update()
        self.title_folder.configure(text=f"Folder: {os.path.basename(self.app.settings_path)}")

    def selectGroup(self, value):
        if value == "*Don't use Groups":
            pass
        elif value == "*Select All Printers":
            self.app.printers_selected = self.app.printers
        elif value == "*Unselect All Printers":
            self.app.printers_selected = {}
        else:
            new_items = {}
            for name, printer in self.app.printers.items():
                if printer.group == value:
                    new_items[name] = printer
            self.app.printers_selected = new_items

        self.printer_list.update()


    def sendToPrinters(self):
        self.logger.wipe()

        files = self.app.selected_folder_files
        printers_selected = self.app.printers_selected

        to_send = [os.path.basename(key) for key in files if files[key]]
        printer_names = [key for key in printers_selected if [key]]

        self.logger.write(f"Printers selected: {printer_names}\nFiles selected: {to_send}")
        printerThreads = list()

        for _, printer in printers_selected.items():
            thread = threading.Thread(target=self.sendOnePrinter, args=(printer, to_send))
            printerThreads.append(thread)
            thread.start()

        while any(t.is_alive() for t in printerThreads):
            self.app.update()
        self.logger.write("Process Complete!")


    def sendOnePrinter(self, printer: Printer, toSend):
        printer.connect()

        if printer.connected:

            self.logger.write(f"Connected to {printer.name}")

            for file_path in toSend:
                try:
                    with open(os.path.join(self.app.selected_folder, file_path), 'rb') as f:
                        self.logger.write(f"Sending {file_path} to printer {printer.name} ...")
                        printer.ftp.storbinary(f'STOR {file_path}', f)
                        self.logger.write(f"Success: {file_path} to printer {printer.name}")
                except:
                    try:
                        with open(os.path.join(self.app.selected_folder, file_path), 'rb') as f:
                            self.logger.write(f"Reattempting to send {file_path} to printer {printer.name} ...")
                            printer.ftp.storbinary(f'STOR {file_path}', f)
                            self.logger.write(f"Success: {file_path} to printer {printer.name}")
                    except:
                        self.logger.write(f"Failiure: {file_path} to printer {printer.name}")

            printer.disconnect()
            self.logger.write(f"Disconnected from {printer.name}")

        else:
            self.logger.write(f"Could not connect to {printer.name}")
