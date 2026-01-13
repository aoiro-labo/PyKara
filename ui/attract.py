# ui/attract.py

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPalette

from theme.fonts import FontSet


class PyKaraAttract(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyKara - Attract Mode")
        self.showFullScreen()

        # 背景色（業務用っぽく暗め）
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(10, 10, 30))
        self.setPalette(palette)

        # 中央ウィジェット
        central = QWidget(self)
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # メインメッセージ
        self.msg = QLabel(
            "Sing Your Soul.\n\n"
            "[ 選曲をお待ちしています ]"
        )
        self.msg.setFont(FontSet.title())
        self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg.setStyleSheet("color: white;")

        layout.addWidget(self.msg)

        # 点滅用タイマー
        self._flash_state = False
        self.flash_timer = QTimer(self)
        self.flash_timer.timeout.connect(self._toggle_flash)
        self.flash_timer.start(800)

    def _toggle_flash(self):
        if self._flash_state:
            self.msg.setStyleSheet("color: white;")
        else:
            self.msg.setStyleSheet("color: #00FFCC;")
        self._flash_state = not self._flash_state
