# 하드웨어 설정 가이드

## 🔌 필요한 부품 목록

### **필수 부품**
- Arduino Uno R4 WiFi × 1
- DS18B20 온도 센서 × 1~8개
- 4.7kΩ 풀업 저항 × 1
- 브레드보드 × 1
- 점퍼 와이어 (수-수, 수-암)

### **선택 부품**
- 방수 DS18B20 센서 (실외 사용 시)
- PCB 보드 (영구 설치 시)
- 전원 어댑터 (5V 2A 권장)
- 케이스 (보호용)

## 🔧 연결 다이어그램

```
Arduino Uno R4 WiFi
┌─────────────────┐
│  Digital Pin 2  │────┬─── DS18B20 #1 (Data)
│                 │    │
│  5V             │────┼─── DS18B20 #1 (VDD)
│                 │    │    DS18B20 #2 (VDD)
│                 │    │    ...
│                 │    │
│  GND            │────┼─── DS18B20 #1 (GND)
│                 │    │    DS18B20 #2 (GND)
│                 │    │    ...
└─────────────────┘    │
                       │
                    4.7kΩ
                  (풀업 저항)
                       │
                       └─── DS18B20 #2 (Data)
                            DS18B20 #3 (Data)
                            ...
```

## 📐 상세 연결 방법

### **1. DS18B20 핀 배치**
```
DS18B20 (TO-92 패키지)
     ┌─────┐
     │  1  │ GND (검정)
     │  2  │ Data (노랑/흰색)
     │  3  │ VDD (빨강)
     └─────┘
```

### **2. 연결 단계**
1. **전원 연결**
   - DS18B20의 VDD(3번 핀) → Arduino 5V
   - DS18B20의 GND(1번 핀) → Arduino GND

2. **데이터 라인 연결**
   - DS18B20의 Data(2번 핀) → Arduino Digital Pin 2
   - 4.7kΩ 저항을 Data 라인과 VDD 사이에 연결 (풀업)

3. **다중 센서 연결**
   - 모든 DS18B20를 병렬로 연결
   - 각 센서의 동일한 핀끼리 연결
   - 풀업 저항은 하나만 사용

## ⚠️ 주의사항

### **전원 관련**
- DS18B20는 3.0V~5.5V에서 동작
- 패러사이트 파워 모드 사용 시 별도 전원 불필요
- 다중 센서 사용 시 충분한 전류 공급 확인

### **신호 품질**
- 데이터 라인 길이는 최대 100m (CAT5 케이블 사용 시)
- 긴 케이블 사용 시 120Ω 종단 저항 고려
- 노이즈가 많은 환경에서는 차폐 케이블 사용

### **센서 식별**
- 각 DS18B20는 고유한 64비트 ROM 코드 보유
- 시스템에서 자동으로 센서 감지 및 ID 할당
- 최대 8개 센서까지 지원

## 🧪 연결 테스트

### **1. 기본 연결 확인**
```cpp
// 테스트 코드 (Arduino IDE)
#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(115200);
  sensors.begin();
  Serial.print("센서 개수: ");
  Serial.println(sensors.getDeviceCount());
}

void loop() {
  sensors.requestTemperatures();
  for(int i = 0; i < sensors.getDeviceCount(); i++) {
    Serial.print("센서 ");
    Serial.print(i);
    Serial.print(": ");
    Serial.println(sensors.getTempCByIndex(i));
  }
  delay(1000);
}
```

### **2. 문제 해결**
- **센서가 감지되지 않는 경우**
  - 연결 상태 재확인
  - 풀업 저항 확인 (4.7kΩ)
  - 전원 공급 확인

- **온도 값이 -127°C로 나오는 경우**
  - 센서 불량 또는 연결 불량
  - 데이터 라인 연결 확인

- **간헐적으로 값이 이상한 경우**
  - 노이즈 간섭 (차폐 케이블 사용)
  - 전원 불안정 (캐패시터 추가)

## 📦 권장 설치 방법

### **프로토타입 단계**
- 브레드보드 사용
- 점퍼 와이어로 연결
- 테스트 및 개발 용이

### **영구 설치 단계**
- PCB 보드에 납땜
- 터미널 블록 사용 (센서 교체 용이)
- 케이스에 설치 (보호)

### **실외 설치 시**
- 방수 DS18B20 센서 사용
- IP65 이상 케이스 사용
- 케이블 방수 처리
- 낙뢰 보호 회로 고려

---

**작성일**: 2025-08-03  
**버전**: v1.0  
**검증 완료**: Arduino Uno R4 WiFi + DS18B20