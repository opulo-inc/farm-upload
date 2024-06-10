from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tkinter.scrolledtext import ScrolledText


class Logger:
    """This class allows you to log to a Tkinter Text or ScrolledText widget"""

    __slots__ = ("logUI",)

    def __init__(self, logUI: ScrolledText) -> None:
        self.logUI = logUI

    def write(self, message: str) -> None:
        """Write new log message"""
        self.logUI.insert(tk.INSERT, message + "\n")
        self.logUI.see("end")
        self.logUI.update()

    def wipe(self) -> None:
        """Clear all logs."""
        self.logUI.delete('1.0', tk.END)
