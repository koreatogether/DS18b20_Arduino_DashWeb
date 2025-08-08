# 보안 모범 사례 가이드

## 🔒 임베디드 시스템 보안 원칙

### **1. 기본 보안 원칙**
- **최소 권한 원칙**: 필요한 최소한의 권한만 부여
- **심층 방어**: 여러 계층의 보안 메커니즘 적용
- **보안 기본값**: 안전한 기본 설정 사용
- **입력 검증**: 모든 외부 입력 철저히 검증
- **오류 처리**: 보안 정보 노출 방지

### **2. 현재 시스템 보안 상태**
```
✅ 입력 검증: 온도 범위, 센서 인덱스, 측정 주기 검증 완료
✅ 버퍼 오버플로우 방지: 고정 크기 버퍼 및 범위 검사
✅ 메모리 보호: 스택 오버플로우 방지 및 안전한 메모리 사용
✅ 데이터 무결성: EEPROM 데이터 검증 및 복구
⚠️ 물리적 보안: 하드웨어 접근 제어 필요
⚠️ 통신 보안: 시리얼 통신 암호화 미적용
```

## 🛡️ 입력 검증 및 데이터 보호

### **1. 온도 값 검증**
```cpp
// ✅ 이미 구현됨 - 강력한 입력 검증
bool SensorController::isValidTemperature(float temp) {
    // DS18B20 물리적 한계 검증
    if (temp < DS18B20_MIN_TEMP || temp > DS18B20_MAX_TEMP) {
        return false;
    }
    
    // NaN 및 무한대 값 검증
    if (isnan(temp) || isinf(temp)) {
        return false;
    }
    
    return true;
}
```

### **2. 센서 인덱스 검증**
```cpp
// ✅ 이미 구현됨 - 배열 경계 검사
bool isValidSensorIndex(int idx) {
    return (idx >= 0 && idx < SENSOR_MAX_COUNT);
}

void setThresholds(int sensorIdx, float upperTemp, float lowerTemp) {
    // 인덱스 검증
    if (!isValidSensorIndex(sensorIdx)) {
        Serial.println(F("❌ 오류: 잘못된 센서 인덱스"));
        return;
    }
    
    // 추가 검증 로직...
}
```

### **3. 문자열 입력 검증**
```cpp
// ✅ 이미 구현됨 - 안전한 문자열 파싱
unsigned long parseIntervalInput(const String& input) {
    // 입력 길이 제한
    if (input.length() > 20) {
        return 0;  // 너무 긴 입력 거부
    }
    
    // 허용된 문자만 검증
    for (int i = 0; i < input.length(); i++) {
        char c = input.charAt(i);
        if (!isDigit(c) && c != 'd' && c != 'h' && c != 'm' && c != 's') {
            return 0;  // 유효하지 않은 문자 거부
        }
    }
    
    // 추가 파싱 로직...
}
```

## 🔐 메모리 보안

### **1. 버퍼 오버플로우 방지**
```cpp
// ✅ 안전한 문자열 처리
void formatSensorStatus(int sensorId, float temp, char* buffer, size_t bufferSize) {
    // snprintf 사용으로 버퍼 오버플로우 방지
    snprintf(buffer, bufferSize, "센서 %d: %.1f°C", sensorId, temp);
    
    // 버퍼 끝에 null terminator 보장
    buffer[bufferSize - 1] = '\0';
}

// ❌ 위험한 방법 (사용 금지)
void unsafeFormatting(int sensorId, float temp, char* buffer) {
    sprintf(buffer, "센서 %d: %.1f°C", sensorId, temp);  // 버퍼 크기 무시
}
```

### **2. 스택 오버플로우 방지**
```cpp
// ✅ 안전한 지역 변수 사용
void processData() {
    char smallBuffer[64];  // 적절한 크기
    // 처리 로직
}

// ❌ 위험한 방법
void dangerousFunction() {
    char hugeBuffer[2048];  // 스택 오버플로우 위험
    // 처리 로직
}
```

### **3. 동적 메모리 사용 최소화**
```cpp
// ✅ 정적 할당 사용
static char globalBuffer[256];

void safeFunction() {
    // 전역 버퍼 재사용
    memset(globalBuffer, 0, sizeof(globalBuffer));
    // 처리 로직
}

// ❌ 위험한 방법 (Arduino에서 권장하지 않음)
void riskyFunction() {
    char* dynamicBuffer = (char*)malloc(256);  // 메모리 누수 위험
    // 처리 로직
    free(dynamicBuffer);  // 실수로 누락 가능
}
```

## 🔍 데이터 무결성 보장

### **1. EEPROM 데이터 검증**
```cpp
// ✅ 이미 구현됨 - 강력한 데이터 검증
void loadSensorThresholds(int sensorIdx) {
    float upper, lower;
    EEPROM.get(addr, upper);
    EEPROM.get(addr + 4, lower);
    
    // 데이터 무결성 검증
    bool needsReset = false;
    
    // NaN 검사
    if (isnan(upper) || isnan(lower)) {
        needsReset = true;
    }
    
    // 범위 검사
    if (!isValidTemperature(upper) || !isValidTemperature(lower)) {
        needsReset = true;
    }
    
    // 논리 검사
    if (upper <= lower) {
        needsReset = true;
    }
    
    // 손상된 데이터 복구
    if (needsReset) {
        upper = DEFAULT_UPPER_THRESHOLD;
        lower = DEFAULT_LOWER_THRESHOLD;
        saveSensorThresholds(sensorIdx, false);
    }
}
```

### **2. 체크섬 기반 검증 (고급)**
```cpp
// 추가 보안이 필요한 경우 구현 가능
uint16_t calculateChecksum(const uint8_t* data, size_t length) {
    uint16_t checksum = 0;
    for (size_t i = 0; i < length; i++) {
        checksum += data[i];
    }
    return checksum;
}

void saveDataWithChecksum(int addr, const void* data, size_t size) {
    // 데이터 저장
    EEPROM.put(addr, data);
    
    // 체크섬 계산 및 저장
    uint16_t checksum = calculateChecksum((const uint8_t*)data, size);
    EEPROM.put(addr + size, checksum);
}

bool loadDataWithChecksum(int addr, void* data, size_t size) {
    // 데이터 로드
    EEPROM.get(addr, data);
    
    // 체크섬 검증
    uint16_t storedChecksum, calculatedChecksum;
    EEPROM.get(addr + size, storedChecksum);
    calculatedChecksum = calculateChecksum((const uint8_t*)data, size);
    
    return (storedChecksum == calculatedChecksum);
}
```

## 🚫 정보 노출 방지

### **1. 디버그 정보 제한**
```cpp
// ✅ 조건부 디버그 출력
#ifdef DEBUG_MODE
    #define DEBUG_PRINT(x) Serial.print(x)
    #define DEBUG_PRINTLN(x) Serial.println(x)
#else
    #define DEBUG_PRINT(x)
    #define DEBUG_PRINTLN(x)
#endif

void sensitiveFunction() {
    DEBUG_PRINTLN(F("[DEBUG] 민감한 작업 시작"));  // 릴리스에서 제거
    
    // 실제 로직
    
    DEBUG_PRINTLN(F("[DEBUG] 작업 완료"));
}
```

### **2. 오류 메시지 표준화**
```cpp
// ✅ 일반적인 오류 메시지
const char* getErrorMessage(ErrorCode code) {
    switch (code) {
        case ERROR_INVALID_INPUT:
            return "유효하지 않은 입력입니다";
        case ERROR_OUT_OF_RANGE:
            return "범위를 벗어났습니다";
        case ERROR_SYSTEM_ERROR:
            return "시스템 오류가 발생했습니다";
        default:
            return "알 수 없는 오류입니다";
    }
}

// ❌ 위험한 방법 (내부 정보 노출)
void badErrorHandling() {
    Serial.print(F("EEPROM 주소 "));
    Serial.print(EEPROM_BASE_ADDR);
    Serial.println(F("에서 읽기 실패"));  // 내부 구조 노출
}
```

## 🔧 안전한 개발 관행

### **1. 상수 사용**
```cpp
// ✅ 매직 넘버 대신 상수 사용
constexpr int MAX_RETRY_COUNT = 3;
constexpr int TIMEOUT_MS = 5000;
constexpr float SAFETY_MARGIN = 0.1f;

void safeOperation() {
    int retryCount = 0;
    while (retryCount < MAX_RETRY_COUNT) {
        if (performOperation()) {
            break;
        }
        retryCount++;
        delay(100);
    }
}
```

### **2. 범위 기반 루프**
```cpp
// ✅ 안전한 배열 순회
void processSensorData() {
    for (int i = 0; i < SENSOR_MAX_COUNT; i++) {
        if (isValidSensorIndex(i)) {  // 추가 안전 검사
            processOneSensor(i);
        }
    }
}
```

### **3. 예외 상황 처리**
```cpp
// ✅ 모든 예외 상황 고려
float readSensorTemperature(int sensorIdx) {
    // 입력 검증
    if (!isValidSensorIndex(sensorIdx)) {
        return DEVICE_DISCONNECTED_C;
    }
    
    // 센서 연결 확인
    if (!isSensorConnected(sensorIdx)) {
        return DEVICE_DISCONNECTED_C;
    }
    
    // 온도 읽기
    float temp = sensors.getTempCByIndex(sensorIdx);
    
    // 결과 검증
    if (!isValidTemperature(temp)) {
        return DEVICE_DISCONNECTED_C;
    }
    
    return temp;
}
```

## 🌐 통신 보안 (향후 확장)

### **1. 시리얼 통신 보안**
```cpp
// 현재는 로컬 시리얼 통신만 사용하므로 보안 위험 낮음
// WiFi 기능 추가 시 고려사항:

// ✅ 입력 길이 제한
bool processSerialCommand(const String& command) {
    if (command.length() > MAX_COMMAND_LENGTH) {
        Serial.println(F("명령어가 너무 깁니다"));
        return false;
    }
    
    // 명령어 처리
    return true;
}

// ✅ 명령어 화이트리스트
bool isValidCommand(const String& command) {
    const char* validCommands[] = {
        "menu", "m", "reset", "c", "y", "n"
    };
    
    for (size_t i = 0; i < sizeof(validCommands) / sizeof(validCommands[0]); i++) {
        if (command.equals(validCommands[i])) {
            return true;
        }
    }
    
    return false;
}
```

### **2. 물리적 보안 권장사항**
```
✅ 하드웨어 보안:
   - 케이스에 설치하여 물리적 접근 제한
   - 중요한 연결부 납땜으로 고정
   - 전원 및 통신 케이블 보호

✅ 설치 보안:
   - 접근이 제한된 장소에 설치
   - 센서 케이블 손상 방지
   - 환경적 요인(습도, 온도) 고려

✅ 유지보수 보안:
   - 정기적인 하드웨어 점검
   - 펌웨어 업데이트 계획
   - 백업 및 복구 절차 수립
```

## 📋 보안 체크리스트

### **개발 단계**
- [x] 모든 입력 검증 구현
- [x] 버퍼 오버플로우 방지
- [x] 메모리 안전성 확보
- [x] 오류 처리 표준화
- [x] 디버그 정보 제한
- [x] 상수 사용으로 매직 넘버 제거

### **배포 단계**
- [ ] 디버그 모드 비활성화
- [ ] 불필요한 시리얼 출력 제거
- [ ] 코드 리뷰 완료
- [ ] 보안 테스트 수행
- [ ] 문서화 완료

### **운영 단계**
- [ ] 물리적 보안 확보
- [ ] 정기적 점검 계획
- [ ] 업데이트 절차 수립
- [ ] 백업 및 복구 계획
- [ ] 사고 대응 절차

## 🚨 보안 사고 대응

### **1. 데이터 손상 감지 시**
```cpp
void handleDataCorruption() {
    Serial.println(F("⚠️ 데이터 손상 감지"));
    
    // 1. 안전한 기본값으로 복구
    resetAllThresholds();
    setMeasurementInterval(DEFAULT_MEASUREMENT_INTERVAL);
    
    // 2. 시스템 상태 점검
    performSystemCheck();
    
    // 3. 사용자에게 알림
    Serial.println(F("시스템이 안전 모드로 복구되었습니다"));
    Serial.println(F("설정을 다시 확인해주세요"));
}
```

### **2. 비정상 입력 감지 시**
```cpp
void handleSuspiciousInput(const String& input) {
    static int suspiciousCount = 0;
    suspiciousCount++;
    
    Serial.println(F("⚠️ 비정상 입력 감지"));
    
    // 연속된 비정상 입력 시 보호 모드 진입
    if (suspiciousCount > 5) {
        Serial.println(F("보호 모드 진입 - 시스템 재시작 필요"));
        // 필요시 시스템 재시작 또는 기능 제한
    }
}
```

---

**작성일**: 2025-08-03  
**버전**: v1.0  
**보안 수준**: 임베디드 시스템 기본 보안 적용