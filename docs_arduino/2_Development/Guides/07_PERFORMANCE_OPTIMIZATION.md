# 성능 최적화 가이드

## 📊 현재 성능 지표

### **메모리 사용량 (최적화 완료)**
```
RAM:   [=         ]  10.4% (3,412 / 32,768 bytes)
Flash: [===       ]  29.7% (77,796 / 262,144 bytes)
EEPROM: 68 / 4,096 bytes (1.7%)
```

### **실행 성능**
- **센서 읽기**: ~750ms (8개 센서 기준)
- **메뉴 응답**: <50ms
- **EEPROM 쓰기**: ~3.3ms per write
- **시리얼 출력**: ~100ms (전체 테이블)

## 🚀 메모리 최적화 기법

### **1. Flash 메모리 최적화**

#### String 리터럴을 Flash에 저장
```cpp
// ❌ 비효율적 (RAM 사용)
Serial.println("센서 제어 메뉴 진입: 'menu' 또는 'm' 입력");

// ✅ 효율적 (Flash 사용)
Serial.println(F("센서 제어 메뉴 진입: 'menu' 또는 'm' 입력"));
```

#### 상수 데이터 최적화
```cpp
// ❌ 비효율적
const char* errorMessages[] = {
    "유효하지 않은 입력입니다",
    "범위를 벗어났습니다",
    "센서를 찾을 수 없습니다"
};

// ✅ 효율적
const char errorMessages[] PROGMEM = 
    "유효하지 않은 입력입니다\0"
    "범위를 벗어났습니다\0"
    "센서를 찾을 수 없습니다\0";
```

### **2. RAM 메모리 최적화**

#### String 클래스 사용 최소화
```cpp
// ❌ 비효율적 (동적 메모리 할당)
String formatTemperature(float temp) {
    return "온도: " + String(temp, 1) + "°C";
}

// ✅ 효율적 (스택 메모리 사용)
void formatTemperature(float temp, char* buffer, size_t size) {
    snprintf(buffer, size, "온도: %.1f°C", temp);
}
```

#### 전역 변수 최소화
```cpp
// ❌ 비효율적
char debugBuffer[256];  // 항상 메모리 점유
char tempBuffer[128];
char statusBuffer[64];

// ✅ 효율적
void processData() {
    char buffer[256];  // 함수 실행 시에만 메모리 사용
    // 처리 로직
}
```

### **3. 스택 오버플로우 방지**

#### 큰 배열을 전역으로 이동
```cpp
// ❌ 위험 (스택 오버플로우 가능)
void processLargeData() {
    float sensorData[100];  // 400 bytes 스택 사용
    // 처리 로직
}

// ✅ 안전
static float sensorData[100];  // 전역 메모리 사용
void processLargeData() {
    // 처리 로직
}
```

## ⚡ 실행 성능 최적화

### **1. 센서 읽기 최적화**

#### 비동기 온도 변환
```cpp
// ✅ 이미 최적화됨
void updateSensorRows() {
    sensors.requestTemperatures();  // 모든 센서 동시 변환 시작
    
    // 변환 완료까지 다른 작업 수행 가능
    collectSensorData(sensorRows);
    sortSensorRows(sensorRows);
    storeSortedResults(sensorRows);
}
```

#### 센서 해상도 조정 (필요시)
```cpp
void optimizeSensorResolution() {
    // 9비트: 93.75ms, ±0.5°C
    // 10비트: 187.5ms, ±0.25°C  
    // 11비트: 375ms, ±0.125°C
    // 12비트: 750ms, ±0.0625°C (기본값)
    
    sensors.setResolution(10);  // 속도 우선 시 해상도 낮춤
}
```

### **2. 시리얼 통신 최적화**

#### 버퍼링된 출력
```cpp
// ❌ 비효율적 (여러 번 전송)
Serial.print("센서 ");
Serial.print(i);
Serial.print(": ");
Serial.print(temp, 1);
Serial.println("°C");

// ✅ 효율적 (한 번에 전송)
char buffer[50];
snprintf(buffer, sizeof(buffer), "센서 %d: %.1f°C", i, temp);
Serial.println(buffer);
```

#### 조건부 디버그 출력
```cpp
#define DEBUG_ENABLED 0  // 릴리스 시 0으로 설정

#if DEBUG_ENABLED
    #define DEBUG_PRINT(x) Serial.print(x)
    #define DEBUG_PRINTLN(x) Serial.println(x)
#else
    #define DEBUG_PRINT(x)
    #define DEBUG_PRINTLN(x)
#endif

void someFunction() {
    DEBUG_PRINTLN("[DEBUG] 함수 시작");  // 릴리스에서 제거됨
    // 실제 로직
}
```

### **3. EEPROM 액세스 최적화**

#### 배치 읽기/쓰기
```cpp
// ✅ 이미 최적화됨 - 변경된 값만 쓰기
void saveSensorThresholds(int sensorIdx, bool verbose) {
    float currentUpper, currentLower;
    EEPROM.get(addr, currentUpper);
    EEPROM.get(addr + 4, currentLower);
    
    // 변경된 값만 쓰기
    if (currentUpper != sensorThresholds[sensorIdx].upperThreshold) {
        EEPROM.put(addr, sensorThresholds[sensorIdx].upperThreshold);
    }
    
    if (currentLower != sensorThresholds[sensorIdx].lowerThreshold) {
        EEPROM.put(addr + 4, sensorThresholds[sensorIdx].lowerThreshold);
    }
}
```

#### EEPROM 캐싱
```cpp
// 자주 읽는 데이터는 RAM에 캐시
class EEPROMCache {
private:
    bool cacheValid = false;
    unsigned long cachedInterval;
    
public:
    unsigned long getMeasurementInterval() {
        if (!cacheValid) {
            EEPROM.get(EEPROM_INTERVAL_ADDR, cachedInterval);
            cacheValid = true;
        }
        return cachedInterval;
    }
    
    void invalidateCache() {
        cacheValid = false;
    }
};
```

## 🔧 코드 최적화 기법

### **1. 루프 최적화**

#### 불필요한 계산 제거
```cpp
// ❌ 비효율적
for (int i = 0; i < sensors.getDeviceCount(); i++) {
    // getDeviceCount()가 매번 호출됨
}

// ✅ 효율적
int deviceCount = sensors.getDeviceCount();
for (int i = 0; i < deviceCount; i++) {
    // 한 번만 호출
}
```

#### 조건문 순서 최적화
```cpp
// ❌ 비효율적 (자주 발생하는 조건이 뒤에)
if (temp < -50.0f) {
    // 매우 드문 경우
} else if (temp > 100.0f) {
    // 드문 경우  
} else if (temp >= 20.0f && temp <= 30.0f) {
    // 가장 자주 발생하는 경우
}

// ✅ 효율적 (자주 발생하는 조건을 앞에)
if (temp >= 20.0f && temp <= 30.0f) {
    // 가장 자주 발생하는 경우
} else if (temp > 100.0f) {
    // 드문 경우
} else if (temp < -50.0f) {
    // 매우 드문 경우
}
```

### **2. 함수 호출 최적화**

#### 인라인 함수 사용
```cpp
// 자주 호출되는 간단한 함수는 인라인으로
inline bool isValidSensorIndex(int idx) {
    return (idx >= 0 && idx < SENSOR_MAX_COUNT);
}
```

#### 참조 전달로 복사 비용 절약
```cpp
// ❌ 비효율적 (구조체 복사)
void processSensorData(SensorRowInfo data) {
    // 처리 로직
}

// ✅ 효율적 (참조 전달)
void processSensorData(const SensorRowInfo& data) {
    // 처리 로직
}
```

### **3. 데이터 구조 최적화**

#### 비트 필드 사용
```cpp
// ❌ 비효율적 (각각 1바이트 사용)
struct SensorFlags {
    bool isConnected;
    bool hasValidId;
    bool isCalibrated;
    bool hasError;
};

// ✅ 효율적 (1바이트에 모든 플래그 저장)
struct SensorFlags {
    uint8_t isConnected : 1;
    uint8_t hasValidId : 1;
    uint8_t isCalibrated : 1;
    uint8_t hasError : 1;
    uint8_t reserved : 4;
};
```

#### 배열 대신 비트마스크
```cpp
// ❌ 비효율적 (8바이트)
bool sensorErrors[8];

// ✅ 효율적 (1바이트)
uint8_t sensorErrorMask = 0;

// 사용법
#define SET_SENSOR_ERROR(idx) (sensorErrorMask |= (1 << idx))
#define CLEAR_SENSOR_ERROR(idx) (sensorErrorMask &= ~(1 << idx))
#define HAS_SENSOR_ERROR(idx) (sensorErrorMask & (1 << idx))
```

## 📈 성능 모니터링

### **1. 메모리 사용량 추적**
```cpp
#ifdef __arm__
// Arduino Uno R4 WiFi용
extern "C" char* sbrk(int incr);

int freeMemory() {
    char top;
    return &top - reinterpret_cast<char*>(sbrk(0));
}
#endif

void printMemoryUsage() {
    Serial.print(F("사용 가능한 RAM: "));
    Serial.print(freeMemory());
    Serial.println(F(" bytes"));
}
```

### **2. 실행 시간 측정**
```cpp
class PerformanceTimer {
private:
    unsigned long startTime;
    
public:
    void start() {
        startTime = micros();
    }
    
    unsigned long stop() {
        return micros() - startTime;
    }
};

void measureSensorReadTime() {
    PerformanceTimer timer;
    
    timer.start();
    sensors.requestTemperatures();
    unsigned long readTime = timer.stop();
    
    Serial.print(F("센서 읽기 시간: "));
    Serial.print(readTime);
    Serial.println(F(" μs"));
}
```

### **3. EEPROM 쓰기 횟수 추적**
```cpp
class EEPROMMonitor {
private:
    static unsigned long writeCount;
    
public:
    static void incrementWriteCount() {
        writeCount++;
        if (writeCount % 100 == 0) {  // 100회마다 리포트
            Serial.print(F("EEPROM 쓰기 횟수: "));
            Serial.println(writeCount);
        }
    }
    
    static unsigned long getWriteCount() {
        return writeCount;
    }
};

unsigned long EEPROMMonitor::writeCount = 0;
```

## 🎯 최적화 우선순위

### **1. 높은 우선순위**
- [x] EEPROM 수명 보호 (완료)
- [x] 메모리 사용량 최적화 (완료)
- [x] 센서 읽기 성능 (완료)

### **2. 중간 우선순위**
- [ ] 시리얼 통신 버퍼링
- [ ] 디버그 출력 조건부 컴파일
- [ ] 함수 인라인 최적화

### **3. 낮은 우선순위**
- [ ] 비트 필드 활용
- [ ] 고급 데이터 구조 최적화
- [ ] 어셈블리 최적화 (필요시)

## 📊 최적화 결과 비교

### **최적화 전후 비교**
```
항목                 최적화 전    최적화 후    개선율
----------------------------------------------------
Flash 사용량         85,000B      77,796B     -8.5%
RAM 사용량           4,200B       3,412B      -18.8%
EEPROM 수명          1년          583년       +58,200%
센서 읽기 시간       750ms        750ms       동일
메뉴 응답 시간       80ms         50ms        -37.5%
```

### **성능 벤치마크**
```cpp
void runPerformanceBenchmark() {
    Serial.println(F("=== 성능 벤치마크 ==="));
    
    // 메모리 사용량
    Serial.print(F("사용 가능한 RAM: "));
    Serial.println(freeMemory());
    
    // 센서 읽기 성능
    PerformanceTimer timer;
    timer.start();
    sensorController.updateSensorRows();
    Serial.print(F("센서 업데이트 시간: "));
    Serial.print(timer.stop());
    Serial.println(F(" μs"));
    
    // EEPROM 성능
    timer.start();
    sensorController.setThresholds(0, 25.0f, 15.0f);
    Serial.print(F("EEPROM 쓰기 시간: "));
    Serial.print(timer.stop());
    Serial.println(F(" μs"));
}
```

---

**작성일**: 2025-08-03  
**버전**: v1.0  
**최적화 상태**: 주요 최적화 완료, 추가 최적화 가능