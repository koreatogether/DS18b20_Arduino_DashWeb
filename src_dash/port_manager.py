"""
COM 포트 관리 유틸리티
포트 사용 상태 확인 및 강제 해제 기능
"""
import serial
import serial.tools.list_ports
# 불필요한 사용 안 함 import 제거하여 린트 경고 감소


def list_available_ports():
    """사용 가능한 시리얼 포트 목록 반환"""
    ports = serial.tools.list_ports.comports()
    available_ports = []
    
    for port in ports:
        available_ports.append({
            'device': port.device,
            'description': port.description,
            'hwid': port.hwid
        })
    
    return available_ports


def is_port_available(port_name):
    """특정 포트가 사용 가능한지 확인"""
    try:
        ser = serial.Serial(port_name, timeout=1)
        ser.close()
        return True
    except (serial.SerialException, PermissionError):
        return False


def find_arduino_port():
    """Arduino가 연결된 포트 자동 감지"""
    ports = list_available_ports()
    # 다양한 칩셋/OS 로케일 대응 (한글 포함)
    arduino_keywords = [
        'Arduino', 'CH340', 'CP210', 'FTDI', 'USB Serial', 'CDC', 'ACM',
        'USB 직렬'  # Windows 한글 로케일에서 표시
    ]
    
    for port in ports:
        description = port['description']
        desc_upper = description.upper()
        for keyword in arduino_keywords:
            # 한글/영문 모두 포함 검사
            if (keyword in description) or (keyword.upper() in desc_upper):
                if is_port_available(port['device']):
                    return port['device']
    
    return None


def test_port_manager():
    """포트 관리자 테스트 함수"""
    print("\n🔍 사용 가능한 포트 목록:")
    ports = list_available_ports()
    for port in ports:
        print(f"  {port['device']}: {port['description']}")
    
    print("\n🔍 Arduino 포트 자동 감지:")
    arduino_port = find_arduino_port()
    if arduino_port:
        print(f"  Arduino 발견: {arduino_port}")
    else:
        print("  Arduino를 찾을 수 없습니다")


if __name__ == "__main__":
    test_port_manager()