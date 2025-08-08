/**
 * SerialCommunication.h
 * Processing과의 시리얼 통신 관리
 */

#ifndef SERIAL_COMMUNICATION_H
#define SERIAL_COMMUNICATION_H

#include <Arduino.h>

// 통신 프로토콜 정의 (Task 3.1 개선)
#define MSG_SENSOR_DATA "SENSOR_DATA"
#define MSG_SYSTEM "SYSTEM"
#define MSG_ALERT "ALERT"
#define MSG_STATUS "STATUS"
#define MSG_ACK "ACK"
#define MSG_ERROR "ERROR"
#define MSG_HEARTBEAT "HEARTBEAT"

// 메시지 타입 열거형
enum MessageType
{
  TYPE_SENSOR_DATA,
  TYPE_SYSTEM,
  TYPE_ALERT,
  TYPE_STATUS,
  TYPE_ACK,
  TYPE_ERROR,
  TYPE_HEARTBEAT
};

class SerialCommunication
{
private:
  static const int INPUT_BUFFER_SIZE = 256;
  char inputBuffer[INPUT_BUFFER_SIZE];
  int bufferIndex;
  unsigned long lastHeartbeat;

  void processMessage(const char *message);

public:
  SerialCommunication();

  void begin();
  void update();

  // 메시지 전송
  void sendSensorData(int sensorId, float temperature);
  void sendSystemMessage(const char *message);
  void sendSystemMessage(const __FlashStringHelper *message); // F() 매크로 지원
  void sendAlert(int sensorId, const char *alertType, float temperature);
  void sendStatus(const char *status);
  void sendAck(const char *command);
  void sendError(const char *error);

  // 메시지 수신 처리
  bool hasMessage();
  bool readMessage(char *output, int maxSize);

  // 버퍼 관리 (Task 3.2)
  void clearInputBuffer();
  int getBufferSize();
  bool isBufferOverflow();

  // 하트비트
  void sendHeartbeat();

  // 메시지 검증 및 통계 (Task 3.1)
  void printMessageStats();
  unsigned long getMessageCount(MessageType type);

  // 통신 상태 모니터링 (Task 3.3)
  void printConnectionStatus();
  bool isConnectionHealthy();
  void resetConnectionStats();

private:
  // 메모리 관리
  int getFreeMemory();

  // 메시지 통계 (Task 3.1)
  unsigned long messageCount[7]; // 각 메시지 타입별 카운트

  // 버퍼 관리 (Task 3.2)
  bool bufferOverflow;

  // 통신 상태 추적 (Task 3.3)
  unsigned long totalCommandsReceived;
  unsigned long totalErrorsGenerated;
  unsigned long lastCommandTime;

  // 메시지 포맷팅 헬퍼 (Task 3.1)
  void sendFormattedMessage(const char *msgType, const char *content);
  void sendFormattedMessage(const char *msgType, const __FlashStringHelper *content);
};

#endif // SERIAL_COMMUNICATION_H