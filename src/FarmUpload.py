import tkinter as tk
from tkinter import filedialog, Scrollbar
import json, os

from Printer import Printer
from Log import Log

class App():
    def __init__(self):
        self.settings = None
        self.printers = []
        self.fileDirectory = ""

        self.ui = tk.Tk()
        self.loadUI()

        self.log = Log(self.logUI, self.logStringVar)

        self.ui.mainloop()

    def loadSettings(self):

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
            checkbox.pack(pady=10)

        self.s.update_idletasks()

    def loadUI(self):
        
        self.ui.title("Print Farm Bulk Uploader")
        w = tk.Label(self.ui, text='Select the printers to send to:')
        w.pack()

        choose_settings_button = tk.Button(self.ui, text="Choose Settings JSON File", command=self.loadSettings)
        choose_settings_button.pack(pady=10, padx=10)

        self.s = tk.Label(self.ui, text='No settings file selected')
        self.s.pack(pady=10, padx=10)

        choose_folder_button = tk.Button(self.ui, text="Choose Folder to Upload", command=self.chooseFolder)
        choose_folder_button.pack(pady=10, padx=10)

        self.v = tk.Label(self.ui, text='No directory selected')
        self.v.pack(pady=10)

        select_printers = tk.Label(self.ui, text="Select which printers to send to:")
        select_printers.pack(pady=10)

        self.printerSelectFrame = tk.Frame(master=self.ui, highlightbackground="black", highlightthickness=1)
        self.printerSelectFrame.pack()

        send_button = tk.Button(self.ui, text="Send to Farm", command=self.send)
        send_button.pack(pady=10)

        scrollbar = Scrollbar(self.ui)

        self.logStringVar = tk.StringVar()
        self.logUI = tk.Label(self.ui, justify="left", textvariable=self.logStringVar)
        self.logUI.pack(pady=10)


    def chooseFolder(self):
        self.fileDirectory = filedialog.askdirectory()
        self.v.config(text=os.path.basename(self.fileDirectory))
        self.v.update_idletasks()

    def send(self):

        self.log.wipeLog()

        toSend = os.listdir(self.fileDirectory)

        self.log.updateLog("Files to be sent: " + str(toSend))
        
        for printer in self.printers:

            if printer.enabled.get():

                printer.connect()
                
                if printer.connected:

                    self.log.updateLog("Connected to " + printer.name)

                    for filename in toSend:
                        try:
                            with open(os.path.join(self.fileDirectory,filename), 'rb') as file:
                                self.log.updateLog("Sending " + str(filename) + " to printer " + printer.name + "..." )
                                printer.ftp.storbinary(f'STOR {filename}', file, callback=self.update)
                                self.log.updateLog("Success")

                        except:
                            try:
                                with open(os.path.join(self.fileDirectory,filename), 'rb') as file:
                                    self.log.updateLog("Reattempting to send " + str(filename) + " to printer " + printer["name"] + "..." )
                                    printer.ftp.storbinary(f'STOR {filename}', file, callback=self.update)
                                    self.log.updateLog("Success")
                            except:
                                self.log.updateLog("Failure")

                    printer.disconnect()

                else:
                    self.log.updateLog("Could not connect to " + printer.name)
            
            else:
                self.log.updateLog("Skipping " + printer.name)

        self.log.updateLog("Process Complete!")


if __name__ == "__main__":
    app = App()