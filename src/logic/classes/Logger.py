

class Logger():
    """This class allows you to log to a CTkinter ScrolledText widget"""

    def __init__(self, logUI):
        self.logUI = logUI

    def write(self, message):
        self.logUI.insert("end", f"{message}\n")

    def wipe(self):
        self.logUI.delete("0.0", "end")