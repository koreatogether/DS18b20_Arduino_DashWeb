"""연결 관련 유틸리티 함수들"""

import time


def safe_disconnect_arduino(arduino):
    """Arduino를 안전하게 연결 해제합니다."""
    try:
        arduino.disconnect()
        time.sleep(0.5)
    except (AttributeError, OSError):
        pass


def attempt_arduino_connection(arduino, port):
    """Arduino 연결을 시도합니다."""
    try:
        if port:
            arduino.port = port
        return arduino.connect()
    except (OSError, AttributeError):
        return False


def attempt_data_reading(arduino):
    """Arduino에서 데이터 읽기를 시도합니다."""
    try:
        return arduino.start_reading()
    except (OSError, AttributeError):
        return False


def get_port_options_safely():
    """포트 옵션을 안전하게 가져옵니다."""
    try:
        from serial.tools import list_ports
    except ImportError:
        return None, None

    try:
        ports = list(list_ports.comports())
        options = []
        default_val = None

        for p in ports:
            label = f"{p.device} - {p.description}"
            options.append({"label": label, "value": p.device})

        if ports:
            default_val = ports[0].device

        return options, default_val
    except (OSError, AttributeError):
        return None, None


def create_fallback_port_options():
    """기본 포트 옵션을 생성합니다."""
    options = [{"label": f"COM{i}", "value": f"COM{i}"} for i in range(1, 11)]
    return options, "COM4"
