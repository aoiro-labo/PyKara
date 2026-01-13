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

# --- 2. 起動処理関数 ---
def start_app():
    app = QApplication(sys.argv)

    # スプラッシュスクリーンの作成
    # 画像がない場合は、QPixmapで仮の背景色を生成
    pixmap = QPixmap(QSize(600, 400))
    pixmap.fill(QColor(0, 0, 0))
    splash = QSplashScreen(pixmap)
    
    # 注意文言の表示
    splash.show()
    splash.showMessage(
        "PyKara System Booting...\n\n【注意】大音量での歌唱は近隣の迷惑にならないようご注意ください", 
        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom, 
        Qt.GlobalColor.white
    )
    
    # 起動時の「溜め」（3秒間）
    # ※実際はここで楽曲データの読み込みなどを行う
    app.processEvents()
    time.sleep(3)

    # メイン画面へ
    main_win = PyKaraMain()
    main_win.show()
    splash.finish(main_win)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    start_app()
