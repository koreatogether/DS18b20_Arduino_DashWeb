#### strncpy 사용 취약점 (CWE-120, Insecure Modules Libraries)
- null 종료 미보장, 잘못된 포인터 체크 미흡, MS-banned 함수

#### strncpy 사용 취약점 (CWE-120, Insecure Modules Libraries)
 - null 종료 미보장, 잘못된 포인터 체크 미흡, MS-banned 함수
 - 해결 방법: 모든 strncpy 사용 코드를 직접 반복문 복사 방식으로 대체하여 null 종료와 오버플로우를 명확히 보장.

 #### strcpy/strncpy 사용 탐지 (Insecure Modules Libraries)
	 - strcpy, strncpy 사용 시 무조건 경고 발생
	 - 해결 방법: 모든 strncpy 사용 코드를 반복문 복사 방식으로 대체하여 경고 발생 원천 차단.

 #### Input Validation 취약점 (CWE-126)
	 - null 종료되지 않은 문자열 처리 미흡, 오버리드 위험
	 - 해결 방법: 테스트 코드에서 strlen 사용 전 summary 버퍼의 마지막 바이트가 항상 '\0'임을 assert로 명확히 체크하여 null 종료 보장.

# C++17 환경에서 static 람다/this 캡처 및 std::function 사용 시 메모리 접근 에러(3221225477) 사례와 해결 방법

## 문제 상황
- C++17 표준에서 `<functional>`, `std::function`, 람다, static 지역 변수 모두 정상 지원.
- 하지만 아래와 같은 코드 패턴에서 테스트 종료(cleanup) 시 3221225477(Access Violation) 에러가 발생:
  - static 지역 변수로 `std::map<std::string, std::function<...>>` 선언
  - 람다에서 `this` 포인터를 캡처하여 멤버 함수/멤버 변수 접근
  - 테스트 teardown/cleanup 또는 프로그램 종료 시, 이미 소멸된 객체의 this를 static 람다가 참조하게 됨

## 원인 분석
- static map은 프로그램 종료 시점까지 살아있음
- 람다에서 this를 캡처하면, 객체가 먼저 소멸된 후에도 static map 내부 람다가 dangling pointer(this)를 보유
- 테스트 프레임워크의 cleanup, 혹은 static 변수 해제 시점에 잘못된 메모리 접근 발생 → 3221225477(Access Violation)

## 해결 방법
- static map/람다 대신, 멤버 변수 map + 멤버 함수 포인터 구조로 리팩터링
- 람다에서 this 캡처를 제거하고, 안전하게 멤버 함수 포인터 호출로 대체
- 예시:
  ```cpp
  // 잘못된 예시 (static map + 람다 this 캡처)
  static const std::map<std::string, std::function<std::string()>> handlers = {
      {"help", [this]() { return getHelpMessage(); }},
      ...
  };
  
  // 안전한 예시 (멤버 변수 map + 멤버 함수 포인터)
  std::map<std::string, std::string (ClassName::*)()> handlerMap;
  handlerMap["help"] = &ClassName::getHelpMessageHandler;
  ...
  // 호출: (this->*handlerMap[cmd])();
  ```

## 앞으로의 교훈 및 주의사항
- C++17 표준이라도 static 람다에서 this 캡처는 객체 생명주기와 충돌 시 치명적 런타임 에러를 유발할 수 있음
- static 지역 변수와 객체 포인터/참조의 생명주기 관계를 항상 명확히 할 것
- 멤버 함수 포인터, weak_ptr, 복사 캡처 등 안전한 대안을 우선 고려
- 테스트/임베디드 환경에서는 cleanup, teardown, static 해제 타이밍에 특히 주의

---
이 사례를 통해, 표준 문법이라도 객체 생명주기와 메모리 관리에 대한 깊은 이해가 필수임을 반드시 기억할 것!

임베디드 개발에서는 실기기 테스트와, 모든 포인터/버퍼/상태값의 명확한 초기화 및 예외처리가 필수입니다.

# MCU 런타임 크래시 분석 및 해결 과정 정리

## 1. 문제 발생
- MCU(Arduino Uno R4 WiFi)에서 주기적으로 버스 폴트(Bus Fault) 크래시 발생
- 시리얼 모니터에 백트레이스 주소, 레지스터 정보, Bus Fault 메시지 출력
- 크래시 발생 시점: 온도 센서 상태를 출력하는 루틴 실행 중

## 2. 문제 파악
- addr2line 및 디버그 심볼을 활용해 백트레이스 주소를 소스 코드 라인으로 매핑
- 주요 콜스택:
  - TemperatureService::printStatus() (src/application/TemperatureService.cpp:35)
  - TemperatureSensorManager::update() (src/domain/TemperatureSensorManager.cpp:22)
  - DallasTemperature 라이브러리 내부
  - UART/Serial 출력 루틴
- SensorStatus 구조체의 문자열 멤버(포인터) 및 센서 미연결/미초기화 영역에서의 접근 가능성 확인

## 3. 문제 원인
- 센서가 연결되지 않았거나, getAddress 실패 시 sensorsTable의 멤버가 미초기화 상태로 남아 있음
- printStatus에서 해당 멤버(특히 문자열 포인터) 접근 시 잘못된 메모리 접근(버스 폴트) 발생
- 라이브러리 내부에서 센서 연결 실패 시 예외 처리 미흡 가능성

## 4. 문제 해결
- TemperatureSensorManager::update()에서 모든 sensorsTable 인덱스를 항상 명확히 초기화(N/A 등)
- printStatus에서 각 상태 문자열이 nullptr일 경우 "N/A"로 안전하게 출력하도록 수정
- 센서가 0개이거나 연결이 불안정할 때도 크래시 없이 동작하도록 예외 처리 강화

## 5. 결과 및 교훈
- 수정 후 센서 미연결/미초기화 상황에서도 MCU가 크래시 없이 정상 동작함을 확인
- 임베디드 환경에서는 모든 포인터/버퍼/상태값의 유효성 보장 및 예외 처리가 필수적임을 재확인
- addr2line, 디버그 심볼, 백트레이스 등 진단 도구의 중요성 실전 경험으로 체득

DS18B20, OneWire, DallasTemperature 등 외부 라이브러리 사용
포인터, 배열, 구조체, 센서 연결 상태 등에서 robust하지 않은 코드가 있었음
센서 미연결, 포인터/구조체 미초기화, 잘못된 메모리 접근 등에서 버스 폴트 발생
특히, 센서 주소/상태/포인터를 제대로 체크하지 않고 접근하면 MCU가 즉시 크래시

robust하게 고치려면:
모든 포인터/구조체/센서 상태값을 명확히 초기화
nullptr, 미연결, 미초기화 상태에서 접근하지 않도록 예외처리
라이브러리 함수 리턴값 체크
print 등에서 nullptr 접근 방지