import tkinter as tk
import logging

class Logger():
    """This class allows you to log to a Tkinter Text or ScrolledText widget"""

    def __init__(self, logUI):
        self.logUI = logUI

    def write(self, message):
        self.logUI.insert(tk.INSERT, message + "\n")
        self.logUI.see("end")
        self.logUI.update()

    def wipe(self):
        self.logUI.delete('1.0', tk.END)