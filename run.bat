@echo off
chcp 65001 >nul
echo PyKaraを起動しています...
echo.

python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo エラーが発生しました (終了コード: %ERRORLEVEL%)
    echo ========================================
    echo.
    echo デバッグモードを有効にするには、config.jsonで以下を設定してください:
    echo   "debug": {
    echo     "enabled": true,
    echo     "show_traceback": true
    echo   }
    echo.
)

pause