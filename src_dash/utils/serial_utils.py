"""
PySerial 호환 안전 flush/reset 유틸리티
"""

from typing import Any


def safe_flush(ser: Any) -> None:
    """PySerial 객체의 입력/출력 버퍼를 안전하게 초기화한다."""
    if ser is None:
        return
    # 입력 버퍼 초기화
    if ser is not None and hasattr(ser, "reset_input_buffer"):
        ser.reset_input_buffer()
    elif ser is not None and hasattr(ser, "flushInput"):
        ser.flushInput()  # type: ignore[attr-defined]
    # 출력 버퍼 초기화
    if ser is not None and hasattr(ser, "reset_output_buffer"):
        ser.reset_output_buffer()
    elif ser is not None and hasattr(ser, "flushOutput"):
        ser.flushOutput()  # type: ignore[attr-defined]
