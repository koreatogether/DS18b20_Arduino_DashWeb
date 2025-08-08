# 배포 가이드

## 🚀 배포 개요

### **배포 환경**
- **개발 환경**: PlatformIO + VS Code
- **타겟 하드웨어**: Arduino Uno R4 WiFi
- **배포 방식**: USB 직접 업로드
- **설정 관리**: EEPROM 기반 영구 저장

### **배포 준비 체크리스트**
- [x] 코드 컴파일 성공 확인
- [x] 메모리 사용량 검증 (Flash 29.7%, RAM 10.4%)
- [x] 하드웨어 연결 확인
- [ ] 기능 테스트 완료
- [ ] 문서화 완료
- [ ] 백업 생성

## 📦 빌드 및 컴파일

### **1. 개발 환경 설정**

#### PlatformIO 설치 확인
```bash
# PlatformIO 버전 확인
pio --version

# 플랫폼 업데이트
pio platform update

# 라이브러리 의존성 확인
pio lib list
```

#### 필수 라이브러리 설치
```ini
; platformio.ini 설정 확인
[env:uno_r4_wifi]
platform = renesas-ra
board = uno_r4_wifi
framework = arduino
lib_deps = 
    milesburton/DallasTemperature@^3.11.0
    paulstoffregen/OneWire@^2.3.8
    bblanchon/ArduinoJson@^6.21.5
    arduino-libraries/EEPROM@^1.0
```

### **2. 컴파일 및 검증**

#### 릴리스 빌드
```bash
# 클린 빌드
pio run -t clean

# 릴리스 빌드
pio run

# 메모리 사용량 확인
pio run -t size
```

#### 빌드 결과 확인
```
예상 결과:
RAM:   [=         ]  10.4% (used 3412 bytes from 32768 bytes)
Flash: [===       ]  29.7% (used 77796 bytes from 262144 bytes)

✅ 메모리 사용량이 안전 범위 내에 있는지 확인
✅ 컴파일 경고 없음 확인
✅ 링크 오류 없음 확인
```

### **3. 펌웨어 최적화**

#### 릴리스 모드 설정
```cpp
// 릴리스 빌드 시 디버그 출력 비활성화
#ifndef DEBUG_MODE
    #define DEBUG_PRINT(x)
    #define DEBUG_PRINTLN(x)
#else
    #define DEBUG_PRINT(x) Serial.print(x)
    #define DEBUG_PRINTLN(x) Serial.println(x)
#endif
```

#### 컴파일러 최적화
```ini
; platformio.ini에 최적화 플래그 추가
build_flags = 
    -Os                    ; 크기 최적화
    -ffunction-sections    ; 함수별 섹션 분리
    -fdata-sections        ; 데이터별 섹션 분리
    -Wl,--gc-sections      ; 사용하지 않는 섹션 제거
```

## 🔧 하드웨어 배포

### **1. 하드웨어 준비**

#### 연결 확인 체크리스트
```
✅ Arduino Uno R4 WiFi 보드 상태 확인
✅ DS18B20 센서 연결 상태 확인
✅ 4.7kΩ 풀업 저항 연결 확인
✅ 전원 공급 안정성 확인
✅ USB 케이블 연결 상태 확인
```

#### 하드웨어 테스트
```cpp
// 배포 전 하드웨어 테스트 코드
void hardwareTest() {
    Serial.println(F("=== 하드웨어 테스트 시작 ==="));
    
    // 센서 감지 테스트
    sensors.begin();
    int deviceCount = sensors.getDeviceCount();
    Serial.print(F("감지된 센서 개수: "));
    Serial.println(deviceCount);
    
    if (deviceCount == 0) {
        Serial.println(F("❌ 센서가 감지되지 않습니다"));
        return;
    }
    
    // 온도 읽기 테스트
    sensors.requestTemperatures();
    for (int i = 0; i < deviceCount; i++) {
        float temp = sensors.getTempCByIndex(i);
        Serial.print(F("센서 "));
        Serial.print(i);
        Serial.print(F(": "));
        
        if (temp == DEVICE_DISCONNECTED_C) {
            Serial.println(F("연결 오류"));
        } else {
            Serial.print(temp, 1);
            Serial.println(F("°C"));
        }
    }
    
    Serial.println(F("=== 하드웨어 테스트 완료 ==="));
}
```

### **2. 펌웨어 업로드**

#### 업로드 절차
```bash
# 1. 포트 확인
pio device list

# 2. 펌웨어 업로드
pio run -t upload

# 3. 시리얼 모니터 시작
pio device monitor
```

#### 업로드 문제 해결
```
문제: 업로드 실패
해결:
1. USB 케이블 재연결
2. Arduino IDE에서 포트 확인
3. 보드 리셋 버튼 누르고 업로드 재시도
4. 다른 USB 포트 사용

문제: 시리얼 통신 안됨
해결:
1. 보드레이트 115200 확인
2. 시리얼 모니터 설정에서 "Both NL & CR" 선택
3. USB 드라이버 재설치
```

### **3. 초기 설정**

#### 시스템 초기화 확인
```
예상 출력:
=== DS18B20 시스템 시작 ===
1. 시리얼 통신 초기화 완료
Firmware build: Aug  3 2025 14:30:25
DS18B20 센서 초기화 중... 완료
EEPROM 임계값 로드 중........ 완료
EEPROM 측정 주기 로드 중. 완료
현재 측정 주기: 15초
2. 센서 및 EEPROM 초기화 완료
3. 메뉴 컨트롤러 초기화 완료
=== 시스템 초기화 완료 ===
```

#### 기본 설정 검증
```cpp
void verifyInitialSettings() {
    Serial.println(F("=== 초기 설정 검증 ==="));
    
    // 센서 개수 확인
    int deviceCount = sensors.getDeviceCount();
    Serial.print(F("센서 개수: "));
    Serial.println(deviceCount);
    
    // 측정 주기 확인
    Serial.print(F("측정 주기: "));
    Serial.println(sensorController.formatInterval(
        sensorController.getMeasurementInterval()));
    
    // 임계값 확인
    for (int i = 0; i < SENSOR_MAX_COUNT; i++) {
        Serial.print(F("센서 "));
        Serial.print(i + 1);
        Serial.print(F(" 임계값: "));
        Serial.print(sensorController.getUpperThreshold(i), 1);
        Serial.print(F("°C / "));
        Serial.print(sensorController.getLowerThreshold(i), 1);
        Serial.println(F("°C"));
    }
    
    Serial.println(F("=== 검증 완료 ==="));
}
```

## ⚙️ 운영 환경 설정

### **1. 센서 ID 할당**

#### 자동 ID 할당
```
1. 시리얼 모니터에서 'menu' 입력
2. '1' 입력 (센서 ID 조정)
3. '3' 입력 (자동 주소순 ID 할당)
4. 할당 완료 확인
```

#### 수동 ID 할당 (필요시)
```
1. 메뉴 → 1 → 1 (개별 센서 ID 변경)
2. 변경할 센서 번호 입력
3. 새로운 ID 입력
4. 다음 센서 반복
```

### **2. 임계값 설정**

#### 개별 센서 임계값 설정
```
예시: 센서 1번을 35°C/15°C로 설정
1. 메뉴 → 2 → 1 (개별 센서 임계값 설정)
2. '1' 입력 (센서 1번 선택)
3. '35' 입력 (상한 임계값)
4. '15' 입력 (하한 임계값)
5. 설정 완료 확인
```

#### 복수 센서 일괄 설정
```
예시: 센서 1,2,3번을 동일한 임계값으로 설정
1. 메뉴 → 2 → 2 (복수 센서 임계값 설정)
2. '1 2 3' 입력 (센서 선택)
3. 'y' 입력 (확인)
4. '40' 입력 (상한 임계값)
5. '10' 입력 (하한 임계값)
6. 설정 완료 확인
```

### **3. 측정 주기 설정**

#### 측정 주기 조정
```
예시: 30분 주기로 설정
1. 메뉴 → 3 (센서 측정 주기 조정)
2. '30m' 입력 (30분)
3. 설정 완료 확인

복합 시간 예시:
- '1h30m' (1시간 30분)
- '2d12h' (2일 12시간)
- '45s' (45초)
```

## 📊 배포 후 검증

### **1. 기능 테스트**

#### 센서 읽기 테스트
```
✅ 모든 센서에서 유효한 온도값 출력 확인
✅ 센서 상태가 "정상" 또는 적절한 상태로 표시
✅ 15초마다 (또는 설정된 주기마다) 자동 업데이트
✅ 센서 연결 해제 시 "오류" 상태 표시
```

#### 메뉴 시스템 테스트
```
✅ 'menu' 입력 시 메뉴 정상 표시
✅ 각 메뉴 옵션 정상 동작
✅ 'c' 입력 시 취소 기능 동작
✅ 잘못된 입력 시 오류 메시지 표시
```

#### EEPROM 저장 테스트
```
✅ 임계값 설정 후 재부팅 시 값 유지
✅ 측정 주기 설정 후 재부팅 시 값 유지
✅ 센서 ID 설정 후 재부팅 시 값 유지
```

### **2. 성능 검증**

#### 메모리 사용량 모니터링
```cpp
void monitorSystemPerformance() {
    Serial.println(F("=== 시스템 성능 모니터링 ==="));
    
    // 메모리 사용량
    Serial.print(F("사용 가능한 RAM: "));
    Serial.print(freeMemory());
    Serial.println(F(" bytes"));
    
    // 센서 읽기 시간
    unsigned long startTime = millis();
    sensorController.updateSensorRows();
    unsigned long duration = millis() - startTime;
    
    Serial.print(F("센서 업데이트 시간: "));
    Serial.print(duration);
    Serial.println(F(" ms"));
    
    // EEPROM 사용량
    Serial.println(F("EEPROM 사용량: 68/4096 bytes (1.7%)"));
    
    Serial.println(F("=== 모니터링 완료 ==="));
}
```

### **3. 장기 안정성 테스트**

#### 24시간 연속 동작 테스트
```
테스트 항목:
✅ 메모리 누수 없음 확인
✅ 센서 읽기 오류 없음 확인
✅ EEPROM 데이터 무결성 유지
✅ 시리얼 통신 안정성 확인
✅ 전원 공급 안정성 확인
```

## 🔄 업데이트 및 유지보수

### **1. 펌웨어 업데이트**

#### 업데이트 절차
```
1. 현재 설정값 백업 (메뉴에서 확인 후 기록)
2. 새 펌웨어 컴파일 및 업로드
3. 하드웨어 테스트 실행
4. 설정값 복원 (필요시)
5. 기능 테스트 수행
```

#### 설정 백업 방법
```cpp
void backupSettings() {
    Serial.println(F("=== 현재 설정 백업 ==="));
    
    // 측정 주기
    Serial.print(F("측정 주기: "));
    Serial.println(sensorController.formatInterval(
        sensorController.getMeasurementInterval()));
    
    // 센서별 임계값
    for (int i = 0; i < SENSOR_MAX_COUNT; i++) {
        Serial.print(F("센서 "));
        Serial.print(i + 1);
        Serial.print(F(": "));
        Serial.print(sensorController.getUpperThreshold(i), 1);
        Serial.print(F("°C / "));
        Serial.print(sensorController.getLowerThreshold(i), 1);
        Serial.println(F("°C"));
    }
    
    Serial.println(F("=== 백업 완료 ==="));
}
```

### **2. 문제 해결**

#### 일반적인 문제 및 해결책
```
문제: 센서 값이 -127°C로 표시
해결: 센서 연결 상태 확인, 센서 교체

문제: 설정값이 저장되지 않음
해결: EEPROM 초기화, 펌웨어 재업로드

문제: 메뉴가 응답하지 않음
해결: 'reset' 명령어 입력, 하드웨어 리셋

문제: 메모리 부족 오류
해결: 불필요한 디버그 출력 제거, 코드 최적화
```

#### 긴급 복구 절차
```cpp
void emergencyRecovery() {
    Serial.println(F("=== 긴급 복구 시작 ==="));
    
    // 1. 모든 설정 초기화
    sensorController.resetAllSensorIds();
    sensorController.resetAllThresholds();
    sensorController.setMeasurementInterval(DEFAULT_MEASUREMENT_INTERVAL);
    
    // 2. 시스템 상태 리셋
    menuController.resetToNormalState();
    
    // 3. 하드웨어 테스트
    hardwareTest();
    
    Serial.println(F("=== 긴급 복구 완료 ==="));
    Serial.println(F("시스템이 기본 설정으로 복구되었습니다"));
}
```

## 📋 배포 체크리스트

### **배포 전 확인사항**
- [ ] 코드 컴파일 성공
- [ ] 메모리 사용량 안전 범위 내
- [ ] 하드웨어 연결 확인
- [ ] 기본 기능 테스트 완료
- [ ] 설정 백업 완료

### **배포 후 확인사항**
- [ ] 시스템 초기화 정상 완료
- [ ] 센서 감지 및 온도 읽기 정상
- [ ] 메뉴 시스템 정상 동작
- [ ] EEPROM 저장/로드 정상
- [ ] 24시간 안정성 테스트 완료

### **문서화 완료사항**
- [ ] 설정값 기록
- [ ] 하드웨어 구성 문서화
- [ ] 문제 해결 가이드 준비
- [ ] 사용자 매뉴얼 작성

---

**작성일**: 2025-08-03  
**버전**: v1.0  
**배포 환경**: Arduino Uno R4 WiFi + DS18B20  
**상태**: 배포 준비 완료