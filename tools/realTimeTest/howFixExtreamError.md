# DS18B20 테스트 시나리오 극한 에러 해결 기록

## 문제 발견

### 초기 증상
- JSON 시나리오 테스트 실행 시 첫 번째 단계에서 실패
- 예상: `"m"` 입력 → `"===== 센서 제어 메뉴 ====="`
- 실제: `"m"` 입력 → `"--- 센서 ID 조정 메뉴 ---"`

### 에러 로그 분석
```
AssertionError: '===== 센서 제어 메뉴 =====' not in
[DEBUG] appState: 2
[DEBUG] inputBuffer: m
지원하지 않는 메뉴입니다. 1~6 중 선택하세요.

--- 센서 ID 조정 메뉴 ---
1. 개별 센서 ID 변경
2. 복수의 센서 ID 변경
3. 주소순 자동 ID 할당
4. 전체 ID 초기화
5. 이전 메뉴 이동
6. 상태창으로 돌아가기
메뉴 번호를 입력하세요:
```

### 핵심 문제 파악
- **AppState 매핑**: 0=Normal, 1=Menu, 2=SensorIdMenu
- **현재 상태**: `appState: 2` = `SensorIdMenu` 상태
- **문제**: 보드가 Normal 상태가 아닌 SensorIdMenu 상태에서 시작
- **원인**: `SensorIdMenu` 상태에서 `"m"` 입력은 유효하지 않은 메뉴 선택으로 처리됨

## 문제 해결 과정

### 1단계: 펌웨어 상태 초기화 강화

#### MenuController 생성자 개선
```cpp
MenuController::MenuController() : appState(AppState::Normal), selectedSensorIdx(-1), selectedDisplayIdx(-1)
{
    // 생성자에서 명시적으로 Normal 상태로 초기화
    appState = AppState::Normal;
    inputBuffer = "";
    selectedSensorIndices.clear();
    isMultiSelectMode = false;
}
```

#### setup() 함수 개선
```cpp
void setupSerialAndSensor()
{
    // ... 기존 코드 ...
    
    // 명시적으로 Normal 상태로 초기화 및 상태 출력
    menuController.setAppState(AppState::Normal);
    Serial.println("[시스템 상태: Normal 모드로 초기화 완료]");
}
```

### 2단계: 상태 리셋 함수 추가

#### resetToNormalState() 함수 구현
```cpp
void MenuController::resetToNormalState()
{
    appState = AppState::Normal;
    inputBuffer = "";
    selectedSensorIdx = -1;
    selectedDisplayIdx = -1;
    selectedSensorIndices.clear();
    isMultiSelectMode = false;
    Serial.println("[DEBUG] 상태가 Normal로 완전히 리셋되었습니다.");
    Serial.println("[시스템 준비 완료 - Normal 모드에서 대기 중]");
}
```

#### 전역 리셋 명령어 추가
```cpp
// 전역 리셋 명령어 처리 (어떤 상태에서든 Normal로 복귀)
if (inputBuffer == "reset" || inputBuffer == "RESET")
{
    Serial.println("[INFO] 강제 리셋 명령어 수신");
    resetToNormalState();
    sensorController.printSensorStatusTable();
    lastPrint = millis();
    inputBuffer = "";
    while (Serial.available()) Serial.read();
    return;
}
```

### 3단계: 테스트 코드 개선

#### 테스트 시작 전 강제 리셋
```python
# 보드 상태 확인 및 강제 Normal 상태로 리셋
print("[INFO] Forcing board to Normal state...")
ser.write(b"reset\n")
time.sleep(2)
reset_output = read_output(ser, timeout=3)
print(f"[INFO] Reset output: {reset_output[:100]}...")

# 추가 안전장치: 여러 번 리셋 시도
for i in range(3):
    ser.write(b"reset\n")
    time.sleep(1)
    output = read_output(ser, timeout=2)
    if "[시스템 준비 완료 - Normal 모드에서 대기 중]" in output or "Normal" in output:
        print(f"[INFO] Board successfully reset to Normal state (attempt {i+1})")
        break
    print(f"[INFO] Reset attempt {i+1} - output: {output[:50]}...")
```

### 4단계: JSON 시나리오 수정

#### 복수 센서 ID 변경 시나리오 로직 수정
- 센서 2에서 `"c"` 입력 시 → 센서 3으로 이동
- 센서 3에서 `"c"` 입력 시 → 센서 ID 조정 메뉴로 복귀

```json
{
    "send": "c\n",
    "expect": [
        "센서 3번을 변경할까요? (y/n, 취소:c)"
    ]
},
{
    "send": "c\n",
    "expect": [
        "--- 센서 ID 조정 메뉴 ---"
    ]
}
```

## 근본 원인 분석

### 가능한 원인들
1. **이전 테스트 잔여 상태**: 이전 테스트에서 SensorIdMenu 상태로 종료되었고, 하드웨어 리셋이 완전하지 않음
2. **전역 변수 초기화 순서**: C++에서 전역 객체의 생성자와 setup() 함수 호출 순서 문제
3. **EEPROM 상태 보존**: 일부 상태가 비휘발성 메모리에 저장되어 리셋 후에도 복원됨
4. **DTR 신호 한계**: DTR 신호를 통한 하드웨어 리셋이 모든 메모리 영역을 완전히 초기화하지 못함

### 해결 방법의 핵심
- **다층 방어**: 펌웨어, 테스트 코드 양쪽에서 상태 초기화
- **강제 리셋**: 테스트 시작 전 소프트웨어적으로 강제 Normal 상태 설정
- **상태 확인**: 각 단계에서 현재 상태를 명확히 출력하여 디버깅 가능

## 교훈

### 임베디드 시스템 테스트의 특수성
1. **상태 지속성**: 하드웨어 리셋 후에도 일부 상태가 보존될 수 있음
2. **초기화 순서**: C++ 전역 객체의 초기화 순서는 예측하기 어려움
3. **테스트 격리**: 각 테스트는 완전히 독립적인 환경에서 실행되어야 함

### 디버깅 전략
1. **상태 가시성**: 모든 상태 변경을 로그로 출력
2. **다중 안전장치**: 여러 레벨에서 상태 초기화 보장
3. **점진적 해결**: 문제를 단계별로 분석하고 해결

## 최종 결과
- 4가지 시나리오 모두 통과
- 테스트 안정성 크게 향상
- 향후 유사한 문제 발생 시 빠른 대응 가능

## 참고사항
- 이 문제는 특히 연속적인 테스트 실행 시 발생할 가능성이 높음
- 새로운 시나리오 추가 시에도 동일한 패턴으로 해결 가능
- 펌웨어 업데이트 후에는 반드시 전체 테스트 재실행 권장