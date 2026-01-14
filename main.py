# main.py

import sys
import traceback
from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QColor, QMouseEvent

from ui.attract import PyKaraAttract
from config import Config
from theme.fonts import FontSet
from theme.theme import ThemeManager
from server.selection_manager import SelectionManager
from server.api_server import APIServer
from utils.logger import DebugLogger


class NonClickableSplashScreen(QSplashScreen):
    """クリックで閉じないスプラッシュスクリーン"""
    def mousePressEvent(self, event: QMouseEvent):
        event.ignore()
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        event.ignore()


class PyKaraApp(QApplication):
    """
    業務用っぽい構造：
    - ウィンドウをアプリケーションが保持
    - GC で落ちるのを防ぐ
    """
    def __init__(self, argv):
        super().__init__(argv)
        self.attract_window = None
        self.karaoke_window = None
        self.splash = None
        self.config = None
        self.logger = None
        self.selection_manager = None
        self.api_server = None
        self.theme_manager = None


def main():
    # =========================
    # 設定とロガー
    # =========================
    try:
        config = Config()
    except Exception as e:
        print(f"設定ファイル読み込み失敗: {e}")
        traceback.print_exc()
        input("Enterキーで終了...")
        sys.exit(1)

    app = PyKaraApp(sys.argv)
    app.config = config
    app.logger = DebugLogger(config)
    app.logger.info("PyKaraを起動しています...")

    try:
        # フォント設定
        FontSet.set_config(config)
        app.logger.debug("FontSetを設定しました")
        
        # テーマ管理
        app.theme_manager = ThemeManager(config)
        app.logger.debug("ThemeManager初期化完了")

        # 選曲管理
        app.selection_manager = SelectionManager()
        app.logger.debug("SelectionManager初期化完了")

        # APIサーバー
        if config.get("server.enabled", True):
            try:
                app.api_server = APIServer(app.selection_manager, config)
                app.api_server.start()
                app.logger.info(f"APIサーバー起動: {app.api_server.get_url()}")
            except Exception as e:
                app.logger.error(f"サーバー起動エラー: {e}", exc_info=sys.exc_info())
                print(f"警告: APIサーバー起動失敗, 続行: {e}")

        # =========================
        # スプラッシュスクリーン
        # =========================
        pixmap = QPixmap(QSize(600, 400))
        splash_bg_color = app.theme_manager.get_splash_bg_color()
        pixmap.fill(splash_bg_color)

        app.splash = NonClickableSplashScreen(pixmap)
        app.splash.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SplashScreen)
        app.splash.show()
        app.logger.debug("スプラッシュスクリーン表示")

        server_info = ""
        if config.get("server.enabled", True) and app.api_server:
            server_info = f"\n\nAPIサーバー: {app.api_server.get_url()}"

        app.splash.showMessage(
            "PyKara System Booting...\n\n"
            "【注意】大音量での歌唱は近隣の迷惑にならないようご注意ください\n\n"
            f"設定: F1キーを押してください{server_info}",
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
            Qt.GlobalColor.white
        )

        # =========================
        # アトラクト画面表示
        # =========================
        def show_attract():
            try:
                app.logger.debug("アトラクト画面生成中...")
                app.attract_window = PyKaraAttract(app.config, app.selection_manager)
                attract = app.attract_window
                attract.show()
                app.logger.debug("アトラクト画面 show() 完了")

                # フルスクリーン切替
                if config.get("display.fullscreen", False):
                    def set_fullscreen():
                        try:
                            attract.showFullScreen()
                            attract.raise_()
                            attract.activateWindow()
                        except Exception as e:
                            app.logger.error(f"フルスクリーン切替失敗: {e}", exc_info=sys.exc_info())
                    QTimer.singleShot(100, set_fullscreen)
                else:
                    attract.raise_()
                    attract.activateWindow()

                if app.splash:
                    app.splash.finish(attract)

                app.logger.debug("アトラクト画面表示完了")

            except Exception as e:
                app.logger.error("アトラクト画面表示失敗", exc_info=sys.exc_info())
                if app.splash:
                    app.splash.close()
                QMessageBox.critical(None, "エラー",
                                     f"アトラクト画面表示失敗:\n{str(e)}\n\n詳細:\n{traceback.format_exc()}")
                sys.exit(1)

        # 起動ディレイ後に表示
        QTimer.singleShot(3000, show_attract)
        app.logger.info("メインループ開始...")
        exit_code = app.exec()
        app.logger.info(f"アプリ終了 (終了コード: {exit_code})")
        sys.exit(exit_code)

    except Exception as e:
        app.logger.error("予期せぬエラー", exc_info=sys.exc_info())
        traceback.print_exc()
        input("Enterキーで終了...")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("中断されました")
        sys.exit(0)
    except Exception as e:
        print(f"致命的エラー: {e}")
        traceback.print_exc()
        input("Enterキーで終了...")
        sys.exit(1)
