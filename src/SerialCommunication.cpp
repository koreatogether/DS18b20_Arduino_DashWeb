/**
 * SerialCommunication.cpp
 * Processing과의 시리얼 통신 구현
 */

#include "SerialCommunication.h"

SerialCommunication::SerialCommunication()
{
  memset(inputBuffer, 0, INPUT_BUFFER_SIZE);
  bufferIndex = 0;
  lastHeartbeat = 0;
  bufferOverflow = false;
  totalCommandsReceived = 0;
  totalErrorsGenerated = 0;
  lastCommandTime = 0;

  // 메시지 통계 초기화 (Task 3.1)
  for (int i = 0; i < 7; i++)
  {
    messageCount[i] = 0;
  }
}

void SerialCommunication::begin()
{
  bufferIndex = 0;
  lastHeartbeat = millis();
}

void SerialCommunication::update()
{
  // 하트비트 전송 (10초마다)
  if (millis() - lastHeartbeat > 10000)
  {
    sendHeartbeat();
    lastHeartbeat = millis();
  }
}

void SerialCommunication::sendSensorData(int sensorId, float temperature)
{
  char content[64];
  snprintf(content, sizeof(content), "%d,%.2f,%lu", sensorId, temperature, millis());
  sendFormattedMessage(MSG_SENSOR_DATA, content);
  messageCount[TYPE_SENSOR_DATA]++;
}

void SerialCommunication::sendSystemMessage(const char *message)
{
  sendFormattedMessage(MSG_SYSTEM, message);
  messageCount[TYPE_SYSTEM]++;
}

void SerialCommunication::sendSystemMessage(const __FlashStringHelper *message)
{
  sendFormattedMessage(MSG_SYSTEM, message);
  messageCount[TYPE_SYSTEM]++;
}

// 메시지 포맷팅 헬퍼 함수들 (Task 3.1)
void SerialCommunication::sendFormattedMessage(const char *msgType, const char *content)
{
  Serial.print(msgType);
  Serial.print(",");
  Serial.println(content);
}

void SerialCommunication::sendFormattedMessage(const char *msgType, const __FlashStringHelper *content)
{
  Serial.print(msgType);
  Serial.print(",");
  Serial.println(content);
}

void SerialCommunication::sendAlert(int sensorId, const char *alertType, float temperature)
{
  char content[96];
  snprintf(content, sizeof(content), "%d,%s,%.2f,%lu", sensorId, alertType, temperature, millis());
  sendFormattedMessage(MSG_ALERT, content);
  messageCount[TYPE_ALERT]++;
}

void SerialCommunication::sendStatus(const char *status)
{
  sendFormattedMessage(MSG_STATUS, status);
  messageCount[TYPE_STATUS]++;
}

void SerialCommunication::sendAck(const char *command)
{
  sendFormattedMessage(MSG_ACK, command);
  messageCount[TYPE_ACK]++;
}

void SerialCommunication::sendError(const char *error)
{
  sendFormattedMessage(MSG_ERROR, error);
  messageCount[TYPE_ERROR]++;
  totalErrorsGenerated++; // Task 3.3: 오류 통계 업데이트
}

bool SerialCommunication::hasMessage()
{
  while (Serial.available())
  {
    char c = Serial.read();

    if (c == '\n' || c == '\r')
    {
      if (bufferIndex > 0)
      {
        inputBuffer[bufferIndex] = '\0'; // null terminate
        return true;
      }
    }
    else if (bufferIndex < INPUT_BUFFER_SIZE - 1)
    {
      inputBuffer[bufferIndex++] = c;
    }
    else
    {
      // 버퍼 오버플로우 방지 (Task 3.2 개선)
      bufferOverflow = true;
      bufferIndex = 0;
      sendError("BUFFER_OVERFLOW_CLEARED");
      sendSystemMessage("INPUT_BUFFER_RESET_DUE_TO_OVERFLOW");
    }
  }
  return false;
}

bool SerialCommunication::readMessage(char *output, int maxSize)
{
  if (bufferIndex > 0)
  {
    int copyLen = min(bufferIndex, maxSize - 1);
    strncpy(output, inputBuffer, copyLen);
    output[copyLen] = '\0';
    bufferIndex = 0;
    return true;
  }
  return false;
}

void SerialCommunication::sendHeartbeat()
{
  const char *healthStatus = isConnectionHealthy() ? "HEALTHY" : "DEGRADED";
  char content[64];
  snprintf(content, sizeof(content), "%lu,%d,%s", millis(), getFreeMemory(), healthStatus);
  sendFormattedMessage(MSG_HEARTBEAT, content);
  messageCount[TYPE_HEARTBEAT]++;
}

// 메시지 통계 함수들 (Task 3.1)
void SerialCommunication::printMessageStats()
{
  char stats[128];
  snprintf(stats, sizeof(stats), "MSG_STATS_SENSOR:%lu,SYSTEM:%lu,ALERT:%lu,STATUS:%lu,ACK:%lu,ERROR:%lu,HEARTBEAT:%lu",
           messageCount[TYPE_SENSOR_DATA], messageCount[TYPE_SYSTEM], messageCount[TYPE_ALERT],
           messageCount[TYPE_STATUS], messageCount[TYPE_ACK], messageCount[TYPE_ERROR], messageCount[TYPE_HEARTBEAT]);
  sendSystemMessage(stats);
}

unsigned long SerialCommunication::getMessageCount(MessageType type)
{
  if (type >= 0 && type < 7)
  {
    return messageCount[type];
  }
  return 0;
}

// 버퍼 관리 함수들 (Task 3.2)
void SerialCommunication::clearInputBuffer()
{
  bufferIndex = 0;
  bufferOverflow = false;
}

int SerialCommunication::getBufferSize()
{
  return bufferIndex;
}

bool SerialCommunication::isBufferOverflow()
{
  return bufferOverflow;
}

// 통신 상태 모니터링 함수들 (Task 3.3)
void SerialCommunication::printConnectionStatus()
{
  unsigned long uptime = millis();
  float errorRate = totalCommandsReceived > 0 ? (float)totalErrorsGenerated / totalCommandsReceived * 100 : 0;

  char status[128];
  snprintf(status, sizeof(status), "CONNECTION_STATUS_UPTIME:%lu,COMMANDS:%lu,ERRORS:%lu,ERROR_RATE:%.1f%%,BUFFER_OK:%s",
           uptime, totalCommandsReceived, totalErrorsGenerated, errorRate, !bufferOverflow ? "YES" : "NO");
  sendSystemMessage(status);
}

bool SerialCommunication::isConnectionHealthy()
{
  // 연결 상태 판단 기준:
  // 1. 버퍼 오버플로우가 없음
  // 2. 오류율이 10% 미만
  // 3. 최근 30초 내에 명령을 받았음 (명령이 있었다면)

  if (bufferOverflow)
    return false;

  if (totalCommandsReceived > 10)
  {
    float errorRate = (float)totalErrorsGenerated / totalCommandsReceived;
    if (errorRate > 0.1)
      return false; // 10% 이상 오류율
  }

  // 명령을 받은 적이 있다면 최근 30초 내에 활동이 있어야 함
  if (totalCommandsReceived > 0 && lastCommandTime > 0)
  {
    if (millis() - lastCommandTime > 30000)
      return false;
  }

  return true;
}

void SerialCommunication::resetConnectionStats()
{
  totalCommandsReceived = 0;
  totalErrorsGenerated = 0;
  lastCommandTime = millis();
  bufferOverflow = false;

  for (int i = 0; i < 7; i++)
  {
    messageCount[i] = 0;
  }

  sendSystemMessage(F("CONNECTION_STATS_RESET"));
}

// 사용 가능한 메모리 확인 (디버깅용)
int SerialCommunication::getFreeMemory()
{
#ifdef ARDUINO_UNO_R4_WIFI
  // Arduino UNO R4 WiFi는 32KB RAM이므로 고정값 반환
  // 실제 메모리 측정은 복잡하므로 대략적인 값 사용
  return 30000; // 약 30KB 여유 (실제로는 더 정확한 측정 필요)
#else
  char top;
#ifdef __arm__
  extern char *sbrk(int incr);
  return &top - reinterpret_cast<char *>(sbrk(0));
#elif defined(CORE_TEENSY) || (ARDUINO > 103 && ARDUINO != 151)
  extern int __heap_start, *__brkval;
  return (int)&top - (__brkval == 0 ? (int)&__heap_start : (int)__brkval);
#else
  extern int __heap_start, *__brkval;
  return (int)&top - (__brkval == 0 ? (int)&__heap_start : (int)__brkval);
#endif
#endif
}