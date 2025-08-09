"""Arduino 연결 및 관리 모듈"""
import time
from .serial_json_communication import ArduinoJSONSerial
from .port_manager import find_arduino_port

try:
    from serial.tools import list_ports
except Exception:
    list_ports = None


def get_initial_port_options():
    """초기 포트 옵션을 가져옵니다."""
    try:
        options = []
        default_val = None
        if list_ports is not None:
            ports = list(list_ports.comports())
            for p in ports:
                label = f"{p.device} - {p.description}"
                options.append({'label': label, 'value': p.device})
            if ports:
                default_val = ports[0].device
        if not options:
            options = [{'label': f'COM{i}', 'value': f'COM{i}'} for i in range(1, 11)]
            default_val = 'COM4'
        return options, default_val
    except Exception:
        return [], None


def try_arduino_connection(arduino, max_attempts=3):
    """Arduino 연결을 시도합니다."""
    for attempt in range(1, max_attempts + 1):
        print(f"🔄 Arduino 연결 시도 {attempt}/{max_attempts}...")
        try:
            if arduino.connect():
                if arduino.start_reading():
                    print("✅ Arduino 연결 및 데이터 읽기 시작 성공!")
                    return True
                else:
                    print("⚠️ 연결은 성공했지만 데이터 읽기 시작 실패")
                    arduino.disconnect()
            else:
                print(f"❌ 연결 시도 {attempt} 실패")
        except (ConnectionError, OSError, PermissionError) as e:
            print(f"❌ 연결 오류 (시도 {attempt}): {e}")
        if attempt < max_attempts:
            print("⏳ 2초 후 재시도...")
            time.sleep(2)
    print("❌ 모든 연결 시도 실패 - 시뮬레이션 모드")
    return False


def initialize_arduino():
    """Arduino를 초기화하고 연결을 시도합니다."""
    # 포트 옵션 가져오기
    initial_port_options, initial_port_value = get_initial_port_options()
    
    # 포트 자동 감지
    detected_port = find_arduino_port()
    selected_port = detected_port
    skip_connect = False
    
    if detected_port:
        print(f"✅ Arduino 포트 자동 감지: {detected_port}")
    else:
        print("⚠️ Arduino 포트 자동 감지 실패: UI에서 선택")
        skip_connect = True
    
    # Arduino 객체 생성
    arduino = ArduinoJSONSerial(port=selected_port or 'COM4', baudrate=115200)
    arduino_connected = False
    
    # 연결 시도
    if not skip_connect:
        arduino_connected = try_arduino_connection(arduino)
    else:
        print("연결 시도 건너뜀 (시뮬레이션)")
    
    return {
        'arduino': arduino,
        'connected': arduino_connected,
        'initial_port_options': initial_port_options,
        'selected_port': selected_port,
        'initial_port_value': initial_port_value
    }


def cleanup_arduino_resources(arduino):
    """Arduino 리소스를 정리합니다."""
    print("🔧 Arduino 리소스 정리 중...")
    try:
        if arduino and hasattr(arduino, 'is_connected') and arduino.is_connected:
            arduino.disconnect()
            print("🔌 Arduino 연결 종료")
    except Exception as e:
        print(f"⚠️ Arduino 연결 해제 중 오류: {e}")
    
    try:
        import threading
        active_threads = threading.active_count()
        if active_threads > 1:
            print(f"⏳ 활성 스레드 {active_threads}개 종료 대기...")
            time.sleep(0.5)
    except Exception as e:
        print(f"⚠️ 스레드 정리 중 오류: {e}")
    
    print("✅ Arduino 리소스 정리 완료")