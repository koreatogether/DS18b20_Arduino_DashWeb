# 최근 주요 에러 기록 및 해결방법

## ⏳ 5. 시리얼 준비 대기 시간 제한 (3초)

### 에러 상황 및 개선 배경
```
Arduino 펌웨어에서 Serial.begin() 이후, 호스트(PC)와 연결이 지연되거나 권한 문제가 발생할 경우
기존에는 while(!Serial)로 무한 대기하여, Python/Windows에서 포트 점유 또는 PermissionError가 발생하면
펌웨어가 영원히 대기 상태에 빠질 수 있음
```

### 원인
- Serial 객체가 준비될 때까지 무한 대기 → 포트 권한 문제 시 펌웨어가 멈춤
- Windows/호스트에서 COM 포트가 점유되면, Arduino가 정상적으로 동작하지 않음

### 해결방법
```cpp
// DS18B20_Arduino.ino
Serial.begin(115200);
// 시리얼 준비 대기 시간 최대 3초로 제한
unsigned long __serialWaitStart = millis();
while (!Serial && (millis() - __serialWaitStart) < 3000) {
    delay(10);
}
```

### 효과
- 포트 권한 문제나 연결 지연 시, 펌웨어가 3초 후 자동 진행 → 무한 대기 방지
- Python/Windows에서 포트 점유/PermissionError 발생 시, 펌웨어가 멈추지 않고 정상적으로 동작
- 실시간 연결/해제 및 재연결 시, 시스템 전체 안정성 향상

### 교훈
- 펌웨어에서 무한 대기 루프는 반드시 제한을 두어야 함
- 호스트와의 연결 실패/지연 상황을 고려한 방어적 코드가 필요

**추가일:** 2025-08-08

## 🔥 1. COM 포트 점유 문제 (가장 심각)

### 에러 상황
```
PermissionError(13, '액세스가 거부되었습니다.', None, 5)
could not open port 'COM4': PermissionError
```

### 원인
- Python 프로세스가 강제 종료되어도 COM4 포트를 계속 점유
- 여러 Python 인스턴스가 동시에 같은 포트에 접근 시도

### 해결방법
```bash
# 1. 실행 중인 Python 프로세스 확인
tasklist | findstr python

# 2. 모든 Python 프로세스 강제 종료
taskkill /F /PID [프로세스ID]
# 또는 모든 Python 프로세스 한번에 종료
taskkill /F /IM python.exe

# 3. 포트 해제 대기 (2초)
# 4. 재연결 시도
```

### 예방책
```python
# 안전한 종료 시그널 핸들러 구현
import signal
def signal_handler(sig, frame):
    cleanup_resources()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
```

---

## 🐛 2. Dash 콜백 함수 누락 오류

### 에러 상황
```
KeyError: "Callback function not found for output '..connection-status.children...'"
ERROR:app:Exception on /_dash-update-component [POST]
```

### 원인
- 자동 포맷팅으로 인해 `update_dashboard` 함수의 `return` 문이 손상됨
- 함수가 완전하지 않아 콜백이 제대로 등록되지 않음

### 해결방법
```python
# update_dashboard 함수 끝에 반드시 return 문 추가
@callback(
    [Output('connection-status', 'children'),
     Output('connection-status', 'style'),
     Output('temp-graph', 'figure'),
     Output('system-log', 'children')] +
    [Output(f'sensor-{i}-temp', 'children') for i in range(1, 9)] +
    [Output(f'sensor-{i}-status', 'children') for i in range(1, 9)],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n_intervals):
    # ... 함수 내용 ...
    
    # 🔥 중요: 반드시 모든 Output에 대응하는 값을 return
    return ([connection_status, connection_style, fig, log_entries] +
            sensor_temps + sensor_statuses)
```

### 예방책
- 자동 포맷팅 후 항상 함수 완전성 확인
- return 문이 함수 내부에 올바르게 위치하는지 검증

---

## 📦 3. 모듈 의존성 오류

### 에러 상황
```
ModuleNotFoundError: No module named 'psutil'
ModuleNotFoundError: No module named 'port_manager'
```

### 원인
- `psutil` 모듈이 설치되지 않았는데 `port_manager.py`에서 사용
- 상대 import 경로 문제로 `port_manager` 모듈을 찾을 수 없음

### 해결방법
```python
# 1. psutil 의존성 제거
# port_manager.py에서 psutil import 제거
import serial
import serial.tools.list_ports
import time
import os
# import psutil  # 제거됨

# 2. 조건부 import로 fallback 구현
try:
    from port_manager import safe_connect_to_port, find_arduino_port
except ImportError:
    safe_connect_to_port = None
    find_arduino_port = None

# 3. fallback 로직 추가
if safe_connect_to_port and find_arduino_port:
    # 포트 관리자 사용
    self.serial_connection = safe_connect_to_port(self.port, self.baudrate)
else:
    # 기본 시리얼 연결 사용
    self.serial_connection = serial.Serial(
        port=self.port,
        baudrate=self.baudrate,
        timeout=2
    )
```

### 예방책
- 외부 의존성 최소화
- 필수가 아닌 모듈은 조건부 import 사용
- fallback 로직으로 안정성 확보

---

## 🎯 해결 결과

### ✅ 최종 성공 상태
1. **COM4 포트**: 안정적 연결/해제 ✅
2. **웹 대시보드**: 완벽 작동 (http://127.0.0.1:8050) ✅  
3. **Arduino 데이터**: 실시간 수신 확인 ✅
   - CSV: `SENSOR_DATA,1,28.81,462845`
   - JSON: `{"type":"sensor","id":1,"temp":25.50,"status":"ok"}`

### 🚀 현재 작동 기능
- 5개 센서 실시간 온도 모니터링
- JSON/CSV 하이브리드 통신
- 웹 기반 반응형 대시보드
- 자동 재연결 및 오류 복구

---

**작성일:** 2025-08-08  
**상태:** 모든 주요 에러 해결 완료 ✅
---

## 🔌
 4. 시리얼 통신 데이터 수신 실패 (치명적 문제)

### 에러 상황
```
INFO:serial_json_communication:Arduino 상태: 대기 바이트=0, 연결=True
Arduino에서 데이터를 보내고 있지만 Python 앱에서 받지 못함
웹 대시보드에 실제 센서 데이터가 표시되지 않고 시뮬레이션 모드로 전환됨
```

### 원인 분석

#### 1. **시리얼 버퍼링 문제**
- `serial_connection.in_waiting`이 항상 0을 반환
- `readline()` 함수가 블로킹되어 데이터를 제대로 읽지 못함
- 타임아웃 설정이 부적절하여 데이터 손실 발생

#### 2. **스레드 동기화 문제**
```python
# 문제가 있던 기존 코드
if self.serial_connection.in_waiting:
    line = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
    # in_waiting이 0이면 이 블록이 실행되지 않음
```

#### 3. **포트 관리자 간섭**
- `safe_connect_to_port()` 함수가 포트를 다르게 설정
- 실제 Arduino와 Python 앱 간의 통신 설정 불일치

#### 4. **타임아웃 설정 문제**
```python
# 문제가 있던 설정
timeout=2  # 너무 긴 타임아웃으로 블로킹 발생
```

### 해결방법

#### ✅ **완전한 시리얼 통신 로직 재작성**

**1. 바이트 단위 읽기 방식 도입**
```python
# 기존 (문제 있던 방식)
if self.serial_connection.in_waiting:
    line = self.serial_connection.readline()

# 새로운 (해결된 방식)
if self.serial_connection.in_waiting > 0:
    # 모든 대기 중인 데이터를 한 번에 읽기
    data = self.serial_connection.read(self.serial_connection.in_waiting)
    text = data.decode('utf-8', errors='ignore')
    buffer += text
    
    # 완전한 라인들만 처리
    while '\n' in buffer:
        line, buffer = buffer.split('\n', 1)
        self._process_line(line.strip())
```

**2. 짧은 타임아웃 설정**
```python
# 개선된 연결 설정
self.serial_connection = serial.Serial(
    port=self.port,
    baudrate=self.baudrate,
    timeout=0.1,  # 매우 짧은 타임아웃
    write_timeout=1,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE
)
```

**3. 포트 관리자 우회**
```python
# 직접 시리얼 연결 (포트 관리자 우회)
# 복잡한 포트 관리자 대신 단순한 직접 연결 사용
```

**4. 안전한 스레드 종료**
```python
def disconnect(self):
    self.is_running = False
    
    # 스레드 종료 대기
    if self.read_thread and self.read_thread.is_alive():
        self.read_thread.join(timeout=2)
    
    # 시리얼 연결 해제
    if self.serial_connection:
        self.serial_connection.close()
```

### 테스트 결과

#### ✅ **해결 후 성공 상태**
```
🧪 새로운 Arduino 시리얼 통신 테스트
✅ Arduino 연결 성공!
📥 수신: SENSOR_DATA,1,29.25°C
📥 수신: SENSOR_DATA,2,28.75°C
📥 수신: SENSOR_DATA,3,29.19°C
📥 수신: SENSOR_DATA,4,29.25°C
📥 수신: SENSOR_DATA,5,29.62°C
📥 수신: {"type":"sensor","id":1,"temp":25.50,"status":"ok"}

[7초] 연결=True, 건강=True, 수신=30개, 센서=5개
온도: ID5:29.6°C, ID4:29.2°C, ID3:29.2°C, ID2:28.8°C, ID1:29.2°C
```

### 핵심 개선사항

#### 1. **데이터 수신 방식 변경**
- **기존**: `readline()` 기반 라인 단위 읽기
- **개선**: `read()` 기반 바이트 단위 읽기 + 버퍼링

#### 2. **블로킹 문제 해결**
- **기존**: 긴 타임아웃으로 인한 블로킹
- **개선**: 짧은 타임아웃(0.1초)으로 논블로킹 처리

#### 3. **데이터 처리 안정성**
- **기존**: `in_waiting` 체크 후 `readline()`
- **개선**: 모든 대기 데이터를 한 번에 읽고 라인별 분할 처리

#### 4. **오류 처리 강화**
- **기존**: 단순한 예외 처리
- **개선**: 상세한 로깅과 단계별 오류 복구

### 교훈

#### 🎯 **시리얼 통신 베스트 프랙티스**
1. **짧은 타임아웃 사용**: 블로킹 방지
2. **바이트 단위 읽기**: 데이터 손실 방지  
3. **버퍼링 활용**: 완전한 메시지만 처리
4. **상세한 로깅**: 문제 진단 용이성
5. **단순한 연결**: 복잡한 포트 관리자 대신 직접 연결

#### 🔧 **디버깅 방법**
1. **단계별 테스트**: 간단한 테스트 스크립트로 검증
2. **로그 분석**: `in_waiting` 값과 실제 수신 데이터 비교
3. **타임아웃 조정**: 블로킹 vs 데이터 손실 균형점 찾기
4. **버퍼 상태 모니터링**: 데이터 누적 및 처리 상태 확인

---

**해결일:** 2025-08-08  
**상태:** ✅ 완전 해결 (30개 데이터 정상 수신 확인)  
**결과:** 실시간 센서 데이터 웹 대시보드 정상 작동