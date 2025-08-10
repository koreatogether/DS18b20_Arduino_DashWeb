"""유틸리티 함수들"""

import os
import sys


def configure_console_encoding():
    """콘솔 인코딩을 설정합니다."""
    try:
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        pass


def debug_callback_registration(app):
    """콜백 등록 상태를 디버그합니다."""
    try:
        print("[DEBUG] Registered callback output keys:")
        for k in app.callback_map.keys():
            print("  -", k)
        print(f"[DEBUG] Total callbacks registered: {len(app.callback_map)}")
    except (AttributeError, KeyError) as e:
        print(f"[DEBUG] Failed to print callback_map keys: {e}")


def post_registration_audit(app):
    """등록 후 콜백 감사를 수행합니다."""
    try:
        print("[DEBUG] Post-registration callback audit:")
        for k in app.callback_map.keys():
            print("  *", k)
        print(f"[DEBUG] Callback count: {len(app.callback_map)}")
    except (AttributeError, KeyError) as e:
        print(f"[DEBUG] Callback audit failed: {e}")


def print_startup_info(arduino_connected):
    """시작 정보를 출력합니다."""
    print("🚀 DS18B20 JSON 대시보드 시작")
    print("📡 Arduino 연결 상태:", "연결됨" if arduino_connected else "연결 안됨")
    print("🌐 웹 인터페이스: http://127.0.0.1:8050")
    print("💡 Ctrl+C로 안전하게 종료하세요")
