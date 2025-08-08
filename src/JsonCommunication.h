/**
 * JsonCommunication.h
 * Arduino에서 JSON 기반 시리얼 통신 지원 (ArduinoJson 사용)
 */

#ifndef JSON_COMMUNICATION_H
#define JSON_COMMUNICATION_H

#include <Arduino.h>
#include <ArduinoJson.h>

class JsonCommunication {
private:
  static const int BUFFER_SIZE = 256;
  static const int JSON_DOC_SIZE = 512;
  
  char inputBuffer[BUFFER_SIZE];
  int bufferIndex;
  bool jsonMode;
  
  // ArduinoJson 문서 객체
  StaticJsonDocument<JSON_DOC_SIZE> jsonDoc;
  
public:
  JsonCommunication();
  
  void begin(bool enableJsonMode = true);
  void setJsonMode(bool enabled);
  bool isJsonMode();
  
  // JSON 메시지 전송 (ArduinoJson 사용)
  void sendSensorData(int sensorId, float temperature, const char* status = "ok");
  void sendAlert(int sensorId, const char* alertType, float temperature, const char* severity = "warning");
  void sendSystemMessage(const char* message, const char* level = "info");
  void sendHeartbeat(unsigned long uptime, int freeMemory, const char* health = "healthy");
  void sendStatus(const char* status, const char* details = "");
  void sendError(const char* error, const char* details = "");
  
  // 명령 수신 처리 (ArduinoJson 사용)
  bool hasCommand();
  bool readCommand(char* output, int maxSize);
  bool parseJsonCommand(const char* jsonStr, char* type, char* content, int maxTypeSize, int maxContentSize);
  
  // 하위 호환성 (기존 CSV 형태)
  void sendCsvMessage(const char* msgType, const char* content);
};

#endif // JSON_COMMUNICATION_H