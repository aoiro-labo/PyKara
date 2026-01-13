# main.py

import sys
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QColor

from ui.attract import PyKaraAttract
from config import Config
from theme.fonts import FontSet
from theme.theme import ThemeManager


def main():
    app = QApplication(sys.argv)

    # =========================
    # 設定の読み込み
    # =========================
    config = Config()
    
    # フォント設定をFontSetに設定
    FontSet.set_config(config)
    
    # テーママネージャー
    theme_manager = ThemeManager(config)

    # =========================
    # スプラッシュスクリーン
    # =========================
    pixmap = QPixmap(QSize(600, 400))
    splash_bg_color = theme_manager.get_splash_bg_color()
    pixmap.fill(splash_bg_color)

    splash = QSplashScreen(pixmap)
    splash.show()

    splash.showMessage(
        "PyKara System Booting...\n\n"
        "【注意】大音量での歌唱は近隣の迷惑にならないようご注意ください\n\n"
        "設定: F1キーを押してください",
        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
        Qt.GlobalColor.white
    )

    # =========================
    # メイン画面表示
    # =========================
    def show_attract():
        attract = PyKaraAttract(config)
        attract.show()
        splash.finish(attract)

    # 起動ディレイ（ここで楽曲DBや音声初期化を想定）
    QTimer.singleShot(3000, show_attract)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
