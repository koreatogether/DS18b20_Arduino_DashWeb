# API 참조 문서

## 📚 SensorController 클래스

### **개요**
DS18B20 온도 센서들을 관리하고 센서별 임계값을 설정하는 핵심 클래스
 
### **생성자**
```cpp
SensorController();
```
- 기본 생성자
- 측정 주기를 기본값(15초)으로 초기화

### **센서 ID 관리**

#### `getSensorLogicalId(int idx)`
```cpp
uint8_t getSensorLogicalId(int idx);
```
- **매개변수**: `idx` - 센서 물리 인덱스 (0~7)
- **반환값**: 센서의 논리 ID (1~8, 0=미할당)
- **설명**: 지정된 센서의 논리 ID를 조회

#### `setSensorLogicalId(int idx, uint8_t newId)`
```cpp
void setSensorLogicalId(int idx, uint8_t newId);
```
- **매개변수**: 
  - `idx` - 센서 물리 인덱스 (0~7)
  - `newId` - 새로운 논리 ID (1~8)
- **설명**: 센서에 논리 ID 할당 (EEPROM 중복 쓰기 방지)

#### `assignIDsByAddress()`
```cpp
void assignIDsByAddress();
```
- **설명**: 센서 주소 순으로 자동 ID 할당 (1, 2, 3, ...)

#### `resetAllSensorIds()`
```cpp
void resetAllSensorIds();
```
- **설명**: 모든 센서 ID를 미할당 상태로 초기화

### **임계값 관리**

#### `initializeThresholds()`
```cpp
void initializeThresholds();
```
- **설명**: EEPROM에서 모든 센서의 임계값 로드 및 초기화

#### `getUpperThreshold(int sensorIdx)`
```cpp
float getUpperThreshold(int sensorIdx);
```
- **매개변수**: `sensorIdx` - 표시 행 인덱스 (0~7)
- **반환값**: 상한 임계값 (°C)
- **설명**: 지정된 센서의 상한 임계값 조회

#### `getLowerThreshold(int sensorIdx)`
```cpp
float getLowerThreshold(int sensorIdx);
```
- **매개변수**: `sensorIdx` - 표시 행 인덱스 (0~7)
- **반환값**: 하한 임계값 (°C)
- **설명**: 지정된 센서의 하한 임계값 조회

#### `setThresholds(int sensorIdx, float upperTemp, float lowerTemp)`
```cpp
void setThresholds(int sensorIdx, float upperTemp, float lowerTemp);
```
- **매개변수**:
  - `sensorIdx` - 표시 행 인덱스 (0~7)
  - `upperTemp` - 상한 온도 (-55~125°C)
  - `lowerTemp` - 하한 온도 (-55~125°C)
- **설명**: 센서의 상/하한 임계값 설정 및 EEPROM 저장

#### `isValidTemperature(float temp)`
```cpp
bool isValidTemperature(float temp);
```
- **매개변수**: `temp` - 검증할 온도값
- **반환값**: 유효성 여부 (true/false)
- **설명**: DS18B20 범위(-55~125°C) 내 온도인지 검증

#### `resetSensorThresholds(int sensorIdx)`
```cpp
void resetSensorThresholds(int sensorIdx);
```
- **매개변수**: `sensorIdx` - 표시 행 인덱스 (0~7)
- **설명**: 지정된 센서의 임계값을 기본값으로 초기화

#### `resetAllThresholds()`
```cpp
void resetAllThresholds();
```
- **설명**: 모든 센서의 임계값을 기본값으로 초기화

### **측정 주기 관리**

#### `getMeasurementInterval()`
```cpp
unsigned long getMeasurementInterval();
```
- **반환값**: 현재 측정 주기 (밀리초)
- **설명**: 현재 설정된 측정 주기 조회

#### `setMeasurementInterval(unsigned long intervalMs)`
```cpp
void setMeasurementInterval(unsigned long intervalMs);
```
- **매개변수**: `intervalMs` - 측정 주기 (10,000~2,592,000,000ms)
- **설명**: 측정 주기 설정 및 EEPROM 저장

#### `isValidMeasurementInterval(unsigned long intervalMs)`
```cpp
bool isValidMeasurementInterval(unsigned long intervalMs);
```
- **매개변수**: `intervalMs` - 검증할 측정 주기
- **반환값**: 유효성 여부 (true/false)
- **설명**: 측정 주기가 유효 범위(10초~30일) 내인지 검증

#### `formatInterval(unsigned long intervalMs)`
```cpp
String formatInterval(unsigned long intervalMs);
```
- **매개변수**: `intervalMs` - 포맷할 측정 주기
- **반환값**: 읽기 쉬운 형태의 문자열 (예: "1시간 30분 45초")
- **설명**: 밀리초를 사람이 읽기 쉬운 형태로 변환

### **센서 상태 확인**

#### `getUpperState(int sensorIdx, float temp)`
```cpp
const char* getUpperState(int sensorIdx, float temp);
```
- **매개변수**:
  - `sensorIdx` - 표시 행 인덱스 (0~7)
  - `temp` - 현재 온도
- **반환값**: "정상" 또는 "초과"
- **설명**: 센서별 상한 임계값 기준으로 상태 판단

#### `getLowerState(int sensorIdx, float temp)`
```cpp
const char* getLowerState(int sensorIdx, float temp);
```
- **매개변수**:
  - `sensorIdx` - 표시 행 인덱스 (0~7)
  - `temp` - 현재 온도
- **반환값**: "정상" 또는 "초과"
- **설명**: 센서별 하한 임계값 기준으로 상태 판단

#### `getSensorStatus(int sensorIdx, float temp)`
```cpp
const char* getSensorStatus(int sensorIdx, float temp);
```
- **매개변수**:
  - `sensorIdx` - 표시 행 인덱스 (0~7)
  - `temp` - 현재 온도
- **반환값**: "정상", "경고", "오류"
- **설명**: 센서별 임계값 기준으로 전체 상태 판단

### **센서 테이블 관리**

#### `printSensorStatusTable()`
```cpp
void printSensorStatusTable();
```
- **설명**: 모든 센서의 상태를 테이블 형태로 시리얼 출력

#### `updateSensorRows()`
```cpp
void updateSensorRows();
```
- **설명**: 센서 데이터를 읽고 내부 테이블 업데이트

---

## 📚 MenuController 클래스

### **개요**
사용자 인터페이스를 관리하고 시리얼 입력을 처리하는 클래스

### **생성자**
```cpp
MenuController();
```
- 기본 생성자
- 상태를 Normal로 초기화

### **메뉴 출력**

#### `printMenu()`
```cpp
void printMenu();
```
- **설명**: 메인 메뉴를 시리얼로 출력

#### `printThresholdMenu()`
```cpp
void printThresholdMenu();
```
- **설명**: 임계값 설정 메뉴를 시리얼로 출력

#### `printMeasurementIntervalMenu()`
```cpp
void printMeasurementIntervalMenu();
```
- **설명**: 측정 주기 설정 메뉴를 시리얼로 출력

### **입력 처리**

#### `handleSerialInput()`
```cpp
void handleSerialInput();
```
- **설명**: 시리얼 입력을 읽고 현재 상태에 따라 처리

#### `parseIntervalInput(const String& input)`
```cpp
unsigned long parseIntervalInput(const String& input);
```
- **매개변수**: `input` - 사용자 입력 문자열
- **반환값**: 파싱된 측정 주기 (밀리초), 0=오류
- **설명**: 복합 시간 입력을 파싱 (예: "1d2h30m45s")

### **상태 관리**

#### `getAppState()`
```cpp
AppState getAppState() const;
```
- **반환값**: 현재 애플리케이션 상태
- **설명**: 현재 메뉴 상태 조회

#### `resetToNormalState()`
```cpp
void resetToNormalState();
```
- **설명**: 애플리케이션 상태를 Normal로 완전 리셋

---

## 📊 상수 및 열거형

### **센서 관련 상수**
```cpp
constexpr int SENSOR_MAX_COUNT = 8;                    // 최대 센서 개수
constexpr float DS18B20_MIN_TEMP = -55.0f;           // DS18B20 최소 온도
constexpr float DS18B20_MAX_TEMP = 125.0f;           // DS18B20 최대 온도
constexpr float DEFAULT_UPPER_THRESHOLD = 30.0f;      // 기본 상한 임계값
constexpr float DEFAULT_LOWER_THRESHOLD = 20.0f;      // 기본 하한 임계값
```

### **측정 주기 관련 상수**
```cpp
constexpr unsigned long MIN_MEASUREMENT_INTERVAL = 10000;      // 최소 측정 주기 (10초)
constexpr unsigned long MAX_MEASUREMENT_INTERVAL = 2592000000; // 최대 측정 주기 (30일)
constexpr unsigned long DEFAULT_MEASUREMENT_INTERVAL = 15000;  // 기본 측정 주기 (15초)
```

### **EEPROM 주소**
```cpp
constexpr int EEPROM_BASE_ADDR = 0;           // 센서 임계값 시작 주소
constexpr int EEPROM_SIZE_PER_SENSOR = 8;    // 센서당 EEPROM 크기
constexpr int EEPROM_INTERVAL_ADDR = 64;     // 측정 주기 저장 주소
```

### **AppState 열거형**
```cpp
enum class AppState {
    Normal,                              // 일반 모니터링 상태
    Menu,                               // 메인 메뉴
    SensorIdMenu,                       // 센서 ID 메뉴
    ThresholdMenu,                      // 임계값 메뉴
    MeasurementIntervalMenu,            // 측정 주기 메뉴
    // ... 기타 상태들
};
```

---

## 🔧 사용 예제

### **기본 사용법**
```cpp
#include "application/SensorController.h"
#include "application/MenuController.h"

SensorController sensorController;
MenuController menuController;

void setup() {
    Serial.begin(115200);
    
    // 센서 및 임계값 초기화
    sensorController.initializeThresholds();
    
    // 메뉴 상태 초기화
    menuController.resetToNormalState();
}

void loop() {
    // 시리얼 입력 처리
    menuController.handleSerialInput();
    
    // 일반 상태에서 주기적 센서 출력
    if (menuController.getAppState() == AppState::Normal) {
        static unsigned long lastPrint = 0;
        unsigned long now = millis();
        
        if (now - lastPrint >= sensorController.getMeasurementInterval()) {
            sensorController.printSensorStatusTable();
            lastPrint = now;
        }
    }
}
```

### **프로그래밍 방식 설정**
```cpp
void setupSensors() {
    // 센서 ID 자동 할당
    sensorController.assignIDsByAddress();
    
    // 센서별 임계값 설정
    sensorController.setThresholds(0, 35.0f, 15.0f);  // 센서 1: 35°C/15°C
    sensorController.setThresholds(1, 40.0f, 10.0f);  // 센서 2: 40°C/10°C
    
    // 측정 주기 설정 (30초)
    sensorController.setMeasurementInterval(30000);
}
```

---

**작성일**: 2025-08-03  
**버전**: v1.0  
**대상**: DS18B20 센서 모니터링 시스템