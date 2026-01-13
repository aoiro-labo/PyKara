# utils/logger.py
import logging
import sys
from pathlib import Path
from datetime import datetime
from config import Config

class DebugLogger:
    """デバッグロガー"""
    
    def __init__(self, config: Config):
        self.config = config
        self.debug_enabled = config.get("debug.enabled", False)
        self.show_traceback = config.get("debug.show_traceback", True)
        self.log_to_file = config.get("debug.log_to_file", False)
        self.log_file = config.get("debug.log_file", "pykara_debug.log")
        
        self.logger = None
        if self.debug_enabled:
            self._setup_logger()
    
    def _setup_logger(self):
        """ロガーをセットアップ"""
        self.logger = logging.getLogger('PyKara')
        self.logger.setLevel(logging.DEBUG)
        
        # コンソールハンドラー
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # ファイルハンドラー（オプション）
        if self.log_to_file:
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """デバッグメッセージを出力"""
        if self.debug_enabled and self.logger:
            self.logger.debug(message)
        elif self.debug_enabled:
            print(f"[DEBUG] {message}")
    
    def info(self, message: str):
        """情報メッセージを出力"""
        if self.debug_enabled and self.logger:
            self.logger.info(message)
        elif self.debug_enabled:
            print(f"[INFO] {message}")
    
    def warning(self, message: str):
        """警告メッセージを出力"""
        if self.debug_enabled and self.logger:
            self.logger.warning(message)
        print(f"[WARNING] {message}")
    
    def error(self, message: str, exc_info=None):
        """エラーメッセージを出力"""
        if self.debug_enabled and self.logger:
            self.logger.error(message, exc_info=exc_info)
        print(f"[ERROR] {message}")
        if exc_info and self.show_traceback:
            import traceback
            traceback.print_exception(*exc_info)
    
    def exception(self, message: str):
        """例外情報を出力"""
        if self.debug_enabled and self.logger:
            self.logger.exception(message)
        print(f"[EXCEPTION] {message}")
        if self.show_traceback:
            import traceback
            traceback.print_exc()
