
from BambuFTP import BambuFTP

class Printer():
    def __init__(self, name, ip, pw, enabled):
        self.name = name;
        self.ip = ip;
        self.pw = pw;
        self.enabled = enabled
        self.connected = False

        self.ftp = BambuFTP()
        self.ftp.set_debuglevel(2)
        self.ftp.set_pasv(True)


    def connect(self):
        try:
            self.ftp.connect(host=self.ip, port=990, timeout=10, source_address=None)
            self.ftp.login('bblp', self.pw)
            self.ftp.prot_p()
            self.connected = True
        except:
            return False
        
    def disconnect(self):
        try:
            self.ftp.quit()
            self.connected = False
        except:
            return False
