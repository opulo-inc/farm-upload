import ftplib
import io
import requests
import time
import queue
from BambuFTP import BambuFTP

MAX_SEND_RETRY = 5


class Printer:
    def __init__(self, config: dict) -> None:
        self.name = config.get("name")
        self.type = config.get("type")
        self.ip = config.get("ip")
        self.enabled = config.get("enabled")
        self.connected = False


class Bambu(Printer):
    def __init__(self, config: dict) -> None:
        Printer.__init__(self, config)

        self.user = config.get("user")
        self.pw = config.get("pw")
        self.ftp = BambuFTP()

        self.ftp.set_pasv(True)

    def connect(self) -> None:
        try:
            self.ftp.connect(host=self.ip, port=990, timeout=10, source_address=None)
            self.ftp.login(self.user, self.pw)
            self.ftp.prot_p()
            self.connected = True
        except ftplib.all_errors:
            return False

    def send(self, filename: str, file: io.BytesIO, logger: queue.Queue) -> bool:
        for i in range(1, MAX_SEND_RETRY+1):
            try:
                self.ftp.storbinary(f"STOR {filename}", file)
            except ftplib.all_errors:
                logger.put(f"Error: reattempting to send to {self.name} ({i}/{MAX_SEND_RETRY})")
                time.sleep(1)
                continue
            return True
        return False

    def disconnect(self) -> None:
        try:
            self.ftp.quit()
            self.connected = False
        except ftplib.all_errors:
            return False


class Octoprint(Printer):
    def __init__(self, config: dict) -> None:
        Printer.__init__(self, config)

        self.port = config.get("port")
        self.api_key = config.get("api_key")
        self.location = config.get("location")

    def connect(self) -> None:
        headers = {"X-Api-Key": self.api_key}
        response = requests.get(
            f"http://{self.ip}:{self.port}/api/version",
            headers=headers,
        )
        if response.status_code == 200:
            self.connected = True
            return
        self.connected = False

    def send(self, filename: str, file: io.BytesIO, logger: queue.Queue) -> bool:
        headers = {"X-Api-Key": self.api_key}
        for i in range(1, MAX_SEND_RETRY+1):
            try:
                response = requests.post(
                    f"http://{self.ip}:{self.port}/api/files/{self.location}",
                    files={"file": file, "filename": filename},
                    headers=headers,
                )
                if response.status_code == 201:
                    return True
            except BaseException as exception:
                logger.put(f"{type(exception).__name__}: reattempting to send to {self.name} ({i}/{MAX_SEND_RETRY})")
                time.sleep(1)
        return False

    def disconnect(self) -> None:
        self.connected = False


class Prusa(Printer):
    def __init__(self, config: dict) -> None:
        Printer.__init__(self, config)

        self.port = config.get("port")
        self.api_key = config.get("api_key")

    def connect(self) -> None:
        headers = {"X-Api-Key": self.api_key}
        response = requests.get(
            f"http://{self.ip}:{self.port}/api/version",
            headers=headers,
        )
        if response.status_code == 200:
            self.connected = True
            return
        self.connected = False

    def send(self, filename: str, file: io.BytesIO, logger: queue.Queue) -> bool:
        headers={
            "X-Api-Key": self.api_key,
            "Overwrite": "?1",
        }
        for i in range(1, MAX_SEND_RETRY+1):
            try:
                response = requests.put(
                    f"http://{self.ip}:{self.port}/api/v1/files/usb/{filename}",
                    data=file,
                    headers=headers,
                )
                if response.status_code == 201:
                    return True
            except BaseException as exception:
                logger.put(f"{type(exception).__name__}: reattempting to send to {self.name} ({i}/{MAX_SEND_RETRY})")
                time.sleep(1)
        return False

    def disconnect(self) -> bool:
        self.connected = False
