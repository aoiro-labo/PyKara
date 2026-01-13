# theme/theme.py
from PyQt6.QtGui import QColor, QPalette
from config import Config

class ThemeManager:
    """テーマ管理クラス"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def get_background_color(self) -> QColor:
        """背景色を取得"""
        rgb = self.config.get("theme.background_color", [10, 10, 30])
        return QColor(rgb[0], rgb[1], rgb[2])
    
    def get_text_color(self) -> QColor:
        """テキスト色を取得"""
        rgb = self.config.get("theme.text_color", [255, 255, 255])
        return QColor(rgb[0], rgb[1], rgb[2])
    
    def get_accent_color(self) -> QColor:
        """アクセント色を取得"""
        rgb = self.config.get("theme.accent_color", [0, 255, 204])
        return QColor(rgb[0], rgb[1], rgb[2])
    
    def get_splash_bg_color(self) -> QColor:
        """スプラッシュ背景色を取得"""
        rgb = self.config.get("theme.splash_bg_color", [0, 0, 0])
        return QColor(rgb[0], rgb[1], rgb[2])
    
    def apply_to_palette(self, palette: QPalette) -> QPalette:
        """パレットにテーマを適用"""
        palette.setColor(QPalette.ColorRole.Window, self.get_background_color())
        return palette
    
    def get_text_color_rgb(self) -> tuple:
        """テキスト色をRGBタプルで取得"""
        rgb = self.config.get("theme.text_color", [255, 255, 255])
        return tuple(rgb)
    
    def get_accent_color_rgb(self) -> tuple:
        """アクセント色をRGBタプルで取得"""
        rgb = self.config.get("theme.accent_color", [0, 255, 204])
        return tuple(rgb)
