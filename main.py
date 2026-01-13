import sys
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget, QSplashScreen
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QPixmap, QColor, QPalette

# --- 1. アトラクト画面（メインウィンドウ） ---
class PyKaraMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyKara - Attract Mode")
        self.showFullScreen() # カラオケ機らしく全画面
        
        # 背景を暗く
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(10, 10, 30))
        self.setPalette(palette)

        # アトラクト画面のコンテンツ
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # キャッチコピー的な表示
        self.msg = QLabel("Sing Your Soul.\n\n[ 選曲をお待ちしています ]")
        self.msg.setFont(QFont("Yu Gothic", 36, QFont.Weight.Bold))
        self.msg.setStyleSheet("color: white;")
        self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.msg)

        # 点滅エフェクト用のタイマー
        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self.toggle_flash)
        self.flash_timer.start(800)
        self.visible_state = True

    def toggle_flash(self):
        if self.visible_state:
            self.msg.setStyleSheet("color: #00FFCC;")
        else:
            self.msg.setStyleSheet("color: white;")
        self.visible_state = not self.visible_state

def start_app():
    app = QApplication(sys.argv)

    pixmap = QPixmap(QSize(600, 400))
    pixmap.fill(QColor(0, 0, 0))
    splash = QSplashScreen(pixmap)
    splash.show()

    splash.showMessage(
        "PyKara System Booting...\n\n【注意】大音量での歌唱は近隣の迷惑にならないようご注意ください",
        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
        Qt.GlobalColor.white
    )

    def show_main():
        main_win = PyKaraMain()
        main_win.show()
        splash.finish(main_win)

    QTimer.singleShot(3000, show_main)

    sys.exit(app.exec())


if __name__ == "__main__":
    start_app()
