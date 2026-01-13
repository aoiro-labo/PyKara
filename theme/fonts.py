# theme/fonts.py
from PyQt6.QtGui import QFont

class FontSet:
    @staticmethod
    def title():
        f = QFont()
        f.setPointSize(36)
        f.setBold(True)
        return f

    @staticmethod
    def normal():
        f = QFont()
        f.setPointSize(20)
        return f

    @staticmethod
    def small():
        f = QFont()
        f.setPointSize(14)
        return f
