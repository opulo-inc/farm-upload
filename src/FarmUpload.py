from __future__ import annotations

import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from typing import TypedDict
import json, os
import threading, queue

from Printer import Printer
from Log import Logger


class PrinterSetting(TypedDict):
    name: str
    ip: str
    pw: str


class App:
    def __init__(self) -> None:
        self.settings: dict[str, list[PrinterSetting]] = {}
        self.printers: list[Printer] = []
        self.fileDirectory = ""

        self.ui = tk.Tk()
        self.loadUI()

        self.logQueue: queue.Queue[str] = queue.Queue()
        self.log = Logger(self.logUI)

        self.ui.after(50, self.processQueue)

        self.ui.mainloop()

    def loadSettings(self) -> None:

        settingsDirectory = filedialog.askopenfilename()
        self.s.config(text=os.path.basename(settingsDirectory))
        f = open(settingsDirectory)
        self.settings = json.load(f)
        f.close()

        # loading printers into app printer array

        for printer in self.settings["printers"]:
            var = tk.BooleanVar()
            self.printers.append(Printer(
                name = printer["name"],
                ip = printer["ip"],
                pw = printer["pw"],
                enabled = var
            ))

            checkbox = tk.Checkbutton(self.printerSelectFrame, text=printer["name"], variable=var, onvalue=True, offvalue=False)
            checkbox.pack(side=tk.LEFT, pady=10)

        self.s.update_idletasks()

    def loadUI(self) -> None:

        self.ui.title("FarmUpload")

        w = tk.Label(self.ui, text='Select the printers to send to:')
        w.pack()

        choose_settings_button = tk.Button(self.ui, text="Choose Settings JSON File", command=self.loadSettings)
        choose_settings_button.pack(pady=10, padx=10)

        self.s = tk.Label(self.ui, text='No settings file selected')
        self.s.pack(pady=10, padx=10)

        select_printers = tk.Label(self.ui, text="Select which printers to send to:")
        select_printers.pack(pady=10)

        self.printerSelectFrame = tk.Frame(master=self.ui, highlightbackground="black", highlightthickness=1)
        self.printerSelectFrame.pack()

        choose_folder_button = tk.Button(self.ui, text="Choose Folder to Upload", command=self.chooseFolder)
        choose_folder_button.pack(pady=10, padx=10)

        self.v = tk.Label(self.ui, text='No directory selected')
        self.v.pack(pady=10)

        send_button = tk.Button(self.ui, text="Send to Farm", command=self.send)
        send_button.pack(pady=10)

        # Logging

        self.logUI = ScrolledText(self.ui)
        self.logUI.pack()

    def chooseFolder(self) -> None:
        self.fileDirectory = filedialog.askdirectory()
        self.v.config(text=os.path.basename(self.fileDirectory))
        self.v.update_idletasks()

    def processQueue(self) -> None:
        try:
            msg = self.logQueue.get_nowait()
            self.log.write(msg)
        except queue.Empty:
            pass

    def sendOnePrinter(self, printer: Printer, toSend: list[str]) -> None:

        with printer:
            if not printer.connected:
                self.logQueue.put(f"Could not connect to {printer.name}")
                return
            self.logQueue.put(f"Connected to {printer.name}")

            for filename in toSend:
                try:
                    with open(os.path.join(self.fileDirectory, filename), 'rb') as file:
                        self.logQueue.put(f"Sending {filename} to printer {printer.name}..." )

                        printer.ftp.storbinary(f'STOR {filename}', file)
                        self.logQueue.put(f"Success: {filename} to printer {printer.name}")

                except:
                    try:
                        with open(os.path.join(self.fileDirectory, filename), 'rb') as file:
                            self.logQueue.put(f"Reattempting to send {filename} to printer {printer.name}...")
                            printer.ftp.storbinary(f'STOR {filename}', file)
                            self.logQueue.put(f"Success: {filename} to printer {printer.name}")
                    except Exception:
                        self.logQueue.put(f"Failure: {filename} to printer {printer.name}")

    def send(self) -> None:

        self.log.wipe()

        toSend = os.listdir(self.fileDirectory)

        self.log.write(f"Files to be sent: {toSend}")

        printerThreads = []

        for printer in self.printers:

            if printer.enabled.get():

                thread = threading.Thread(target=self.sendOnePrinter, args=(printer, toSend))
                printerThreads.append(thread)
                thread.start()

            else:
                self.log.write(f"Skipping {printer.name}")

        while any(t.is_alive() for t in printerThreads):
            self.processQueue()
            # keeps ui from hanging
            self.ui.update()

        self.processQueue()

        self.logQueue.put("Process Complete!")

        self.processQueue()


if __name__ == "__main__":
    app = App()
