#!/usr/bin/env python3
"""
Real-time test script for DS18B20 Embedded Application v2.
Connects to serial port, sends test inputs, reads outputs, logs results.
"""
try:
    import serial
except ImportError:
    import sys
    print('pyserial 모듈이 설치되어 있지 않습니다.')
    print(f'설치 명령: {sys.executable} -m pip install pyserial')
    sys.exit(1)
import time
import os
from datetime import datetime

# Configuration
BAUDRATE = 115200
TIMEOUT = 3  # seconds (increased to capture slower responses)
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')

 # Define test cases based on the "4-3 개별 센서 ID 변경" 체크리스트
TEST_CASES = [
    {
        'description': '메인 메뉴 진입',
        'input': 'm\n',
        'expected': ['===== 센서 제어 메뉴 =====']
    },
    {
        'description': '센서 ID 조정 메뉴 출력',
        'input': '1\n',
        'expected': ['--- 센서 ID 조정 메뉴 ---']
    },
    {
        'description': '변경할 센서 번호 선택',
        'input': '2\n',
        'expected': ['변경할 센서 번호(1~8, 취소:c) 입력:', '센서 2번을 변경할까요? (y/n, 취소:c)']
    },
    {
        'description': '변경 확인 및 새 ID 입력 프롬프트',
        'input': 'y\n',
        'expected': ['센서 2의 새로운 ID(1~8, 취소:c)를 입력하세요:']
    },
    {
        'description': '유효한 새 ID 입력 및 완료 메시지',
        'input': '1\n',
        'expected': ['[진단]', '센서 2의 ID를 1(으)로 변경 완료']
    },
    {
        'description': '변경 후 메뉴 갱신 확인',
        'input': '\n',
        'expected': ['--- 센서 ID 조정 메뉴 ---']
    },
    {
        'description': '빈 입력 에러 처리',
        'input': '\n',
        'expected': ['입력값이 올바르지 않습니다', '재입력']
    },
    {
        'description': '문자열 입력 에러 처리',
        'input': 'abc\n',
        'expected': ['입력값이 올바르지 않습니다', '재입력']
    },
    {
        'description': '범위 벗어난 번호 에러 처리',
        'input': '9\n',
        'expected': ['입력값이 올바르지 않습니다', '재입력']
    },
    {
        'description': '취소 입력 처리',
        'input': 'c\n',
        'expected': ['센서 ID 조정 메뉴로 돌아갑니다']
    },
]


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def open_serial(port):
    # Open serial and toggle DTR for soft reset
    ser = serial.Serial(port, BAUDRATE, timeout=TIMEOUT)
    try:
        ser.setDTR(False)
        time.sleep(2)
        ser.setDTR(True)
    except Exception:
        pass
    return ser


def run_tests(ser):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(LOG_DIR, f'test_{timestamp}.log')
    results = []
    with open(log_file, 'w', encoding='utf-8') as f:
        # clear initial buffer
        try:
            ser.reset_input_buffer()
        except Exception:
            pass
        for case in TEST_CASES:
            desc = case['description']
            inp = case['input']
            exp = case['expected']
            # Header and input info
            f.write(f'=== {desc} ===\n')
            f.write(f'Input: {repr(inp)}\n')
            print(f'Running: {desc}')
            ser.write(inp.encode())
            time.sleep(1)  # wait for serial output
            # Read output lines
            out_lines = []
            start_time = time.time()
            while time.time() - start_time < TIMEOUT:
                line = ser.readline().decode(errors='ignore')
                if not line:
                    break
                f.write(f'RECV: {line}')
                out_lines.append(line)
            f.write('--- End of output ---\n')
            # Combine lines and check expected substrings
            out = ''.join(out_lines)
            for e in exp:
                found = e in out
                f.write(f'Expected: "{e}" - {"FOUND" if found else "NOT FOUND"}\n')
            ok = all(e in out for e in exp)
            results.append((desc, ok))
            f.write(f'Result: {"PASS" if ok else "FAIL"}\n\n')
            print(f'Result: {"PASS" if ok else "FAIL"}')
            time.sleep(0.2)
        # Summary
        f.write('=== Summary ===\n')
        print('=== Summary ===')
        for desc, ok in results:
            mark = 'V' if ok else 'X'
            f.write(f'[{mark}] {desc}\n')
            print(f'[{mark}] {desc}')
    print(f'Logs saved to {log_file}')


if __name__ == '__main__':
    # Use default serial port COM4 for testing
    port = 'COM4'
    ensure_dir(LOG_DIR)
    try:
        ser = open_serial(port)
        time.sleep(2)  # wait for board to reset
        run_tests(ser)
    except Exception as e:
        print(f'Error: {e}')
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
