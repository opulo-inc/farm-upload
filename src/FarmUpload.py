import tkinter as tk
from tkinter import filedialog
import tkinter.scrolledtext as st 
import json, os
import threading, queue

from Printer import BambuPrinter, KlipperPrinter
from Log import Logger

class App():
    def __init__(self):
        self.settings = None
        self.printers = []
        self.fileDirectory = ""

        self.ui = tk.Tk()
        self.loadUI()

        self.logQueue = queue.Queue()
        self.log = Logger(self.logUI)

        self.ui.after(50, self.processQueue)

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
            # switch for printer["type"]
            if printer["type"] == "Bambu":
                self.printers.append(BambuPrinter(
                    name = printer["name"],
                    ip = printer["ip"],
                    pw = printer["pw"],
                    enabled = var
                ))
            if printer["type"] == "Klipper":
                self.printers.append(KlipperPrinter(
                    name = printer["name"],
                    ip = printer["ip"],
                    enabled = var
                ))


            checkbox = tk.Checkbutton(self.printerSelectFrame, text=printer["name"], variable=var, onvalue=True, offvalue=False)
            checkbox.pack(side=tk.LEFT, pady=10)

        self.s.update_idletasks()

    def loadUI(self):
        
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

        self.logUI = st.ScrolledText(self.ui)
        self.logUI.pack()
        
    def chooseFolder(self):
        self.fileDirectory = filedialog.askdirectory()
        self.v.config(text=os.path.basename(self.fileDirectory))
        self.v.update_idletasks()

    def processQueue(self):
        try:
            msg = self.logQueue.get_nowait()
            self.log.write(msg)
        except queue.Empty:
            pass

    def sendOnePrinter(self, printer, toSend):

        printer.connect()
        
        if printer.connected:

            self.logQueue.put("Connected to " + str(printer.name))

            for filename in toSend:
                try:
                    with open(os.path.join(self.fileDirectory,filename), 'rb') as file:
                        self.logQueue.put("Sending " + str(filename) + " to printer " + printer.name + "..." )
                        
                        printer.upload(file, filename)
                        
                        self.logQueue.put("Success: " + str(filename) + " to printer " + printer.name)

                except:
                    try:
                        with open(os.path.join(self.fileDirectory,filename), 'rb') as file:
                            self.logQueue.put("Reattempting to send " + str(filename) + " to printer " + printer["name"] + "..." )
                            printer.upload(file, filename)
                            self.logQueue.put("Success: " + str(filename) + " to printer " + printer.name)
                    except:
                        self.logQueue.put("Failure: " + str(filename) + " to printer " + printer.name)

            printer.disconnect()

        else:
            self.logQueue.put("Could not connect to " + printer.name)
        

    def send(self):

        self.log.wipe()

        toSend = os.listdir(self.fileDirectory)

        self.log.write("Files to be sent: " + str(toSend))

        printerThreads = list()

        for printer in self.printers:

            if printer.enabled.get():

                thread = threading.Thread(target=self.sendOnePrinter, args=(printer, toSend))
                printerThreads.append(thread)
                thread.start()

            else:
                self.log.write("Skipping " + printer.name)

        while any(t.is_alive() for t in printerThreads):
            self.processQueue()
            # keeps ui from hanging
            self.ui.update()

        self.processQueue()
            
        self.logQueue.put("Process Complete!")

        self.processQueue()


if __name__ == "__main__":
    app = App()
