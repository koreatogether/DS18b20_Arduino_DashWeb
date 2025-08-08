# 문제 해결 가이드

## 🚨 일반적인 문제 및 해결책

### **1. 센서가 감지되지 않는 문제**

#### 증상
- 시리얼 모니터에 "연결된 센서가 없습니다" 메시지
- 센서 개수가 0으로 표시
- 모든 센서 상태가 "N/A"

#### 원인 및 해결책
```
❌ 문제: 하드웨어 연결 불량
✅ 해결: 
   - DS18B20 핀 연결 재확인 (VDD-5V, GND-GND, Data-Pin2)
   - 브레드보드 접촉 불량 확인
   - 점퍼 와이어 교체

❌ 문제: 풀업 저항 누락
✅ 해결:
   - 4.7kΩ 저항을 Data 라인과 VDD 사이에 연결
   - 저항값 확인 (3.3kΩ~10kΩ 범위 사용 가능)

❌ 문제: 전원 공급 불안정
✅ 해결:
   - USB 케이블 교체
   - 외부 5V 전원 어댑터 사용
   - 전원 라인에 100μF 캐패시터 추가
```

#### 디버깅 코드
```cpp
void debugSensorConnection() {
    Serial.println("=== 센서 연결 디버깅 ===");
    Serial.print("감지된 센서 개수: ");
    Serial.println(sensors.getDeviceCount());
    
    if (sensors.getDeviceCount() == 0) {
        Serial.println("1. 하드웨어 연결 확인");
        Serial.println("2. 풀업 저항 (4.7kΩ) 확인");
        Serial.println("3. 전원 공급 확인");
    }
}
```

### **2. 온도 값이 -127°C로 표시되는 문제**

#### 증상
- 특정 센서의 온도가 항상 -127.00°C
- 간헐적으로 -127°C와 정상값 사이를 오감

#### 원인 및 해결책
```
❌ 문제: 센서 불량
✅ 해결:
   - 다른 DS18B20 센서로 교체
   - 센서 핀 납땜 상태 확인

❌ 문제: 데이터 라인 노이즈
✅ 해결:
   - 케이블 길이 단축 (1m 이하 권장)
   - 차폐 케이블 사용
   - 데이터 라인에 100Ω 직렬 저항 추가

❌ 문제: 전원 부족
✅ 해결:
   - 센서별 개별 전원 공급
   - 더 큰 용량의 전원 어댑터 사용
```

### **3. EEPROM 데이터 손실 문제**

#### 증상
- 재부팅 후 설정값이 기본값으로 돌아감
- "EEPROM 데이터 손상" 메시지
- 임계값이 무작위 값으로 표시

#### 원인 및 해결책
```
❌ 문제: EEPROM 초기화 미실행
✅ 해결:
   - setup()에서 initializeThresholds() 호출 확인
   - 시리얼 초기화 후 EEPROM 초기화 순서 준수

❌ 문제: 전원 불안정으로 인한 데이터 손상
✅ 해결:
   - 안정적인 전원 공급
   - 전원 라인에 큰 용량 캐패시터 추가
   - UPS 사용 (중요한 설정의 경우)

❌ 문제: EEPROM 수명 초과
✅ 해결:
   - 새로운 Arduino 보드 사용
   - 외부 EEPROM 모듈 추가 고려
```

### **4. 메뉴 시스템 응답 없음**

#### 증상
- 'menu' 입력해도 메뉴가 나타나지 않음
- 키보드 입력이 인식되지 않음
- 시리얼 모니터에 아무것도 출력되지 않음

#### 원인 및 해결책
```
❌ 문제: 시리얼 통신 설정 불일치
✅ 해결:
   - 보드레이트 115200으로 설정 확인
   - 시리얼 모니터 설정에서 "Both NL & CR" 선택
   - USB 드라이버 재설치

❌ 문제: 애플리케이션 상태 오류
✅ 해결:
   - 'reset' 명령어 입력
   - Arduino 하드웨어 리셋 버튼 누르기
   - 펌웨어 재업로드

❌ 문제: 입력 버퍼 오버플로우
✅ 해결:
   - 시리얼 모니터 재시작
   - 짧은 명령어 사용
   - 입력 간격 두기
```

### **5. 메모리 부족 문제**

#### 증상
- 시스템이 무작위로 재시작
- 일부 기능이 작동하지 않음
- 컴파일 시 메모리 경고

#### 원인 및 해결책
```
❌ 문제: RAM 부족
✅ 해결:
   - 불필요한 전역 변수 제거
   - String 대신 char 배열 사용
   - F() 매크로로 문자열을 Flash에 저장

❌ 문제: Flash 메모리 부족
✅ 해결:
   - 불필요한 라이브러리 제거
   - 디버그 메시지 최소화
   - 코드 최적화

❌ 문제: 스택 오버플로우
✅ 해결:
   - 재귀 함수 사용 최소화
   - 큰 지역 변수를 전역으로 이동
   - 함수 호출 깊이 줄이기
```

## 🔧 고급 문제 해결

### **6. 센서 ID 할당 문제**

#### 증상
- 센서 ID가 무작위로 변경됨
- 동일한 ID가 여러 센서에 할당됨
- ID 설정이 저장되지 않음

#### 디버깅 방법
```cpp
void debugSensorIDs() {
    Serial.println("=== 센서 ID 디버깅 ===");
    int deviceCount = sensors.getDeviceCount();
    
    for (int i = 0; i < deviceCount; i++) {
        DeviceAddress addr;
        sensors.getAddress(addr, i);
        
        Serial.print("센서 ");
        Serial.print(i);
        Serial.print(" 주소: ");
        for (int j = 0; j < 8; j++) {
            if (addr[j] < 16) Serial.print("0");
            Serial.print(addr[j], HEX);
        }
        Serial.print(" ID: ");
        Serial.println(sensorController.getSensorLogicalId(i));
    }
}
```

### **7. 측정 주기 설정 문제**

#### 증상
- 설정한 주기와 다르게 동작
- 복합 시간 입력이 파싱되지 않음
- 주기 설정이 저장되지 않음

#### 디버깅 방법
```cpp
void debugMeasurementInterval() {
    Serial.println("=== 측정 주기 디버깅 ===");
    unsigned long interval = sensorController.getMeasurementInterval();
    
    Serial.print("현재 설정된 주기: ");
    Serial.print(interval);
    Serial.println("ms");
    
    Serial.print("포맷된 주기: ");
    Serial.println(sensorController.formatInterval(interval));
    
    Serial.print("유효성 검사: ");
    Serial.println(sensorController.isValidMeasurementInterval(interval) ? "통과" : "실패");
}
```

### **8. EEPROM 수명 관리**

#### EEPROM 사용량 모니터링
```cpp
void monitorEEPROMUsage() {
    Serial.println("=== EEPROM 사용량 ===");
    Serial.print("센서 임계값: 0-63 bytes (");
    Serial.print((64.0 / 4096.0) * 100, 1);
    Serial.println("%)");
    
    Serial.print("측정 주기: 64-67 bytes (");
    Serial.print((4.0 / 4096.0) * 100, 1);
    Serial.println("%)");
    
    Serial.print("총 사용량: 68/4096 bytes (");
    Serial.print((68.0 / 4096.0) * 100, 1);
    Serial.println("%)");
    
    Serial.print("여유 공간: ");
    Serial.print(4096 - 68);
    Serial.println(" bytes");
}
```

## 📊 성능 최적화

### **메모리 사용량 최적화**
```cpp
// ❌ 비효율적
String message = "센서 " + String(i) + "번 온도: " + String(temp) + "°C";

// ✅ 효율적
char message[50];
snprintf(message, sizeof(message), "센서 %d번 온도: %.1f°C", i, temp);
```

### **EEPROM 쓰기 최소화**
```cpp
// ✅ 이미 구현됨 - 값이 변경된 경우에만 쓰기
void saveSensorThresholds(int sensorIdx) {
    float currentUpper, currentLower;
    EEPROM.get(addr, currentUpper);
    EEPROM.get(addr + 4, currentLower);
    
    if (currentUpper != newUpper) {
        EEPROM.put(addr, newUpper);
    }
    
    if (currentLower != newLower) {
        EEPROM.put(addr + 4, newLower);
    }
}
```

## 🆘 긴급 복구 방법

### **완전 초기화**
```cpp
void emergencyReset() {
    Serial.println("=== 긴급 초기화 실행 ===");
    
    // 1. 모든 센서 ID 초기화
    sensorController.resetAllSensorIds();
    
    // 2. 모든 임계값 초기화
    sensorController.resetAllThresholds();
    
    // 3. 측정 주기 기본값으로 설정
    sensorController.setMeasurementInterval(15000);
    
    // 4. 메뉴 상태 초기화
    menuController.resetToNormalState();
    
    Serial.println("초기화 완료 - 시스템 재시작 권장");
}
```

### **EEPROM 완전 지우기**
```cpp
void clearEEPROM() {
    Serial.println("EEPROM 완전 지우기 중...");
    
    for (int i = 0; i < 100; i++) {  // 처음 100바이트만
        EEPROM.write(i, 0xFF);
    }
    
    Serial.println("EEPROM 지우기 완료 - 재부팅 필요");
}
```

## 📞 지원 요청 시 필요한 정보

### **시스템 정보 수집**
```cpp
void collectSystemInfo() {
    Serial.println("=== 시스템 정보 ===");
    Serial.print("펌웨어 빌드: ");
    Serial.print(__DATE__);
    Serial.print(" ");
    Serial.println(__TIME__);
    
    Serial.print("감지된 센서 개수: ");
    Serial.println(sensors.getDeviceCount());
    
    Serial.print("현재 측정 주기: ");
    Serial.println(sensorController.formatInterval(sensorController.getMeasurementInterval()));
    
    Serial.print("메뉴 상태: ");
    Serial.println((int)menuController.getAppState());
    
    Serial.print("사용 가능한 RAM: ");
    Serial.println(freeMemory());  // 별도 구현 필요
}
```

---

**작성일**: 2025-08-03  
**버전**: v1.0  
**업데이트**: 문제 발견 시 지속적으로 업데이트