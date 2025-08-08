# 임베디드 프로젝트 관리 가이드

## 📁 표준 폴더 구조

### **루트 디렉토리 구성**
```
project-name/
├── src/                    # 소스 코드 (필수)
├── include/                # 전역 헤더 파일 (필수)
├── lib/                    # 프로젝트 전용 라이브러리 (필수)
├── test/                   # 테스트 코드 (필수)
├── docs/                   # 문서 (필수)
├── tools/                  # 개발 도구 및 스크립트 (선택)
├── hardware/               # 하드웨어 관련 파일 (선택)
├── examples/               # 예제 코드 (선택)
└── assets/                 # 이미지, 다이어그램 등 (선택)
```

### **src/ 디렉토리 세부 구조 (계층형 아키텍처)**
```
src/
├── main.ino               # Arduino 메인 파일
├── application/           # 애플리케이션 계층
│   ├── controllers/       # 컨트롤러 클래스
│   ├── services/          # 비즈니스 로직
│   └── handlers/          # 이벤트 핸들러
├── domain/                # 도메인 계층
│   ├── entities/          # 도메인 엔티티
│   ├── interfaces/        # 인터페이스 정의
│   └── value_objects/     # 값 객체
└── infrastructure/        # 인프라 계층
    ├── sensors/           # 센서 드라이버
    ├── storage/           # 저장소 구현
    └── communication/     # 통신 모듈
```

### **docs/ 디렉토리 구조**
```
docs/
├── mustRead/              # 필수 읽기 문서
│   ├── 01_PROJECT_OVERVIEW.md
│   ├── 02_GITHUB_GUIDE.md
│   └── 03_MANAGEMENT_GUIDE.md
├── api/                   # API 문서
├── hardware/              # 하드웨어 문서
├── development/           # 개발 가이드
├── deployment/            # 배포 가이드
└── troubleshooting/       # 문제 해결 가이드
```

---

## 📝 파일 명명 규칙

### **1. 소스 코드 파일**
```cpp
// 클래스 파일: PascalCase
SensorController.h
SensorController.cpp
MenuController.h
MenuController.cpp

// 인터페이스: I + PascalCase
ITemperatureSensor.h
IDataStorage.h

// 유틸리티: snake_case 또는 PascalCase
StringUtils.h
MathHelper.h
```

### **2. 문서 파일**
```markdown
// 필수 문서: 번호 + 대문자
01_PROJECT_OVERVIEW.md
02_GITHUB_GUIDE.md
03_MANAGEMENT_GUIDE.md

// 일반 문서: UPPER_CASE
README.md
CHANGELOG.md
LICENSE.md
CONTRIBUTING.md

// 기능별 문서: kebab-case
sensor-calibration.md
menu-system-design.md
eeprom-management.md
```

### **3. 설정 파일**
```ini
// 프로젝트 설정
platformio.ini
.gitignore
.gitattributes

// 환경 설정
.env.example
config.h.template
```

---

## 🔧 코드 관리 방법

### **1. 헤더 파일 구조**
```cpp
#pragma once                    // 헤더 가드 (권장)
#include <Arduino.h>            // 시스템 헤더
#include <OneWire.h>

#include "../domain/Interface.h" // 프로젝트 헤더

// 상수 정의
constexpr int MAX_SENSORS = 8;
constexpr float DEFAULT_TEMP = 25.0f;

// 전방 선언
class SensorManager;

// 클래스 정의
class SensorController {
public:
    // Public 인터페이스
    
private:
    // Private 멤버
};
```

### **2. 소스 파일 구조**
```cpp
#include "SensorController.h"   // 대응 헤더 먼저
#include <vector>               // 시스템 헤더
#include <algorithm>

#include "OtherClass.h"         // 프로젝트 헤더

// 전역 변수 (최소화)
extern OneWire oneWire;

// 구현부
SensorController::SensorController() {
    // 생성자
}

// Public 메서드들

// Private 메서드들
```

### **3. 주석 작성 규칙**
```cpp
/**
 * @brief 센서 임계값을 설정합니다
 * @param sensorIdx 센서 인덱스 (0-7)
 * @param upperTemp 상한 온도 (-55~125°C)
 * @param lowerTemp 하한 온도 (-55~125°C)
 * @return 설정 성공 여부
 */
bool setThresholds(int sensorIdx, float upperTemp, float lowerTemp);

// 복잡한 로직에 대한 설명
void complexFunction() {
    // Step 1: 데이터 검증
    if (!validateInput()) return;
    
    // Step 2: EEPROM에서 기존값 읽기
    loadFromEEPROM();
    
    // Step 3: 새로운 값으로 업데이트
    updateValues();
}
```

---

## 📊 버전 관리 전략

### **1. Git 브랜치 전략**
```
main                    # 안정 버전 (배포용)
├── develop            # 개발 통합 브랜치
├── feature/sensor-mgmt # 기능 개발 브랜치
├── feature/menu-system
├── hotfix/eeprom-bug  # 긴급 수정
└── release/v1.0       # 릴리스 준비
```

### **2. 커밋 메시지 규칙**
```
feat: 센서별 임계값 설정 기능 추가
fix: EEPROM 중복 쓰기 문제 해결
docs: API 문서 업데이트
style: 코드 포맷팅 개선
refactor: SensorController 구조 개선
test: 임계값 검증 테스트 추가
chore: 빌드 스크립트 업데이트
```

### **3. 태그 및 릴리스**
```
v1.0.0    # 메이저 릴리스
v1.0.1    # 패치 릴리스
v1.1.0    # 마이너 릴리스
v2.0.0    # 메이저 업데이트
```

---

## 🧪 테스트 관리

### **1. 테스트 디렉토리 구조**
```
test/
├── unit/                  # 단위 테스트
│   ├── test_sensor_controller.cpp
│   ├── test_menu_controller.cpp
│   └── test_eeprom_manager.cpp
├── integration/           # 통합 테스트
│   ├── test_sensor_integration.cpp
│   └── test_menu_integration.cpp
├── hardware/              # 하드웨어 테스트
│   └── test_ds18b20.cpp
└── mocks/                 # 모의 객체
    ├── MockSensor.h
    └── MockEEPROM.h
```

### **2. 테스트 작성 규칙**
```cpp
#include <unity.h>
#include "SensorController.h"

void setUp(void) {
    // 테스트 전 초기화
}

void tearDown(void) {
    // 테스트 후 정리
}

void test_sensor_threshold_validation(void) {
    SensorController controller;
    
    // Given
    float validUpper = 30.0f;
    float validLower = 20.0f;
    
    // When
    bool result = controller.setThresholds(0, validUpper, validLower);
    
    // Then
    TEST_ASSERT_TRUE(result);
    TEST_ASSERT_EQUAL_FLOAT(validUpper, controller.getUpperThreshold(0));
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_sensor_threshold_validation);
    return UNITY_END();
}
```

---

## 📚 문서화 가이드

### **1. README.md 필수 섹션**
```markdown
# 프로젝트 제목

## 개요
- 프로젝트 목적 및 주요 기능

## 하드웨어 요구사항
- 필요한 부품 목록
- 연결 다이어그램

## 소프트웨어 요구사항
- 개발 환경
- 필요한 라이브러리

## 설치 및 빌드
- 단계별 설치 가이드
- 빌드 명령어

## 사용법
- 기본 사용법
- 설정 방법
- 예제 코드

## API 문서
- 주요 클래스 및 메서드

## 기여 방법
- 개발 가이드라인
- 이슈 리포팅

## 라이선스
```

### **2. 코드 문서화 (Doxygen)**
```cpp
/**
 * @file SensorController.h
 * @brief DS18B20 센서 제어 클래스
 * @author Your Name
 * @date 2025-08-03
 * @version 1.0
 */

/**
 * @class SensorController
 * @brief DS18B20 온도 센서들을 관리하는 컨트롤러 클래스
 * 
 * 이 클래스는 여러 개의 DS18B20 센서를 관리하고,
 * 각 센서별로 개별적인 임계값을 설정할 수 있습니다.
 * 
 * @example
 * @code
 * SensorController controller;
 * controller.setThresholds(0, 30.0f, 20.0f);
 * float temp = controller.getTemperature(0);
 * @endcode
 */
```

---

## 🔒 보안 및 품질 관리

### **1. 코드 품질 체크리스트**
- [ ] 모든 함수에 적절한 주석
- [ ] 매직 넘버 대신 상수 사용
- [ ] 메모리 누수 없음
- [ ] 예외 상황 처리
- [ ] 입력 검증 구현
- [ ] 단위 테스트 작성

### **2. 보안 체크리스트**
- [ ] 하드코딩된 비밀번호 없음
- [ ] 입력 데이터 검증
- [ ] 버퍼 오버플로우 방지
- [ ] 민감한 정보 로깅 금지
- [ ] 안전한 기본값 설정

### **3. 성능 최적화**
- [ ] 메모리 사용량 모니터링
- [ ] EEPROM 쓰기 최소화
- [ ] 불필요한 연산 제거
- [ ] 적절한 데이터 타입 선택
- [ ] 컴파일러 최적화 활용

---

## 🚀 배포 및 유지보수

### **1. 릴리스 체크리스트**
- [ ] 모든 테스트 통과
- [ ] 문서 업데이트
- [ ] 버전 번호 업데이트
- [ ] 변경 로그 작성
- [ ] 바이너리 빌드 및 테스트
- [ ] 태그 생성 및 푸시

### **2. 유지보수 가이드**
- 정기적인 의존성 업데이트
- 보안 패치 적용
- 성능 모니터링
- 사용자 피드백 수집
- 버그 리포트 관리

---

**작성일**: 2025-08-03  
**버전**: v1.0  
**적용 범위**: Arduino/임베디드 프로젝트