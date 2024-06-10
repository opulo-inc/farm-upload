"""
This is an extension of the ftplib python module to support implicit FTPS connections and file transfer for Bambu Lab 3D printers.

It is based heavily off of the extension made by tfboy: https://python-forum.io/thread-39467.html
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import ftplib
import ssl, os
from socket import (  # type: ignore[attr-defined]
    _GLOBAL_DEFAULT_TIMEOUT,
    socket,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    import _typeshed

class Error(Exception): pass
CRLF = '\r\n'
B_CRLF = b'\r\n'

_SSLSocket = ssl.SSLSocket

# ftps = FTP('192.168.1.204', 990)
# ftps.debugging = 2
# #ftps.connect('192.168.1.212', 990)
# ftps.login('bblp', '94679547')
# #ftps.prot_p()

# require implicit ftp over tls

class BambuFTP(ftplib.FTP_TLS):
    """FTP_TLS subclass that automatically wraps sockets in SSL to support implicit FTPS."""
    def __init__(
        self,
        host: str = '',
        user: str = '',
        passwd: str = '',
        acct: str = '',
        *,
        context: ssl.SSLContext | None = None,
        timeout: float = _GLOBAL_DEFAULT_TIMEOUT,
        source_address: tuple[str, int] | None = None,
        encoding: str = 'utf-8'
    ) -> None:
        super().__init__(host, user, passwd, acct,
                         context=context, timeout=timeout,
                         source_address=source_address, encoding=encoding)
        self._sock: ssl.SSLSocket | None = None

    @property  # type: ignore[override]
    def sock(self) -> ssl.SSLSocket | None:
        """Return the socket."""
        return self._sock

    @sock.setter
    def sock(self, value: socket | ssl.SSLSocket | None) -> None:
        """When modifying the socket, ensure that it is ssl wrapped."""
        if value is not None and not isinstance(value, ssl.SSLSocket):
            self._sock = self.context.wrap_socket(value)
            return
        self._sock = value

    def storlines(
        self,
        cmd: str,
        fp: _typeshed.SupportsReadline[bytes],
        callback: Callable[[bytes], object] | None = None
    ) -> str:
        """Store a file in line mode.  A new port is created for you.

        Args:
          cmd: A STOR command.
          fp: A file-like object with a readline() method.
          callback: An optional single parameter callable that is called on
                    each line after it is sent.  [default: None]

        Returns:
          The response code.
        """
        self.voidcmd('TYPE A')
        with self.transfercmd(cmd) as conn:
            while 1:
                buf = fp.readline(self.maxline + 1)
                if len(buf) > self.maxline:
                    raise Error(f"got more than {self.maxline} bytes")
                if not buf:
                    break
                if buf[-2:] != B_CRLF:
                    if buf[-1] in B_CRLF: buf = buf[:-1]
                    buf = buf + B_CRLF
                conn.sendall(buf)
                if callback:
                    callback(buf)
            # no ssl layer to shut down, so commented out
            # if _SSLSocket is not None and isinstance(conn, _SSLSocket):
            #     conn.unwrap()
        return self.voidresp()

    def storbinary(
        self,
        cmd: str,
        fp: _typeshed.SupportsRead[bytes],
        blocksize: int = 8192,
        callback: Callable[[bytes], object] | None = None,
        rest: int | str | None = None
    ) -> str:
        """Store a file in binary mode.  A new port is created for you.

        Args:
          cmd: A STOR command.
          fp: A file-like object with a read(num_bytes) method.
          blocksize: The maximum data size to read from fp and send over
                     the connection at once.  [default: 8192]
          callback: An optional single parameter callable that is called on
                    each block of data after it is sent.  [default: None]
          rest: Passed to transfercmd().  [default: None]

        Returns:
          The response code.
        """
        self.voidcmd('TYPE I')
        with self.transfercmd(cmd, rest) as conn:
            while 1:
                buf = fp.read(blocksize)
                if not buf:
                    break
                conn.sendall(buf)
                if callback:
                    callback(buf)
            # no ssl layer to shut down, so commented out
            # if _SSLSocket is not None and isinstance(conn, _SSLSocket):
            #     conn.unwrap()
        return self.voidresp()
