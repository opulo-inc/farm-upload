
class Log():
    def __init__(self, logUI, logStringVar):
        self.logStringVar = logStringVar
        self.logUI = logUI

        self.logText = "Log:\n"
        self.logStringVar.set(self.logText)

    def updateLog(self, text):
        self.logText = self.logText + text + "\n"
        self.logStringVar.set(self.logText)
        self.logUI.update()

    def wipeLog(self):
        self.logText = "Log:\n"
        self.logStringVar.set(self.logText)
        self.logUI.update()