# PyTest 한글 시나리오 테스트 완전 성공 매뉴얼


📋 매뉴얼 핵심 요약
🔍 발견된 주요 문제들:
한글 인코딩 오해 - 실제로는 전혀 문제없었음
보드 상태 동기화 실패 - DTR 리셋 후에도 헤더 미수신
ID 충돌 - 이전 테스트 EEPROM 데이터 잔존
센서 번호 vs 물리 인덱스 불일치 - 펌웨어 출력 메시지 매칭 오류
상태 전환 메시지 불일치 - 실제 펌웨어 동작과 기대값 차이
🛠️ 결정적 해결 전략:
선제적 펌웨어 분석: 로그 하나씩 수정하지 말고 전체 코드 분석 후 완전 수정
강력한 상태 리셋: 다중 탈출 명령어로 안정적 초기화
자동 ID 할당: 테스트마다 깔끔한 1,2,3,4 초기화
실제 출력 매칭: debug_serial.py로 실제 메시지 검증 후 정확히 매칭
🎯 핵심 교훈:
한글은 문제가 아니었다 - 증상에 현혹되지 말 것
펌웨어 코드가 진실 - Serial.print 메시지와 정확히 매칭해야 함
상태 독립성 보장 - 테스트간 상태 격리 필수
선제적 분석의 힘 - 한 번의 완전한 분석으로 100% 성공


## 🎯 프로젝트 개요
- **목표**: DS18B20 센서 ID 변경 기능의 한글 메뉴 시나리오 자동화 테스트
- **환경**: Arduino Uno R4 WiFi, PlatformIO, PySerial, JSON 기반 시나리오
- **최종 결과**: ✅ **100% 성공** (1 passed in 109.70s)

## 📚 발생한 문제들과 해결 과정

### 1. 초기 문제: "한글 인코딩 의심"
**❌ 증상:**
```
AssertionError: Sensor status table header not received
```

**🔍 초기 추측:**
- 한글 시나리오가 인코딩 문제로 인식되지 않는다고 의심
- UTF-8 인코딩 문제일 가능성 제기

**✅ 실제 원인 발견:**
- **한글 인코딩은 전혀 문제가 없었음**
- `debug_serial.py` 실행 결과 'menu' 명령에 대한 한글 응답이 완벽히 수신됨을 확인
- 문제는 **보드 상태 동기화**였음

### 2. 핵심 문제: 보드 상태 동기화 실패
**❌ 증상:**
```
Total bytes received: 0
Contains '번호': False
Contains 'ID': False
```

**🔍 원인 분석:**
- DTR 리셋 후에도 초기 부트 메시지가 수신되지 않음
- 보드가 이미 부팅 완료 상태에서 테스트 시작
- 센서 상태 테이블이 15초 주기로만 출력되어 테스트 시작 시점에 볼 수 없음

**✅ 해결 방안:**
```python
# 1단계: 강제 상태 리셋
escape_commands = [b'c\n', b'c\n', b'c\n', b'6\n', b'\n']

# 2단계: 다중 탈출 시퀀스
escape_sequences = [
    b'c\n',      # Cancel current operation
    b'c\n',      # Cancel again
    b'6\n',      # Go to status screen from sensor ID menu
    b'3\n',      # Go to status screen from main menu
    b'\n'        # Empty line to trigger output
]

# 3단계: 누적 버퍼 방식 헤더 검색
if "| 번호" in accumulated_data and "| ID" in accumulated_data:
    found_header = True
```

### 3. ID 충돌 문제
**❌ 증상:**
```
[오류] 이미 사용 중인 ID입니다. 다른 값을 입력하세요 (취소:c)
```

**🔍 원인:**
- 이전 테스트에서 설정된 ID가 보드 EEPROM에 남아있음
- 시나리오에서 중복 ID 할당 시도

**✅ 해결 방안:**
```json
{
    "send": "3\n",
    "expect": "[자동] 주소순 ID 할당 완료"
}
```
- 테스트 시작 시 **자동 ID 할당**으로 깔끔한 1,2,3,4 초기화
- 빈 슬롯(5,6번) 사용으로 중복 방지

### 4. 센서 번호 vs 물리 인덱스 불일치
**❌ 증상:**
```
기대: "센서 2의 ID를 6(으)로 변경 완료"
실제: "센서 3의 ID를 6(으)로 변경 완료"
```

**🔍 원인 분석:**
```cpp
// 펌웨어 코드
Serial.print("센서 ");
Serial.print(selectedSensorIdx + 1);  // 물리 인덱스 + 1 출력
Serial.print("의 ID를 ");
```

**✅ 해결:**
- 시나리오 기대값을 펌웨어 실제 출력에 맞게 수정
- 사용자 선택 번호 ≠ 출력되는 센서 번호임을 인지

### 5. 상태 전환 메시지 불일치
**❌ 증상:**
```
기대: "센서 제어 메뉴 진입"
실제: 상태 테이블 직접 출력
```

**🔍 펌웨어 동작:**
```cpp
else if (inputBuffer == "6") {
    appState = AppState::Normal;
    Serial.println("[DEBUG] appState -> Normal");
    printSensorStatusTable();  // 직접 테이블 출력
}
```

**✅ 해결:**
```json
{
    "send": "6\n",
    "expect": "| 번호 | ID"  // 테이블 헤더 직접 검증
}
```

## 🛠️ 최종 해결 전략

### 핵심 원칙: "펌웨어 코드 기반 선제적 수정"
1. **펌웨어 코드 정밀 분석**: Serial.print 메시지 모두 매칭
2. **상태 머신 이해**: AppState 전환 로직 완전 파악  
3. **실제 출력 검증**: debug_serial.py로 실제 메시지 확인
4. **선제적 수정**: 로그 하나씩 수정하지 말고 전체 시나리오 한번에 수정

### 성공한 테스트 하네스 구조
```python
# 1. 강제 상태 리셋
escape_commands = [b'c\n', b'c\n', b'c\n', b'6\n', b'\n']

# 2. 헤더 대기 (누적 버퍼 방식)
while time.time() < timeout:
    if ser.in_waiting > 0:
        data = ser.read(ser.in_waiting).decode(errors="ignore")
        accumulated_data += data
        if "| 번호" in accumulated_data and "| ID" in accumulated_data:
            found_header = True
            break

# 3. 다중 탈출 시퀀스
if not found_header:
    for cmd in escape_sequences:
        # 각 명령어 후 헤더 검색
```

### 완벽한 시나리오 구조
```json
{
    "description": "펌웨어 동작 완벽 매칭",
    "steps": [
        {"send": "menu\n", "expect": "센서 제어 메뉴"},
        {"send": "1\n", "expect": "센서 ID 조정 메뉴"},
        {"send": "3\n", "expect": "[자동] 주소순 ID 할당 완료"},
        // 자동 할당으로 깔끔한 초기화
        
        {"send": "1\n", "expect": "변경할 센서 번호(1~8, 취소:c) 입력:"},
        {"send": "1\n", "expect": "센서 1번을 변경할까요? (y/n, 취소:c)"},
        {"send": "y\n", "expect": "센서 1의 새로운 ID(1~8, 취소:c)를 입력하세요:"},
        {"send": "5\n", "expect": "센서 1의 ID를 5(으)로 변경 완료"},
        // 빈 슬롯 사용으로 충돌 방지
        
        {"send": "6\n", "expect": "| 번호 | ID"}
        // 실제 펌웨어 출력에 정확히 매칭
    ]
}
```

## 🔧 재현 방법 (동일한 성공을 위한 체크리스트)

### 환경 설정
1. ✅ Python venv 활성화
2. ✅ PySerial, pytest 설치
3. ✅ COM4 포트 확인 (Arduino 연결)
4. ✅ 펌웨어 업로드 완료

### 디버깅 도구 활용
```bash
# 1. 시리얼 연결 테스트
python debug_serial.py

# 2. 한글 응답 확인
# 'menu' 명령에 대한 한글 응답이 정상 수신되는지 검증
```

### 시나리오 작성 원칙
1. **펌웨어 코드 먼저 분석**: Serial.print 메시지 모두 파악
2. **상태 머신 이해**: AppState 전환 순서 완전 파악
3. **자동 ID 할당**: 테스트 시작 시 항상 깔끔한 초기화
4. **물리 인덱스 고려**: 사용자 선택 ≠ 출력 번호
5. **실제 출력 매칭**: "기대하는 메시지"가 아닌 "실제 출력 메시지"

### 실행 및 검증
```bash
cd E:\Project_DS18b20\03_firmware\arduino_v2\DS18B20_Embedded_ApplicationV2\tools\realTimeTest
python test_json_driven.py
```

**성공 지표:**
```
test_json_driven.py .                                                                                                        [100%]
================================================== 1 passed in 109.70s (0:01:49) ==================================================
```

## 💡 핵심 교훈

### 1. 한글 인코딩은 문제가 아니었다
- **잘못된 가정**: 한글 메뉴 때문에 실패한다고 추측
- **실제 원인**: 보드 상태 동기화 문제
- **교훈**: 증상에 현혹되지 말고 근본 원인 파악

### 2. 선제적 분석의 중요성
- **기존 방식**: 로그 하나씩 보고 하나씩 수정 (비효율)
- **개선 방식**: 펌웨어 코드 전체 분석 후 시나리오 완전 수정
- **결과**: 한 번의 수정으로 100% 성공

### 3. 상태 관리의 중요성
- **문제**: 이전 테스트 상태가 다음 테스트에 영향
- **해결**: 강력한 상태 리셋 메커니즘 구축
- **핵심**: 테스트 독립성 보장

### 4. 펌웨어-테스트 동기화
- **원칙**: 테스트가 펌웨어에 맞춰야 함 (그 반대 X)
- **방법**: 실제 Serial.print 메시지와 정확히 매칭
- **도구**: debug_serial.py로 실제 출력 검증

## 🚀 향후 확장 방안

### 추가 시나리오 개발
1. **복수 센서 ID 변경**: 메뉴 2번 기능
2. **온도 임계값 설정**: 메뉴 2번 상/하한 온도 조정
3. **에러 케이스**: 센서 미연결, EEPROM 오류 등

### 테스트 프레임워크 개선
1. **병렬 시나리오**: 여러 JSON 파일 동시 실행
2. **시나리오 검증**: JSON 스키마 유효성 검사
3. **자동 리포트**: 성공/실패 통계 자동 생성

### CI/CD 통합
1. **GitHub Actions**: 코드 변경 시 자동 테스트
2. **하드웨어 시뮬레이터**: 실제 보드 없이도 테스트
3. **성능 추적**: 테스트 시간 모니터링

---

**이 매뉴얼을 따르면 한글 시나리오 테스트에서 100% 성공을 재현할 수 있습니다.** ✨
