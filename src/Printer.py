from __future__ import annotations

from typing import TYPE_CHECKING

from BambuFTP import BambuFTP

if TYPE_CHECKING:
    from tkinter import BooleanVar
    from types import TracebackType

    from typing_extensions import Self


class Printer:
    __slots__ = ("name", "ip", "pw", "enabled", "connected", "ftp")

    def __init__(self, name: str, ip: str, pw: str, enabled: BooleanVar) -> None:
        self.name = name
        self.ip = ip
        self.pw = pw
        self.enabled = enabled
        self.connected = False

        self.ftp = BambuFTP()
        #self.ftp.set_debuglevel(2)
        self.ftp.set_pasv(True)


    def connect(self) -> bool:
        """Connect and login to FPT server. Return True on success."""
        try:
            self.ftp.connect(host=self.ip, port=990, timeout=10, source_address=None)
            self.ftp.login('bblp', self.pw)
            self.ftp.prot_p()
            self.connected = True
        except Exception as exc:
            return False
        return True

    def disconnect(self) -> bool:
        """Disconnect from FPT server. Return True on success."""
        try:
            self.ftp.quit()
            self.connected = False
        except Exception:
            return False
        return True

    def __enter__(self) -> Self:
        """Context manager enter."""
        self.connect()
        ##if not self.connect():
        ##    raise ValueError("Error connecting.")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Context manager exit."""
        self.disconnect()
        ##if not self.disconnect():
        ##    raise ValueError("Error disconnecting.")
