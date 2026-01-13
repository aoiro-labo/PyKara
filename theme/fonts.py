# theme/fonts.py
from PyQt6.QtGui import QFont
from config import Config

class FontSet:
    """フォント設定クラス（設定に対応）"""
    
    _config: Config = None
    
    @classmethod
    def set_config(cls, config: Config):
        """設定オブジェクトを設定"""
        cls._config = config
    
    @classmethod
    def _get_font(cls, size_key: str, bold_key: str, default_size: int, default_bold: bool = False) -> QFont:
        """フォントを取得（設定を参照）"""
        f = QFont()
        
        if cls._config:
            family = cls._config.get("font.family", "")
            if family:
                f.setFamily(family)
            
            size = cls._config.get(f"font.{size_key}", default_size)
            f.setPointSize(size)
            
            bold = cls._config.get(f"font.{bold_key}", default_bold)
            f.setBold(bold)
        else:
            # 設定が未設定の場合はデフォルト値を使用
            f.setPointSize(default_size)
            f.setBold(default_bold)
        
        return f
    
    @classmethod
    def title(cls):
        return cls._get_font("title_size", "title_bold", 36, True)
    
    @classmethod
    def normal(cls):
        return cls._get_font("normal_size", "normal_bold", 20, False)
    
    @classmethod
    def small(cls):
        return cls._get_font("small_size", "small_bold", 14, False)
