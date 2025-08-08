# 테스트 전략 가이드

## 🧪 테스트 개요

### **테스트 피라미드**
```
        /\
       /  \
      / E2E \     ← 소수의 종단간 테스트
     /______\
    /        \
   / Integration \  ← 중간 수준의 통합 테스트
  /______________\
 /                \
/ Unit Tests       \ ← 다수의 단위 테스트
/____________________\
```

### **현재 테스트 상태**
```
✅ 수동 테스트: 하드웨어 연결 및 기능 검증 완료
⚠️ 단위 테스트: 미구현 (권장사항)
⚠️ 통합 테스트: 미구현 (권장사항)
⚠️ 자동화 테스트: 미구현 (선택사항)
```

## 🔬 단위 테스트 (Unit Tests)

### **1. 테스트 환경 설정**

#### PlatformIO 테스트 설정
```ini
; platformio.ini에 추가
[env:test]
platform = native
framework = 
lib_deps = 
    throwtheswitch/Unity@^2.5.2
build_flags = 
    -D UNIT_TEST
    -D NATIVE_TEST
test_framework = unity
```

#### 테스트 디렉토리 구조
```
test/
├── test_sensor_controller/
│   └── test_sensor_controller.cpp
├── test_menu_controller/
│   └── test_menu_controller.cpp
├── test_eeprom_manager/
│   └── test_eeprom_manager.cpp
└── test_utils/
    ├── MockSensor.h
    ├── MockEEPROM.h
    └── TestHelpers.h
```

### **2. SensorController 단위 테스트**

#### 임계값 검증 테스트
```cpp
// test/test_sensor_controller/test_sensor_controller.cpp
#include <unity.h>
#include "../../src/application/SensorController.h"

void setUp(void) {
    // 각 테스트 전 초기화
}

void tearDown(void) {
    // 각 테스트 후 정리
}

void test_temperature_validation_valid_range(void) {
    SensorController controller;
    
    // 유효한 온도 범위 테스트
    TEST_ASSERT_TRUE(controller.isValidTemperature(25.0f));
    TEST_ASSERT_TRUE(controller.isValidTemperature(-55.0f));
    TEST_ASSERT_TRUE(controller.isValidTemperature(125.0f));
    TEST_ASSERT_TRUE(controller.isValidTemperature(0.0f));
}

void test_temperature_validation_invalid_range(void) {
    SensorController controller;
    
    // 무효한 온도 범위 테스트
    TEST_ASSERT_FALSE(controller.isValidTemperature(-56.0f));
    TEST_ASSERT_FALSE(controller.isValidTemperature(126.0f));
    TEST_ASSERT_FALSE(controller.isValidTemperature(NAN));
    TEST_ASSERT_FALSE(controller.isValidTemperature(INFINITY));
}

void test_threshold_setting_valid_values(void) {
    SensorController controller;
    
    // 유효한 임계값 설정
    controller.setThresholds(0, 30.0f, 20.0f);
    
    TEST_ASSERT_EQUAL_FLOAT(30.0f, controller.getUpperThreshold(0));
    TEST_ASSERT_EQUAL_FLOAT(20.0f, controller.getLowerThreshold(0));
}

void test_threshold_setting_invalid_logic(void) {
    SensorController controller;
    
    // 논리적으로 잘못된 임계값 (상한 <= 하한)
    float originalUpper = controller.getUpperThreshold(0);
    float originalLower = controller.getLowerThreshold(0);
    
    controller.setThresholds(0, 20.0f, 30.0f);  // 잘못된 설정
    
    // 값이 변경되지 않아야 함
    TEST_ASSERT_EQUAL_FLOAT(originalUpper, controller.getUpperThreshold(0));
    TEST_ASSERT_EQUAL_FLOAT(originalLower, controller.getLowerThreshold(0));
}

void test_sensor_status_evaluation(void) {
    SensorController controller;
    controller.setThresholds(0, 30.0f, 20.0f);
    
    // 정상 범위
    TEST_ASSERT_EQUAL_STRING("정상", controller.getSensorStatus(0, 25.0f));
    
    // 상한 초과
    TEST_ASSERT_EQUAL_STRING("경고", controller.getSensorStatus(0, 35.0f));
    
    // 하한 미만
    TEST_ASSERT_EQUAL_STRING("경고", controller.getSensorStatus(0, 15.0f));
    
    // 연결 오류
    TEST_ASSERT_EQUAL_STRING("오류", controller.getSensorStatus(0, DEVICE_DISCONNECTED_C));
}

int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_temperature_validation_valid_range);
    RUN_TEST(test_temperature_validation_invalid_range);
    RUN_TEST(test_threshold_setting_valid_values);
    RUN_TEST(test_threshold_setting_invalid_logic);
    RUN_TEST(test_sensor_status_evaluation);
    
    return UNITY_END();
}
```

### **3. 측정 주기 파싱 테스트**

```cpp
// test/test_menu_controller/test_interval_parsing.cpp
#include <unity.h>
#include "../../src/application/MenuController.h"

void test_simple_interval_parsing(void) {
    MenuController controller;
    
    // 단순 초 단위
    TEST_ASSERT_EQUAL_UINT32(30000, controller.parseIntervalInput("30"));
    TEST_ASSERT_EQUAL_UINT32(30000, controller.parseIntervalInput("30s"));
    
    // 분 단위
    TEST_ASSERT_EQUAL_UINT32(300000, controller.parseIntervalInput("5m"));
    TEST_ASSERT_EQUAL_UINT32(300000, controller.parseIntervalInput("5M"));
    
    // 시간 단위
    TEST_ASSERT_EQUAL_UINT32(7200000, controller.parseIntervalInput("2h"));
    TEST_ASSERT_EQUAL_UINT32(7200000, controller.parseIntervalInput("2H"));
    
    // 일 단위
    TEST_ASSERT_EQUAL_UINT32(86400000, controller.parseIntervalInput("1d"));
    TEST_ASSERT_EQUAL_UINT32(86400000, controller.parseIntervalInput("1D"));
}

void test_complex_interval_parsing(void) {
    MenuController controller;
    
    // 복합 단위
    TEST_ASSERT_EQUAL_UINT32(93600000, controller.parseIntervalInput("1d2h"));      // 1일 2시간
    TEST_ASSERT_EQUAL_UINT32(9000000, controller.parseIntervalInput("2h30m"));      // 2시간 30분
    TEST_ASSERT_EQUAL_UINT32(5445000, controller.parseIntervalInput("1h30m45s"));  // 1시간 30분 45초
}

void test_invalid_interval_parsing(void) {
    MenuController controller;
    
    // 무효한 입력
    TEST_ASSERT_EQUAL_UINT32(0, controller.parseIntervalInput(""));
    TEST_ASSERT_EQUAL_UINT32(0, controller.parseIntervalInput("abc"));
    TEST_ASSERT_EQUAL_UINT32(0, controller.parseIntervalInput("30x"));
    TEST_ASSERT_EQUAL_UINT32(0, controller.parseIntervalInput("-30"));
    TEST_ASSERT_EQUAL_UINT32(0, controller.parseIntervalInput("999999d"));  // 오버플로우
}

void test_edge_cases(void) {
    MenuController controller;
    
    // 경계값 테스트
    TEST_ASSERT_EQUAL_UINT32(10000, controller.parseIntervalInput("10"));     // 최소값
    TEST_ASSERT_EQUAL_UINT32(0, controller.parseIntervalInput("9"));          // 최소값 미만
    
    // 대소문자 혼합
    TEST_ASSERT_EQUAL_UINT32(93645000, controller.parseIntervalInput("1D2H30M45S"));
}
```

### **4. Mock 객체 활용**

#### MockEEPROM 구현
```cpp
// test/test_utils/MockEEPROM.h
#ifndef MOCK_EEPROM_H
#define MOCK_EEPROM_H

#include <map>
#include <cstdint>

class MockEEPROM {
private:
    std::map<int, uint8_t> memory;
    int writeCount = 0;
    
public:
    template<typename T>
    void put(int address, const T& value) {
        writeCount++;
        const uint8_t* bytes = reinterpret_cast<const uint8_t*>(&value);
        for (size_t i = 0; i < sizeof(T); i++) {
            memory[address + i] = bytes[i];
        }
    }
    
    template<typename T>
    void get(int address, T& value) {
        uint8_t* bytes = reinterpret_cast<uint8_t*>(&value);
        for (size_t i = 0; i < sizeof(T); i++) {
            auto it = memory.find(address + i);
            bytes[i] = (it != memory.end()) ? it->second : 0xFF;
        }
    }
    
    int getWriteCount() const { return writeCount; }
    void resetWriteCount() { writeCount = 0; }
    void clear() { memory.clear(); writeCount = 0; }
};

extern MockEEPROM mockEEPROM;

#endif
```

## 🔗 통합 테스트 (Integration Tests)

### **1. 센서-컨트롤러 통합 테스트**

```cpp
// test/integration/test_sensor_integration.cpp
#include <unity.h>
#include "../../src/application/SensorController.h"
#include "../test_utils/MockSensor.h"

void test_sensor_controller_integration(void) {
    SensorController controller;
    MockSensor mockSensor;
    
    // Mock 센서 설정
    mockSensor.setTemperature(0, 25.5f);
    mockSensor.setTemperature(1, 35.2f);
    mockSensor.setConnected(0, true);
    mockSensor.setConnected(1, true);
    
    // 임계값 설정
    controller.setThresholds(0, 30.0f, 20.0f);
    controller.setThresholds(1, 30.0f, 20.0f);
    
    // 상태 업데이트
    controller.updateSensorRows();
    
    // 결과 검증
    TEST_ASSERT_EQUAL_STRING("정상", controller.getSensorStatus(0, 25.5f));
    TEST_ASSERT_EQUAL_STRING("경고", controller.getSensorStatus(1, 35.2f));
}
```

### **2. 메뉴-센서 통합 테스트**

```cpp
// test/integration/test_menu_sensor_integration.cpp
void test_threshold_setting_workflow(void) {
    SensorController sensorController;
    MenuController menuController;
    
    // 시뮬레이션된 사용자 입력 시퀀스
    simulateUserInput("menu");
    simulateUserInput("2");  // 임계값 메뉴
    simulateUserInput("1");  // 개별 센서 설정
    simulateUserInput("1");  // 센서 1 선택
    simulateUserInput("35"); // 상한값
    simulateUserInput("15"); // 하한값
    
    // 결과 검증
    TEST_ASSERT_EQUAL_FLOAT(35.0f, sensorController.getUpperThreshold(0));
    TEST_ASSERT_EQUAL_FLOAT(15.0f, sensorController.getLowerThreshold(0));
}
```

## 🎯 하드웨어 테스트

### **1. 센서 연결 테스트**

```cpp
// test/hardware/test_ds18b20_connection.cpp
void test_sensor_detection(void) {
    // 실제 하드웨어 필요
    sensors.begin();
    
    int deviceCount = sensors.getDeviceCount();
    TEST_ASSERT_GREATER_THAN(0, deviceCount);
    TEST_ASSERT_LESS_OR_EQUAL(8, deviceCount);
    
    // 각 센서의 주소 유효성 검증
    for (int i = 0; i < deviceCount; i++) {
        DeviceAddress addr;
        TEST_ASSERT_TRUE(sensors.getAddress(addr, i));
        
        // 주소가 모두 0이 아닌지 확인
        bool hasNonZero = false;
        for (int j = 0; j < 8; j++) {
            if (addr[j] != 0) {
                hasNonZero = true;
                break;
            }
        }
        TEST_ASSERT_TRUE(hasNonZero);
    }
}

void test_temperature_reading(void) {
    sensors.begin();
    sensors.requestTemperatures();
    
    int deviceCount = sensors.getDeviceCount();
    for (int i = 0; i < deviceCount; i++) {
        float temp = sensors.getTempCByIndex(i);
        
        // 유효한 온도 범위 확인
        TEST_ASSERT_NOT_EQUAL(DEVICE_DISCONNECTED_C, temp);
        TEST_ASSERT_GREATER_OR_EQUAL(-55.0f, temp);
        TEST_ASSERT_LESS_OR_EQUAL(125.0f, temp);
    }
}
```

### **2. EEPROM 테스트**

```cpp
// test/hardware/test_eeprom.cpp
void test_eeprom_write_read_cycle(void) {
    const int testAddr = 100;  // 안전한 테스트 주소
    const float testValue = 42.5f;
    
    // 쓰기
    EEPROM.put(testAddr, testValue);
    
    // 읽기
    float readValue;
    EEPROM.get(testAddr, readValue);
    
    // 검증
    TEST_ASSERT_EQUAL_FLOAT(testValue, readValue);
    
    // 정리
    EEPROM.put(testAddr, 0.0f);
}

void test_eeprom_endurance(void) {
    const int testAddr = 200;
    const int testCycles = 100;  // 실제로는 더 적게 테스트
    
    for (int i = 0; i < testCycles; i++) {
        float testValue = (float)i;
        
        EEPROM.put(testAddr, testValue);
        
        float readValue;
        EEPROM.get(testAddr, readValue);
        
        TEST_ASSERT_EQUAL_FLOAT(testValue, readValue);
    }
    
    // 정리
    EEPROM.put(testAddr, 0.0f);
}
```

## 🚀 성능 테스트

### **1. 메모리 사용량 테스트**

```cpp
// test/performance/test_memory_usage.cpp
void test_memory_usage_limits(void) {
    int initialFreeMemory = freeMemory();
    
    // 메모리 집약적 작업 수행
    SensorController controller;
    controller.initializeThresholds();
    
    int afterInitMemory = freeMemory();
    int memoryUsed = initialFreeMemory - afterInitMemory;
    
    // 메모리 사용량이 예상 범위 내인지 확인
    TEST_ASSERT_LESS_THAN(1000, memoryUsed);  // 1KB 미만 사용
    
    Serial.print("메모리 사용량: ");
    Serial.print(memoryUsed);
    Serial.println(" bytes");
}
```

### **2. 응답 시간 테스트**

```cpp
// test/performance/test_response_time.cpp
void test_sensor_read_performance(void) {
    SensorController controller;
    
    unsigned long startTime = micros();
    controller.updateSensorRows();
    unsigned long endTime = micros();
    
    unsigned long duration = endTime - startTime;
    
    // 1초 이내에 완료되어야 함
    TEST_ASSERT_LESS_THAN(1000000, duration);
    
    Serial.print("센서 읽기 시간: ");
    Serial.print(duration);
    Serial.println(" μs");
}
```

## 📋 테스트 실행 가이드

### **1. 테스트 실행 명령어**

```bash
# 모든 테스트 실행
pio test

# 특정 환경 테스트
pio test -e test

# 특정 테스트만 실행
pio test -f test_sensor_controller

# 하드웨어 테스트 (실제 하드웨어 필요)
pio test -e uno_r4_wifi -f test_hardware
```

### **2. 테스트 결과 해석**

```
테스트 결과 예시:
===================
test/test_sensor_controller/test_sensor_controller.cpp:45:test_temperature_validation_valid_range:PASS
test/test_sensor_controller/test_sensor_controller.cpp:52:test_temperature_validation_invalid_range:PASS
test/test_sensor_controller/test_sensor_controller.cpp:60:test_threshold_setting_valid_values:PASS
test/test_sensor_controller/test_sensor_controller.cpp:68:test_threshold_setting_invalid_logic:PASS
test/test_sensor_controller/test_sensor_controller.cpp:78:test_sensor_status_evaluation:PASS

-----------------------
5 Tests 0 Failures 0 Ignored 
OK
```

### **3. 지속적 통합 (CI) 설정**

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'
    
    - name: Install PlatformIO
      run: pip install platformio
    
    - name: Run tests
      run: pio test -e test
```

## 📊 테스트 커버리지

### **목표 커버리지**
- 단위 테스트: 80% 이상
- 통합 테스트: 주요 워크플로우 100%
- 하드웨어 테스트: 핵심 기능 100%

### **현재 상태**
```
구성 요소                테스트 상태    우선순위
--------------------------------------------
SensorController        미구현         높음
MenuController          미구현         중간
EEPROM 관리            미구현         높음
입력 파싱              미구현         중간
하드웨어 연결          수동 테스트     높음
```

---

**작성일**: 2025-08-03  
**버전**: v1.0  
**테스트 프레임워크**: Unity  
**상태**: 테스트 전략 수립 완료, 구현 권장