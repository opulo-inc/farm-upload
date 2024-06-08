from BambuFTP import BambuFTP
import requests

class Printer():
    def __init__(self, name, ip, enabled):
        self.name = name
        self.ip = ip
        self.enabled = enabled
        self.connected = False

    def connect(self):
        raise NotImplementedError("Subclasses must implement this method")
        
    def disconnect(self):
        raise NotImplementedError("Subclasses must implement this method")
    
    def upload(self):
        raise NotImplementedError("Subclasses must implement this method")
        

class BambuPrinter(Printer):
    def __init__(self, name, ip, pw, enabled):
        super().__init__(name, ip, enabled)
        self.pw = pw
        self.ftp = BambuFTP()
        #self.ftp.set_debuglevel(2)
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
        
    def upload(self, file, filename):
        if (not self.connected):
            raise Exception("Printer not connected")
        try:
            self.ftp.storbinary(f'STOR {filename}', file)
        except:
            return False

class KlipperPrinter(Printer):
    def __init__(self, name, ip, enabled):
        super().__init__(name, ip, enabled)

    def connect(self):
        infoResponse = requests.get(f'http://{self.ip}/server/info')
        self.connected = infoResponse.ok
        return self.connected

    def disconnect(self):
        return True
        
    def upload(self, file, filename):

        files = {
            'file': (filename, file)
        }
        uploadResponse = requests.post(f'http://{self.ip}/server/files/upload', files=files)
        return uploadResponse.ok
