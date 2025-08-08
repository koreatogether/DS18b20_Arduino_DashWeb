# Arduino-Processing 시리얼 통신 테스트

## 개요
아두이노에서 프로세싱으로 임의 데이터를 전송하는 시리얼 통신 테스트 코드입니다.

## 파일 구성
- `src/Arduino_Serial_Test.ino` - 아두이노 테스트 코드
- `src_processing/Processing_Serial_Test.pde` - 프로세싱 테스트 코드

## 아두이노 코드 기능

### 전송 데이터 타입
1. **센서 데이터**: `SENSOR_DATA,sensorId,temperature,timestamp`
   - 1초마다 임의의 온도 데이터 전송
   - 센서 ID: 1-8 랜덤
   - 온도: 20.0-35.0도 랜덤

2. **시스템 메시지**: `SYSTEM,message`
   - 5회마다 카운터 정보 전송

3. **하트비트**: `HEARTBEAT,timestamp,freeMemory`
   - 10회마다 시스템 상태 전송

4. **이벤트**: `EVENT,eventType`
   - 15회마다 임의 이벤트 전송

5. **디버그 정보**: `DEBUG,info`
   - 매회 루프 카운트와 메모리 정보

### 명령 처리
- `PING` → `ACK,PONG` 응답
- `STATUS` → 현재 상태 정보 전송
- `RESET` → 카운터 리셋

## 프로세싱 코드 기능

### 자동 연결
- 일반적인 Arduino 포트 자동 검색
- COM3, COM4, COM5 (Windows) 우선 시도
- /dev/ttyUSB0, /dev/ttyACM0 (Linux) 우선 시도

### 데이터 처리
- 모든 수신 메시지 실시간 출력
- 메시지 타입별 분류 처리
- 통계 정보 표시

### 키보드 명령
- **SPACE**: Arduino에 PING 전송
- **S**: Arduino 상태 조회
- **R**: Arduino 카운터 리셋
- **C**: 재연결 시도
- **D**: 연결 해제
- **1-9**: 포트 번호로 수동 연결

### 화면 표시
- 연결 상태 (초록/빨강)
- 메시지 통계 (총 메시지, 센서 데이터, 하트비트, 에러)
- 최근 15개 메시지 목록
- 최근 10개 센서 데이터

## 사용 방법

### 1. 아두이노 업로드
```
1. Arduino IDE에서 src/Arduino_Serial_Test.ino 열기
2. 보드와 포트 선택
3. 업로드
```

### 2. 프로세싱 실행
```
1. Processing IDE에서 src_processing/Processing_Serial_Test.pde 열기
2. 실행 (Ctrl+R)
3. 콘솔에서 연결 상태 확인
```

### 3. 테스트 확인
```
1. 프로세싱 콘솔에서 데이터 수신 확인
2. 1초마다 센서 데이터 수신 확인
3. 키보드 명령으로 양방향 통신 테스트
```

## 예상 출력

### 아두이노 시리얼 모니터
```
SYSTEM,ARDUINO_STARTED
SYSTEM,READY_TO_SEND_DATA
SYSTEM,SERIAL_TEST_MODE_ACTIVE
SENSOR_DATA,3,24.50,1234
DEBUG,LOOP_COUNT_1,FREE_MEMORY_1500
SENSOR_DATA,7,28.30,2234
DEBUG,LOOP_COUNT_2,FREE_MEMORY_1500
...
```

### 프로세싱 콘솔
```
=== Processing Serial Test 시작 ===
사용 가능한 시리얼 포트:
  [0] COM1
  [1] COM3
Arduino 연결 성공: COM3
수신: SYSTEM,ARDUINO_STARTED
  -> 시스템: ARDUINO_STARTED
수신: SENSOR_DATA,3,24.50,1234
  -> 센서 데이터: ID=3, 온도=24.50°C
...
```

## 문제 해결

### 연결 실패 시
1. Arduino가 올바른 포트에 연결되었는지 확인
2. 다른 프로그램에서 시리얼 포트를 사용 중인지 확인
3. Processing에서 1-9 키로 수동 포트 선택 시도

### 데이터 수신 안됨
1. Arduino 시리얼 모니터에서 데이터 전송 확인
2. 보드레이트 115200 확인
3. USB 케이블 상태 확인

### 메모리 부족
1. Arduino 시리얼 모니터에서 FREE_MEMORY 값 확인
2. 필요시 SEND_INTERVAL 증가

## 확장 가능성
- 실제 센서 데이터로 교체
- 그래프 시각화 추가
- 데이터 로깅 기능
- 설정 변경 명령 추가
- 에러 처리 강화