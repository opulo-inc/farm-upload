from __future__ import annotations
from BambuFTP import BambuFTP

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import tkinter as tk


class Printer():
    def __init__(self, name: str, ip: str, pw: str, enabled: tk.BooleanVar):
        self.name: str = name
        self.ip: str = ip
        self.pw: str = pw
        self.enabled: tk.BooleanVar = enabled
        self.connected: bool = False

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
