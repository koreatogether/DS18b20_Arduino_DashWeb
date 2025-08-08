# Arduino Assert 구현 및 활용 가이드

## 개요

Arduino 환경에서는 표준 C++ assert가 제한적으로 지원되므로, 커스텀 assert 시스템을 구현하여 개발 단계에서의 디버깅과 테스트를 효과적으로 수행할 수 있습니다.

## Assert의 필요성

### Arduino 환경의 제약사항
- 표준 `<cassert>` 헤더의 제한적 지원
- 디버깅 도구의 부족
- 런타임 에러 감지의 어려움
- 메모리 제약으로 인한 신중한 에러 처리 필요

### Assert의 장점
- **조기 버그 발견**: 잘못된 파라미터나 상태를 즉시 감지
- **개발 효율성**: 문제 발생 지점을 정확히 파악
- **코드 품질**: 전제 조건과 후제 조건 명시
- **성능**: 릴리즈 모드에서 완전 제거 가능

## Arduino Assert 시스템 구현

### 1. Assert 헤더 파일 (ArduinoAssert.h)

```cpp
#ifndef ARDUINO_ASSERT_H
#define ARDUINO_ASSERT_H

#include <Arduino.h>

// 디버그 모드 설정
#ifdef DEBUG
  #define ASSERT_ENABLED 1
#else
  #define ASSERT_ENABLED 0
#endif

// Assert 실패 시 호출되는 함수
void assertFailed(const char* file, int line, const char* condition);

// 기본 Assert 매크로
#if ASSERT_ENABLED
  #define ASSERT(condition) \
    do { \
      if (!(condition)) { \
        assertFailed(__FILE__, __LINE__, #condition); \
      } \
    } while(0)
  
  // 메시지 포함 Assert
  #define ASSERT_MSG(condition, message) \
    do { \
      if (!(condition)) { \
        Serial.print("ASSERT FAILED: "); \
        Serial.print(message); \
        Serial.print(" at "); \
        Serial.print(__FILE__); \
        Serial.print(":"); \
        Serial.println(__LINE__); \
        while(1); \
      } \
    } while(0)
    
  // 범위 검증 Assert
  #define ASSERT_RANGE(value, min, max) \
    ASSERT((value) >= (min) && (value) <= (max))
    
  // Null 포인터 검증 Assert
  #define ASSERT_NOT_NULL(ptr) \
    ASSERT((ptr) != nullptr)
    
#else
  // 릴리즈 모드에서는 모든 assert 비활성화
  #define ASSERT(condition) ((void)0)
  #define ASSERT_MSG(condition, message) ((void)0)
  #define ASSERT_RANGE(value, min, max) ((void)0)
  #define ASSERT_NOT_NULL(ptr) ((void)0)
#endif

// 정적 assert (컴파일 타임 검증)
#define STATIC_ASSERT(condition, message) \
  static_assert(condition, message)

#endif
```

### 2. Assert 구현 파일 (ArduinoAssert.cpp)

```cpp
#include "ArduinoAssert.h"

void assertFailed(const char* file, int line, const char* condition) {
  // 시리얼 출력으로 상세 정보 표시
  Serial.println();
  Serial.println("=== ASSERTION FAILED ===");
  Serial.print("File: ");
  Serial.println(file);
  Serial.print("Line: ");
  Serial.println(line);
  Serial.print("Condition: ");
  Serial.println(condition);
  Serial.println("========================");
  Serial.flush();
  
  // LED 깜빡임으로 시각적 표시
  pinMode(LED_BUILTIN, OUTPUT);
  while(1) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(200);
    digitalWrite(LED_BUILTIN, LOW);
    delay(200);
  }
}
```

## 프로젝트 설정

### PlatformIO 설정 (platformio.ini)

```ini
[env:nanoatmega328]
platform = atmelavr
board = nanoatmega328
framework = arduino

; 디버그 모드 빌드 플래그
build_flags = 
    -DARDUINO_NANO
    -DSERIAL_BUFFER_SIZE=128
    -DDEBUG  ; Assert 활성화

; 릴리즈 모드용 환경 (Assert 비활성화)
[env:nanoatmega328_release]
platform = atmelavr
board = nanoatmega328
framework = arduino
build_flags = 
    -DARDUINO_NANO
    -DSERIAL_BUFFER_SIZE=128
    ; DEBUG 플래그 제거로 Assert 비활성화
```

## 실제 적용 사례

### 1. SensorManager에서의 Assert 활용

```cpp
#include "ArduinoAssert.h"

bool SensorManager::isValidSensorIndex(int index) {
  // 개발 시 범위 검증
  ASSERT_RANGE(index, 0, MAX_SENSORS - 1);
  return (index >= 0 && index < sensorCount);
}

bool SensorManager::setSensorId(int index, int newId) {
  // 입력 검증 assert
  ASSERT_MSG(isValidSensorIndex(index), "Invalid sensor index");
  ASSERT_MSG(isValidSensorId(newId), "Invalid sensor ID");
  
  // 실제 비즈니스 로직
  if (!isValidSensorIndex(index)) {
    return false;
  }
  // ... 나머지 구현
}

bool SensorManager::setThresholds(int index, float upper, float lower) {
  // 다중 조건 검증
  ASSERT_MSG(isValidSensorIndex(index), "Invalid sensor index");
  ASSERT_MSG(upper > lower, "Upper limit must be greater than lower limit");
  ASSERT_RANGE(upper, -55.0, 125.0); // DS18B20 범위
  ASSERT_RANGE(lower, -55.0, 125.0);
  
  // 실제 구현...
}
```

### 2. 정적 Assert 활용

```cpp
// 컴파일 타임 검증
STATIC_ASSERT(MAX_SENSORS <= 8, "Too many sensors defined");
STATIC_ASSERT(sizeof(SensorInfo) <= 64, "SensorInfo struct too large");
STATIC_ASSERT(DEFAULT_INTERVAL >= 100, "Interval too short");
```

## 단위 테스트 시스템

### 1. 테스트 유틸리티 (TestUtils.h)

```cpp
#ifndef TEST_UTILS_H
#define TEST_UTILS_H

#include "ArduinoAssert.h"

class TestRunner {
private:
  int totalTests, passedTests, failedTests;
  
public:
  TestRunner() : totalTests(0), passedTests(0), failedTests(0) {}
  
  void runTest(const char* testName, void (*testFunc)()) {
    Serial.print("Running test: ");
    Serial.println(testName);
    
    totalTests++;
    
    try {
      testFunc();
      passedTests++;
      Serial.println("  ✓ PASSED");
    } catch (...) {
      failedTests++;
      Serial.println("  ✗ FAILED");
    }
  }
  
  void printResults() {
    Serial.println("\n=== TEST RESULTS ===");
    Serial.print("Total: "); Serial.println(totalTests);
    Serial.print("Passed: "); Serial.println(passedTests);
    Serial.print("Failed: "); Serial.println(failedTests);
    Serial.println("===================");
  }
};

// 테스트용 Assert 매크로
#define TEST_ASSERT(condition) \
  do { \
    if (!(condition)) { \
      Serial.print("TEST FAILED: "); \
      Serial.print(#condition); \
      Serial.print(" at line "); \
      Serial.println(__LINE__); \
      throw "Test failed"; \
    } \
  } while(0)

#define TEST_ASSERT_EQUAL(expected, actual) \
  TEST_ASSERT((expected) == (actual))

#define TEST_ASSERT_FLOAT_EQUAL(expected, actual, tolerance) \
  TEST_ASSERT(abs((expected) - (actual)) < (tolerance))

#endif
```

### 2. 실제 테스트 구현 (SensorTests.cpp)

```cpp
#include "TestUtils.h"
#include "SensorManager.h"

void testTemperatureValidation() {
  // 유효한 온도 테스트
  TEST_ASSERT(sensorManager.isValidTemperature(25.0));
  TEST_ASSERT(sensorManager.isValidTemperature(-10.0));
  
  // 감시값 테스트
  TEST_ASSERT(!sensorManager.isValidTemperature(INVALID_TEMPERATURE));
  
  // 범위 밖 값 테스트
  TEST_ASSERT(!sensorManager.isValidTemperature(-60.0));
  TEST_ASSERT(!sensorManager.isValidTemperature(130.0));
}

void testSensorIdValidation() {
  TEST_ASSERT(sensorManager.isValidSensorId(1));
  TEST_ASSERT(sensorManager.isValidSensorId(8));
  TEST_ASSERT(!sensorManager.isValidSensorId(0));
  TEST_ASSERT(!sensorManager.isValidSensorId(9));
}

void runAllSensorTests() {
  TestRunner testRunner;
  
  testRunner.runTest("Temperature Validation", testTemperatureValidation);
  testRunner.runTest("Sensor ID Validation", testSensorIdValidation);
  
  testRunner.printResults();
}
```

### 3. 메인 스케치에서 테스트 실행

```cpp
void setup() {
  Serial.begin(9600);
  while (!Serial);
  
  // 시스템 초기화
  serialComm.begin();
  sensorManager.begin();
  commandProcessor.begin(&sensorManager, &serialComm);
  
#ifdef DEBUG
  // 디버그 모드에서만 단위 테스트 실행
  Serial.println("Running unit tests...");
  runAllSensorTests();
  Serial.println("Tests completed. Starting normal operation...");
#endif
  
  // 정상 동작 시작
  sensorManager.scanSensors();
}
```

## Assert 매크로 종류별 활용

### 1. 기본 ASSERT
```cpp
// 기본 조건 검증
ASSERT(sensorCount > 0);
ASSERT(temperature != INVALID_TEMPERATURE);
```

### 2. ASSERT_MSG (메시지 포함)
```cpp
// 상세한 에러 메시지 제공
ASSERT_MSG(index < MAX_SENSORS, "Sensor index out of bounds");
ASSERT_MSG(interval >= 100, "Measurement interval too short");
```

### 3. ASSERT_RANGE (범위 검증)
```cpp
// 값의 범위 검증
ASSERT_RANGE(temperature, -55.0, 125.0);
ASSERT_RANGE(sensorId, 1, 8);
ASSERT_RANGE(index, 0, MAX_SENSORS - 1);
```

### 4. ASSERT_NOT_NULL (포인터 검증)
```cpp
// 포인터 유효성 검증
ASSERT_NOT_NULL(sensorData);
ASSERT_NOT_NULL(configPtr);
```

### 5. STATIC_ASSERT (컴파일 타임 검증)
```cpp
// 컴파일 시점 검증
STATIC_ASSERT(MAX_SENSORS <= 8, "Hardware limitation");
STATIC_ASSERT(sizeof(float) == 4, "Float size assumption");
```

## 성능 및 메모리 고려사항

### 1. 릴리즈 모드 최적화

```cpp
// 디버그 모드
#ifdef DEBUG
  ASSERT(condition);  // 실제 검증 코드 생성
#else
  ASSERT(condition);  // ((void)0)으로 완전 제거
#endif
```

### 2. 메모리 사용량

| 구성 요소 | 디버그 모드 | 릴리즈 모드 |
|-----------|-------------|-------------|
| Assert 매크로 | 코드 생성 | 완전 제거 |
| 파일명/라인 | 포함 | 제거 |
| 에러 메시지 | 포함 | 제거 |
| 전체 오버헤드 | ~1-2KB | 0 바이트 |

### 3. 실행 시간 영향

```cpp
// 디버그 모드: 조건 검사 + 분기
if (!(condition)) {
    assertFailed(__FILE__, __LINE__, #condition);
}

// 릴리즈 모드: 완전 제거
// (컴파일러가 코드를 생성하지 않음)
```

## 디버깅 및 문제 해결

### 1. Assert 실패 시 정보 수집

```
=== ASSERTION FAILED ===
File: SensorManager.cpp
Line: 145
Condition: index >= 0 && index < MAX_SENSORS
========================
```

### 2. 시각적 피드백

- **LED 깜빡임**: Assert 실패 시 내장 LED가 200ms 간격으로 깜빡임
- **시리얼 출력**: 상세한 실패 정보를 시리얼 모니터에 출력
- **시스템 정지**: 무한 루프로 시스템 정지하여 문제 상황 유지

### 3. 일반적인 Assert 패턴

```cpp
// 함수 진입 시 전제 조건 검증
void processTemperature(float temp) {
    ASSERT_MSG(isValidTemperature(temp), "Invalid temperature input");
    // ... 함수 구현
}

// 함수 종료 시 후제 조건 검증
float calculateAverage(float* values, int count) {
    ASSERT_NOT_NULL(values);
    ASSERT(count > 0);
    
    // ... 계산 로직
    
    ASSERT(result >= 0); // 후제 조건
    return result;
}

// 상태 불변성 검증
void updateSensorState() {
    ASSERT(sensorCount <= MAX_SENSORS); // 불변성 검증
    // ... 상태 업데이트
    ASSERT(sensorCount <= MAX_SENSORS); // 불변성 유지 확인
}
```

## 베스트 프랙티스

### 1. Assert 사용 원칙

```cpp
// ✅ 좋은 Assert 사용
ASSERT_MSG(index < MAX_SENSORS, "Sensor index out of bounds");
ASSERT_RANGE(temperature, -55.0, 125.0);

// ❌ 나쁜 Assert 사용
ASSERT(someComplexFunction()); // 부작용이 있는 함수 호출
ASSERT(malloc(100) != NULL);   // 메모리 할당 실패는 다른 방식으로 처리
```

### 2. 에러 처리와의 구분

```cpp
// Assert: 프로그래머 실수 (개발 시에만)
ASSERT_RANGE(index, 0, MAX_SENSORS - 1);

// 에러 처리: 런타임 오류 (항상 필요)
if (!sensors.begin()) {
    Serial.println("Sensor initialization failed");
    return false;
}
```

### 3. 성능 고려사항

```cpp
// ✅ 간단한 조건 검사
ASSERT(ptr != nullptr);
ASSERT(count > 0);

// ❌ 복잡한 계산 (릴리즈에서도 영향)
ASSERT(calculateChecksum(data) == expectedChecksum);
```

## 확장 가능한 Assert 시스템

### 1. 로그 레벨별 Assert

```cpp
#define ASSERT_CRITICAL(condition) ASSERT_MSG(condition, "CRITICAL")
#define ASSERT_WARNING(condition) ASSERT_MSG(condition, "WARNING")
#define ASSERT_INFO(condition) ASSERT_MSG(condition, "INFO")
```

### 2. 조건부 Assert

```cpp
#define ASSERT_IF_DEBUG(condition) \
    do { if (debugLevel >= DEBUG_LEVEL_HIGH) ASSERT(condition); } while(0)
```

### 3. 통계 수집

```cpp
class AssertStats {
    static int assertCount;
    static int failureCount;
public:
    static void recordAssertion() { assertCount++; }
    static void recordFailure() { failureCount++; }
    static void printStats() {
        Serial.print("Assertions: "); Serial.println(assertCount);
        Serial.print("Failures: "); Serial.println(failureCount);
    }
};
```

## 결론

Arduino 환경에서 커스텀 Assert 시스템을 구현하면 다음과 같은 이점을 얻을 수 있습니다:

### 주요 장점
1. **개발 효율성**: 버그를 조기에 발견하여 디버깅 시간 단축
2. **코드 품질**: 전제 조건과 후제 조건을 명시하여 코드 의도 명확화
3. **성능**: 릴리즈 모드에서 완전 제거되어 성능 영향 없음
4. **유지보수성**: 문제 발생 지점을 정확히 파악하여 수정 용이

### 구현 핵심
- **조건부 컴파일**: DEBUG 플래그로 개발/릴리즈 모드 구분
- **매크로 활용**: 다양한 검증 패턴을 간편하게 사용
- **시각적 피드백**: LED와 시리얼 출력으로 문제 상황 명확히 표시
- **테스트 통합**: 단위 테스트 시스템과 연계하여 품질 보증

이러한 Assert 시스템을 통해 Arduino 프로젝트의 안정성과 개발 효율성을 크게 향상시킬 수 있습니다.