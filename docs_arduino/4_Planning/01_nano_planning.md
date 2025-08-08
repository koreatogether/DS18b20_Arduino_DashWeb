# Arduino Nano DS18B20 센서 모니터링 시스템 개발 문서

## 프로젝트 개요

DS18B20 온도 센서를 이용한 다중 센서 모니터링 시스템의 Arduino Nano 펌웨어 개발

### 목표
- 최대 8개의 DS18B20 센서 동시 관리
- Processing과의 실시간 시리얼 통신
- 개별 센서 설정 및 제어
- 임계값 기반 경고 시스템

## 개발 환경 설정

### PlatformIO 설정
```ini
[env:nanoatmega328]
platform = atmelavr
board = nanoatmega328
framework = arduino

; 시리얼 통신 설정
monitor_speed = 9600
monitor_port = AUTO

; 업로드 설정
upload_port = AUTO
upload_speed = 57600

; Arduino IDE 호환을 위한 소스 디렉토리 설정 (루트 디렉토리)
src_dir = .

; 테스트 제외 설정
test_ignore = *

; 라이브러리 의존성
lib_deps = 
    paulstoffregen/OneWire@^2.3.7
    milesburton/DallasTemperature@^3.11.0
```

### 프로젝트 구조
```
DS18B20_Sensor_Monitor/
├── DS18B20_Sensor_Monitor.ino    # 메인 Arduino 스케치
├── SensorManager.h               # 센서 관리 헤더
├── SensorManager.cpp             # 센서 관리 구현
├── SerialCommunication.h         # 시리얼 통신 헤더
├── SerialCommunication.cpp       # 시리얼 통신 구현
├── CommandProcessor.h            # 명령 처리 헤더
├── CommandProcessor.cpp          # 명령 처리 구현
└── platformio.ini                # PlatformIO 설정
```

## 시스템 아키텍처

### 클래스 구조

#### 1. SensorManager 클래스
**역할**: DS18B20 센서들의 전반적인 관리
- 센서 스캔 및 초기화
- 온도 데이터 읽기
- 개별 센서 설정 관리
- 임계값 모니터링

**주요 메서드**:
```cpp
void begin();                                    // 초기화
void scanSensors();                             // 센서 스캔
void updateSensors();                           // 센서 데이터 업데이트
bool setSensorId(int index, int newId);         // 센서 ID 설정
bool setThresholds(int index, float upper, float lower); // 임계값 설정
bool setMeasurementInterval(int index, unsigned long intervalMs); // 측정 간격 설정
void checkThresholds();                         // 임계값 체크
```

#### 2. SerialCommunication 클래스
**역할**: Processing과의 시리얼 통신 관리
- 메시지 송수신 프로토콜 관리
- 데이터 포맷팅 및 파싱
- 하트비트 및 상태 관리

**통신 프로토콜**:
```
SENSOR_DATA,sensorId,temperature,timestamp
SYSTEM,message
ALERT,sensorId,alertType,temperature,timestamp
STATUS,status
ACK,command
ERROR,error
HEARTBEAT,timestamp,freeMemory
```

#### 3. CommandProcessor 클래스
**역할**: Processing에서 받은 명령어 처리
- 명령어 파싱 및 실행
- 파라미터 검증
- 응답 메시지 생성

**지원 명령어**:
- `SET_ID,sensorIndex,newId`: 센서 ID 변경
- `SET_THRESHOLD,sensorIndex,upper,lower`: 임계값 설정
- `SET_INTERVAL,sensorIndex,intervalMs`: 측정 주기 설정
- `GET_STATUS`: 전체 센서 상태 조회
- `SCAN_SENSORS`: 센서 재스캔
- `RESET`: 시스템 리셋

## 하드웨어 연결

### DS18B20 센서 연결
```
Arduino Nano    DS18B20
Digital Pin 2 ← Data Pin (with 4.7kΩ pullup to VCC)
5V (or 3.3V) ← VCC
GND          ← GND
```

### 회로 구성
- **전원**: 5V 또는 3.3V (센서 사양에 따라)
- **풀업 저항**: 4.7kΩ (데이터 라인과 VCC 사이)
- **최대 센서 수**: 8개 (소프트웨어 제한)

## 주요 기능 구현

### 1. 센서 자동 감지
```cpp
void SensorManager::scanSensors() {
  sensorCount = sensors.getDeviceCount();
  
  for (int i = 0; i < sensorCount; i++) {
    if (sensors.getAddress(sensorList[i].address, i)) {
      sensorList[i].isConnected = true;
      sensors.setResolution(sensorList[i].address, TEMPERATURE_PRECISION);
    }
  }
}
```

### 2. 개별 센서 설정
각 센서별로 독립적인 설정 관리:
- **센서 ID**: 1-8 범위의 사용자 정의 ID
- **임계값**: 상한/하한 온도 임계값
- **측정 간격**: 개별 센서별 측정 주기

### 3. 실시간 데이터 전송
```cpp
void SensorManager::updateSensors() {
  sensors.requestTemperatures();
  
  for (int i = 0; i < sensorCount; i++) {
    if (currentTime - sensorList[i].lastRead >= sensorList[i].interval) {
      float temp = readTemperature(i);
      serialComm.sendSensorData(sensorList[i].id, temp);
    }
  }
}
```

### 4. 임계값 모니터링
```cpp
void SensorManager::checkThresholds() {
  for (int i = 0; i < sensorCount; i++) {
    float temp = sensorList[i].temperature;
    bool isAlert = (temp > sensorList[i].upperLimit) || (temp < sensorList[i].lowerLimit);
    
    if (isAlert && !sensorList[i].thresholdAlert) {
      String alertType = (temp > sensorList[i].upperLimit) ? "HIGH" : "LOW";
      serialComm.sendAlert(sensorList[i].id, alertType, temp);
    }
  }
}
```

## 통신 프로토콜

### Processing → Arduino 명령
```
SET_ID,0,5              # 센서 0의 ID를 5로 변경
SET_THRESHOLD,1,80.0,20.0  # 센서 1의 임계값 설정
SET_INTERVAL,2,5000     # 센서 2의 측정 간격을 5초로 설정
GET_STATUS              # 전체 센서 상태 요청
```

### Arduino → Processing 응답
```
SENSOR_DATA,5,25.3,12345    # 센서 ID 5, 온도 25.3°C
ALERT,3,HIGH,85.2,12346     # 센서 ID 3, 상한 경고
SYSTEM,Sensor scan complete # 시스템 메시지
ACK,SET_ID,0,5             # 명령 수행 확인
```

## 메모리 관리

### 최적화 전략
- **정적 배열 사용**: 동적 메모리 할당 최소화
- **String 객체 최소화**: char 배열 우선 사용
- **버퍼 크기 제한**: 시리얼 버퍼 오버플로우 방지

### 메모리 모니터링
```cpp
int freeMemory() {
  char top;
  extern int __heap_start, *__brkval;
  int v;
  return (int) &top - (__brkval == 0 ? (int) &__heap_start : (int) __brkval);
}
```

## 에러 처리

### 센서 연결 오류
- 센서 연결 해제 감지
- 자동 재연결 시도
- Processing에 상태 알림

### 통신 오류
- 명령어 파싱 오류 처리
- 파라미터 검증
- 에러 메시지 전송

### 시스템 안정성
- 하트비트 메시지
- 메모리 사용량 모니터링
- 소프트웨어 리셋 기능

## 테스트 및 디버깅

### 시리얼 모니터 출력
```
SYSTEM,DS18B20 Sensor Monitor Started
SYSTEM,Arduino Nano Ready
SYSTEM,Scanning for DS18B20 sensors...
SYSTEM,Sensor 1 found: 28:AA:BB:CC:DD:EE:FF:00
SYSTEM,Total sensors found: 3
SENSOR_DATA,1,25.3,1234
SENSOR_DATA,2,26.1,1235
```

### 개발 도구
- **PlatformIO**: 크로스 플랫폼 개발 환경
- **Arduino IDE**: 호환성 유지
- **시리얼 모니터**: 실시간 디버깅

## 향후 개선 사항

### 기능 확장
- EEPROM을 이용한 설정 저장 
- 더 많은 센서 타입 지원
- 무선 통신 모듈 추가

### 성능 최적화
- 인터럽트 기반 시리얼 통신
- 저전력 모드 구현
- 더 효율적인 메모리 사용

## 결론

Arduino Nano 기반의 DS18B20 센서 모니터링 시스템이 성공적으로 구현되었습니다. 모듈화된 설계로 유지보수성과 확장성을 확보했으며, Processing과의 안정적인 통신을 통해 실시간 모니터링이 가능합니다.