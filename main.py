# main.py

import sys
import traceback
from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QColor, QMouseEvent, QMouseEvent

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
        """マウスクリックイベントを無視（閉じないようにする）"""
        event.ignore()
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """ダブルクリックイベントも無視"""
        event.ignore()


def main():
    # =========================
    # 設定の読み込み（最初に読み込む）
    # =========================
    try:
        config = Config()
    except Exception as e:
        print(f"設定ファイルの読み込みに失敗しました: {e}")
        traceback.print_exc()
        input("Enterキーを押して終了してください...")
        sys.exit(1)
    
    # デバッグロガーの初期化
    logger = DebugLogger(config)
    logger.info("PyKaraを起動しています...")
    
    try:
        app = QApplication(sys.argv)
        logger.debug("QApplicationを初期化しました")
    except Exception as e:
        logger.error("QApplicationの初期化に失敗しました", exc_info=sys.exc_info())
        if config.get("debug.enabled", False):
            traceback.print_exc()
        input("Enterキーを押して終了してください...")
        sys.exit(1)
    
    try:
        # フォント設定をFontSetに設定
        FontSet.set_config(config)
        logger.debug("FontSetを設定しました")
        
        # テーママネージャー
        theme_manager = ThemeManager(config)
        logger.debug("ThemeManagerを初期化しました")

        # =========================
        # 選曲管理とサーバーの初期化
        # =========================
        selection_manager = SelectionManager()
        logger.debug("SelectionManagerを初期化しました")
        
        api_server = None
        if config.get("server.enabled", True):
            try:
                api_server = APIServer(selection_manager, config)
                api_server.start()
                server_url = api_server.get_url()
                logger.info(f"APIサーバーを起動しました: {server_url}")
            except Exception as e:
                logger.error(f"サーバー起動エラー: {e}", exc_info=sys.exc_info())
                if not config.get("debug.enabled", False):
                    # デバッグモードでない場合は警告のみ
                    print(f"警告: サーバーの起動に失敗しましたが、続行します: {e}")

        # =========================
        # スプラッシュスクリーン
        # =========================
        try:
            pixmap = QPixmap(QSize(600, 400))
            splash_bg_color = theme_manager.get_splash_bg_color()
            pixmap.fill(splash_bg_color)

            # クリックで閉じないカスタムスプラッシュスクリーンを使用
            splash = NonClickableSplashScreen(pixmap)
            
            # ウィンドウ表示にする（フルスクリーンではない）
            splash.setWindowFlags(
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.SplashScreen
            )
            
            splash.show()
            logger.debug("スプラッシュスクリーンを表示しました")

            server_info = ""
            if config.get("server.enabled", True) and api_server:
                server_url = api_server.get_url()
                server_info = f"\n\nAPIサーバー: {server_url}"

            splash.showMessage(
                "PyKara System Booting...\n\n"
                "【注意】大音量での歌唱は近隣の迷惑にならないようご注意ください\n\n"
                f"設定: F1キーを押してください{server_info}",
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
                Qt.GlobalColor.white
            )
        except Exception as e:
            logger.error("スプラッシュスクリーンの表示に失敗しました", exc_info=sys.exc_info())
            splash = None

        # =========================
        # メイン画面表示
        # =========================
        def show_attract():
            try:
                logger.debug("アトラクト画面を表示しようとしています...")
                attract = PyKaraAttract(config, selection_manager)
                logger.debug("アトラクト画面のインスタンスを作成しました")
                
                # 表示モードを設定に応じて切り替え
                attract.show()
                logger.debug("アトラクト画面をshow()しました")
                
                # 設定に応じてフルスクリーンまたはウィンドウ表示
                fullscreen = config.get("display.fullscreen", False)
                if fullscreen:
                    # 少し待ってからフルスクリーンに（ウィンドウが確実に表示されてから）
                    def set_fullscreen():
                        try:
                            logger.debug("フルスクリーンモードに切り替えようとしています...")
                            attract.showFullScreen()
                            logger.debug("フルスクリーンモードに切り替えました")
                            attract.raise_()
                            attract.activateWindow()
                        except Exception as e:
                            logger.error(f"フルスクリーン設定エラー: {e}", exc_info=sys.exc_info())
                            # フルスクリーンに失敗しても通常表示で続行
                    
                    QTimer.singleShot(100, set_fullscreen)
                else:
                    # ウィンドウ表示の場合
                    logger.debug("ウィンドウ表示モードで表示します")
                    attract.raise_()
                    attract.activateWindow()
                
                logger.debug("アトラクト画面を表示しました")
                if splash:
                    splash.finish(attract)
            except Exception as e:
                logger.error("アトラクト画面の表示に失敗しました", exc_info=sys.exc_info())
                if splash:
                    splash.close()
                
                # エラーダイアログを表示
                error_msg = f"アトラクト画面の表示に失敗しました:\n{str(e)}"
                if config.get("debug.show_traceback", True):
                    error_msg += f"\n\n詳細:\n{traceback.format_exc()}"
                
                try:
                    msg_box = QMessageBox()
                    msg_box.setIcon(QMessageBox.Icon.Critical)
                    msg_box.setWindowTitle("エラー")
                    msg_box.setText(error_msg)
                    msg_box.exec()
                except:
                    # ダイアログ表示も失敗した場合はコンソールに出力
                    print(error_msg)
                
                sys.exit(1)

        # 起動ディレイ（ここで楽曲DBや音声初期化を想定）
        QTimer.singleShot(3000, show_attract)
        logger.info("メインループを開始します...")

        try:
            exit_code = app.exec()
            logger.info(f"アプリケーションを終了します (終了コード: {exit_code})")
            sys.exit(exit_code)
        except Exception as e:
            logger.error("メインループ中にエラーが発生しました", exc_info=sys.exc_info())
            raise
        
    except Exception as e:
        logger.error("予期しないエラーが発生しました", exc_info=sys.exc_info())
        if config.get("debug.enabled", False):
            traceback.print_exc()
        input("Enterキーを押して終了してください...")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nユーザーによって中断されました")
        sys.exit(0)
    except Exception as e:
        print(f"致命的なエラー: {e}")
        traceback.print_exc()
        input("Enterキーを押して終了してください...")
        sys.exit(1)
