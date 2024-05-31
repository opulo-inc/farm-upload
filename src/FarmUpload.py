import tkinter as tk
from tkinter import filedialog
import json, os

from BambuFTP import BambuFTP

class App():
    def __init__(self):
        self.settings = None
        self.printers = []
        self.fileDirectory = ""

        self.ui = tk.Tk()

        self.logText = "Log:\n"
        self.logStringVar = tk.StringVar()
        self.logStringVar.set(self.logText)
        
        #self.loadSettings()
        self.loadUI()

    def loadSettings(self):

        settingsDirectory = filedialog.askopenfilename()
        self.s.config(text=settingsDirectory)
        f = open(settingsDirectory)
        self.settings = json.load(f)
        f.close()
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

        send_button = tk.Button(self.ui, text="Send to Farm", command=self.send)
        send_button.pack(pady=10)

        self.log = tk.Label(self.ui, justify="left", textvariable=self.logStringVar)
        self.log.pack(pady=10)

        self.ui.mainloop()

    def updateLog(self, text):
        self.logText = self.logText + text + "\n"
        self.logStringVar.set(self.logText)
        self.log.update()

    def wipeLog(self):
        self.logText = "Log:\n"
        self.logStringVar.set(self.logText)
        self.log.update()


    def chooseFolder(self):
        self.fileDirectory = filedialog.askdirectory()
        self.v.config(text=self.fileDirectory)
        self.v.update_idletasks()

    def connect(self, printerJSON):
        try:
            ftp = BambuFTP()
            ftp.set_debuglevel(2)
            ftp.set_pasv(True)
            ftp.connect(host=printerJSON["ip"], port=990, timeout=10, source_address=None)
            ftp.login('bblp', printerJSON["pw"])
            ftp.prot_p()
            self.printers.append([printerJSON["name"], ftp])
            self.updateLog("Connected to " + printerJSON["name"])
            return ftp
        except:
            self.updateLog("Was unable to connect to " + printerJSON["name"])
            return None

    def disconnect(self, ftp, name):
        try:
            ftp.quit()
            self.updateLog("Disconnected from " + str(name))
        except:
            self.updateLog("Was unable to disconnect from " + str(name))

    def send(self):

        self.wipeLog()

        toSend = os.listdir(self.fileDirectory)

        self.updateLog("Files to be sent: " + str(toSend))
        
        for printer in self.settings["printers"]:

            ftp = self.connect(printer)
            
            if ftp is not None:

                for filename in toSend:
                    try:
                        with open(os.path.join(self.fileDirectory,filename), 'rb') as file:
                            self.updateLog("Sending " + str(filename) + " to printer " + printer["name"] + "..." )
                            ftp.storbinary(f'STOR {filename}', file, callback=self.update)
                            self.updateLog("Success")

                    except:
                        try:
                            with open(os.path.join(self.fileDirectory,filename), 'rb') as file:
                                self.updateLog("Reattempting to send " + str(filename) + " to printer " + printer["name"] + "..." )
                                ftp.storbinary(f'STOR {filename}', file, callback=self.update)
                                self.updateLog("Success")
                        except:
                            self.updateLog("Failure")

                self.disconnect(ftp, printer["name"])

        self.updateLog("Process Complete.")


    def update(self, block):
        print(str(block))


if __name__ == "__main__":
    app = App()