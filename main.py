# main.py

import sys
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QColor

from ui.attract import PyKaraAttract


def main():
    app = QApplication(sys.argv)

    # =========================
    # スプラッシュスクリーン
    # =========================
    pixmap = QPixmap(QSize(600, 400))
    pixmap.fill(QColor(0, 0, 0))

    splash = QSplashScreen(pixmap)
    splash.show()

    splash.showMessage(
        "PyKara System Booting...\n\n"
        "【注意】大音量での歌唱は近隣の迷惑にならないようご注意ください",
        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
        Qt.GlobalColor.white
    )

    # =========================
    # メイン画面表示
    # =========================
    def show_attract():
        attract = PyKaraAttract()
        attract.show()
        splash.finish(attract)

    # 起動ディレイ（ここで楽曲DBや音声初期化を想定）
    QTimer.singleShot(3000, show_attract)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
