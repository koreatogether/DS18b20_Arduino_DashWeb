/**
 * DS18B20_Arduino.ino
 * Arduino 메인 파일 - OOP/SOLID/DIP 구조 적용
 *
 * 의존성 주입과 인터페이스를 통한 느슨한 결합 구현
 * 각 컴포넌트는 250줄 이하로 분리되어 관리
 * gitgnore 12123123
 */

#include <Arduino.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include "SerialCommunication.h"
#include "JsonCommunication.h"
#include "SensorManager.h"
#include "CommandProcessor.h"
#include "SystemState.h"

// 하드웨어 설정
#define ONE_WIRE_BUS 2

// 하드웨어 객체
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
SerialCommunication serialComm;
JsonCommunication jsonComm; // JSON 통신 추가

// 시스템 컴포넌트 (DIP 적용)
SystemState systemState;
SensorManager sensorManager(&oneWire, &sensors, &serialComm);
CommandProcessor commandProcessor(&serialComm, &sensorManager, &systemState);

// JSON 통신 모드 플래그
bool useJsonMode = true;

// 함수 선언
void processJsonCommands();
void handleJsonCommand(const char *type, const char *content);
void sendJsonSystemStats();
void sendJsonSensorInfo();
void sendJsonTemperatureData();

void setup()
{
  // 115200 baud rate로 시리얼 통신 초기화 (Requirement 2.1)
  Serial.begin(115200);

  // 시리얼 통신이 준비될 때까지 대기 (최대 3초로 제한: 무한 대기 방지)
  // 일부 환경에서 호스트 측 포트 권한 문제나 지연으로 인해 무한 대기하는 문제를 예방
  unsigned long __serialWaitStart = millis();
  while (!Serial && (millis() - __serialWaitStart) < 3000)
  {
    delay(10);
  }

  // SerialCommunication 객체 초기화
  serialComm.begin();

  // JsonCommunication 객체 초기화
  jsonComm.begin(useJsonMode);

  // 시작 메시지 전송 (JSON/CSV 하이브리드)
  if (useJsonMode)
  {
    jsonComm.sendSystemMessage("Arduino started with JSON communication", "info");
    jsonComm.sendSystemMessage("Serial communication initialized at 115200 baud", "info");
  }
  else
  {
    serialComm.sendSystemMessage(F("ARDUINO_STARTED"));
    serialComm.sendSystemMessage(F("SERIAL_COMM_INITIALIZED_115200"));
  }

  // 시스템 상태 초기화
  systemState.initialize();

  // DS18B20 센서 초기화 (Task 2.1)
  sensorManager.initialize();

  if (useJsonMode)
  {
    jsonComm.sendStatus("ready", "All systems initialized");
  }
  else
  {
    serialComm.sendSystemMessage(F("READY_FOR_COMMUNICATION"));
  }

  // 초기화 완료 표시
  delay(100);
  serialComm.sendSystemMessage(F("SETUP_COMPLETE"));
}

void loop()
{
  // SerialCommunication 업데이트 (하트비트 등)
  serialComm.update();

  // JSON 명령 처리
  processJsonCommands();

  // JSON 테스트 데이터 전송 (5초마다)
  static unsigned long lastJsonTest = 0;
  if (millis() - lastJsonTest > 5000)
  {
    if (useJsonMode)
    {
      jsonComm.sendSensorData(1, 25.5, "ok");
      jsonComm.sendSystemMessage("Arduino JSON test message", "info");
    }
    lastJsonTest = millis();
  }

  // 센서 상태 모니터링 (Task 2.2)
  monitorSensorHealth();

  // 정기적인 테스트 메시지 전송
  sendTestMessages();

  // 수신된 메시지 처리 (Requirement 2.2)
  commandProcessor.processIncomingCommands();

  delay(10); // CPU 부하 감소
}

/**
 * 센서 데이터 전송 함수 (Task 2.3 개선)
 * 다중 센서 동시 처리 및 개별 측정 간격 지원
 */
void sendTestMessages()
{
  if (systemState.isTimeForTestMessage())
  {
    systemState.incrementTestCounter();
    systemState.updateTestMessageTime();

    // 1. 시스템 메시지
    char testMsg[64];
    snprintf(testMsg, sizeof(testMsg), "TEST_MESSAGE_%d", systemState.getTestCounter());
    serialComm.sendSystemMessage(testMsg);

    // 3. 상태 메시지 (5회마다)
    if (systemState.getTestCounter() % 5 == 0)
    {
      char statusMsg[128];
      snprintf(statusMsg, sizeof(statusMsg), "TEST_COUNTER_%d,SENSORS_%d",
               systemState.getTestCounter(), sensorManager.getSensorCount());
      serialComm.sendStatus(statusMsg);
    }

    // 4. 테스트 경고 메시지 (10회마다)
    if (systemState.getTestCounter() % 10 == 0)
    {
      float alertTemp = sensorManager.getSensorCount() > 0 ? sensors.getTempCByIndex(0) : 25.0;
      serialComm.sendAlert(1, "TEST_ALERT", alertTemp);
    }
  }

  // 2. 센서 데이터는 이제 별도로 처리 (Task 2.3)
  if (sensorManager.getSensorCount() > 0)
  {
    // 실제 센서 데이터 읽기 (다중 센서 동시 처리)
    sensorManager.updateSensorData();
  }
  else
  {
    // 가상 센서 데이터 (센서가 없을 때)
    static unsigned long lastVirtualSensor = 0;
    if (millis() - lastVirtualSensor >= 1000)
    {
      float testTemperature = 20.0 + (systemState.getTestCounter() % 10); // 20.0 ~ 29.0도
      serialComm.sendSensorData(1, testTemperature);
      lastVirtualSensor = millis();
    }
  }
}

/**
 * 센서 상태 모니터링 및 자동 복구 (Task 2.2)
 */
void monitorSensorHealth()
{
  if (systemState.isTimeForHealthCheck())
  {
    systemState.updateHealthCheckTime();
    sensorManager.monitorHealth();
  }
}

/**
 * JSON 명령 처리 함수
 */
void processJsonCommands()
{
  if (jsonComm.hasCommand())
  {
    char command[256];
    if (jsonComm.readCommand(command, sizeof(command)))
    {
      char type[32], content[256];
      if (jsonComm.parseJsonCommand(command, type, content, sizeof(type), sizeof(content)))
      {
        handleJsonCommand(type, content);
      }
      else
      {
        // JSON이 아닌 경우 기존 방식으로 처리
        if (strncmp(command, "JSON_MODE", 9) == 0)
        {
          useJsonMode = !useJsonMode;
          jsonComm.setJsonMode(useJsonMode);
          jsonComm.sendStatus("json_mode_changed", useJsonMode ? "enabled" : "disabled");
        }
      }
    }
  }
}

/**
 * JSON 명령 처리
 */
void handleJsonCommand(const char *type, const char *content)
{
  if (strcmp(type, "config") == 0)
  {
    if (strstr(content, "toggle_json_mode") != nullptr)
    {
      useJsonMode = !useJsonMode;
      jsonComm.setJsonMode(useJsonMode);
      jsonComm.sendStatus("json_mode_toggled", useJsonMode ? "JSON" : "CSV");
    }
  }
  else if (strcmp(type, "request") == 0)
  {
    if (strstr(content, "get_stats") != nullptr)
    {
      sendJsonSystemStats();
    }
    else if (strstr(content, "get_sensors") != nullptr)
    {
      sendJsonSensorInfo();
    }
    else if (strstr(content, "get_temperature") != nullptr)
    {
      sendJsonTemperatureData();
    }
  }
  else if (strcmp(type, "control") == 0)
  {
    if (strstr(content, "reset") != nullptr)
    {
      jsonComm.sendSystemMessage("System reset requested", "warning");
      delay(1000);
      // Arduino UNO R4 WiFi용 소프트웨어 리셋
      NVIC_SystemReset();
    }
  }
  else
  {
    char errorDetails[64];
    snprintf(errorDetails, sizeof(errorDetails), "Type: %s", type);
    jsonComm.sendError("Unknown command type", errorDetails);
  }
}

/**
 * JSON 형태로 시스템 통계 전송
 */
void sendJsonSystemStats()
{
  unsigned long uptime = millis();
  int sensorCount = sensorManager.getSensorCount();

  char statsMsg[128];
  snprintf(statsMsg, sizeof(statsMsg), "Uptime: %lus, Sensors: %d, Test counter: %d",
           uptime / 1000, sensorCount, systemState.getTestCounter());

  jsonComm.sendSystemMessage(statsMsg, "info");
}

/**
 * JSON 형태로 센서 정보 전송
 */
void sendJsonSensorInfo()
{
  int count = sensorManager.getSensorCount();
  char countMsg[64];
  snprintf(countMsg, sizeof(countMsg), "Total sensors detected: %d", count);
  jsonComm.sendSystemMessage(countMsg, "info");

  for (int i = 0; i < count; i++)
  {
    float temp = sensorManager.readSensorTemperature(i);
    const char *status = (temp != DEVICE_DISCONNECTED_C) ? "connected" : "disconnected";

    char sensorName[16];
    char statusDetails[64];
    snprintf(sensorName, sizeof(sensorName), "sensor_%d", i + 1);
    snprintf(statusDetails, sizeof(statusDetails), "%s, temp: %.2f°C", status, temp);
    jsonComm.sendStatus(sensorName, statusDetails);
  }
}

/**
 * JSON 형태로 온도 데이터 전송
 */
void sendJsonTemperatureData()
{
  int count = sensorManager.getSensorCount();

  for (int i = 0; i < count; i++)
  {
    float temperature = sensorManager.readSensorTemperature(i);

    if (temperature != DEVICE_DISCONNECTED_C)
    {
      // 정상 온도 데이터
      jsonComm.sendSensorData(i + 1, temperature, "ok");

      // 온도 경고 체크
      if (temperature > 30.0)
      {
        jsonComm.sendAlert(i + 1, "HIGH_TEMP", temperature, "warning");
      }
      else if (temperature < 5.0)
      {
        jsonComm.sendAlert(i + 1, "LOW_TEMP", temperature, "warning");
      }
    }
    else
    {
      // 센서 연결 오류
      jsonComm.sendSensorData(i + 1, -999.0, "disconnected");
      char errorDetails[32];
      snprintf(errorDetails, sizeof(errorDetails), "Sensor ID: %d", i + 1);
      jsonComm.sendError("Sensor disconnected", errorDetails);
    }
  }
}