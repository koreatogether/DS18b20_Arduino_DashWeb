/**
 * JsonCommunication.cpp
 * Arduino에서 JSON 기반 시리얼 통신 구현 (ArduinoJson 사용)
 */

#include "JsonCommunication.h"

JsonCommunication::JsonCommunication() {
  memset(inputBuffer, 0, BUFFER_SIZE);
  bufferIndex = 0;
  jsonMode = true;
}

void JsonCommunication::begin(bool enableJsonMode) {
  memset(inputBuffer, 0, BUFFER_SIZE);
  bufferIndex = 0;
  jsonMode = enableJsonMode;
  
  if (jsonMode) {
    sendSystemMessage("JSON communication initialized", "info");
  } else {
    Serial.println("SYSTEM,CSV communication initialized");
  }
}

void JsonCommunication::setJsonMode(bool enabled) {
  jsonMode = enabled;
  const char* mode = enabled ? "JSON" : "CSV";
  char message[64];
  snprintf(message, sizeof(message), "Communication mode changed to %s", mode);
  sendSystemMessage(message, "info");
}

bool JsonCommunication::isJsonMode() {
  return jsonMode;
}

// ArduinoJson을 사용하므로 별도의 헬퍼 함수 불필요

void JsonCommunication::sendSensorData(int sensorId, float temperature, const char* status) {
  if (jsonMode) {
    jsonDoc.clear();
    jsonDoc["type"] = "sensor";
    jsonDoc["timestamp"] = millis();
    jsonDoc["id"] = sensorId;
    jsonDoc["temp"] = round(temperature * 100) / 100.0;  // 소수점 2자리
    jsonDoc["status"] = status;
    
    serializeJson(jsonDoc, Serial);
    Serial.println();
  } else {
    // 하위 호환성: CSV 형태
    char csvContent[64];
    snprintf(csvContent, sizeof(csvContent), "%d,%.2f,%lu", sensorId, temperature, millis());
    sendCsvMessage("SENSOR_DATA", csvContent);
  }
}

void JsonCommunication::sendAlert(int sensorId, const char* alertType, float temperature, const char* severity) {
  if (jsonMode) {
    jsonDoc.clear();
    jsonDoc["type"] = "alert";
    jsonDoc["timestamp"] = millis();
    jsonDoc["id"] = sensorId;
    jsonDoc["alert"] = alertType;
    jsonDoc["temp"] = round(temperature * 100) / 100.0;
    jsonDoc["severity"] = severity;
    
    serializeJson(jsonDoc, Serial);
    Serial.println();
  } else {
    // 하위 호환성: CSV 형태
    char csvContent[64];
    snprintf(csvContent, sizeof(csvContent), "%d,%s,%.2f,%lu", sensorId, alertType, temperature, millis());
    sendCsvMessage("ALERT", csvContent);
  }
}

void JsonCommunication::sendSystemMessage(const char* message, const char* level) {
  if (jsonMode) {
    jsonDoc.clear();
    jsonDoc["type"] = "system";
    jsonDoc["timestamp"] = millis();
    jsonDoc["msg"] = message;
    jsonDoc["level"] = level;
    
    serializeJson(jsonDoc, Serial);
    Serial.println();
  } else {
    // 하위 호환성: CSV 형태
    sendCsvMessage("SYSTEM", message);
  }
}

void JsonCommunication::sendHeartbeat(unsigned long uptime, int freeMemory, const char* health) {
  if (jsonMode) {
    jsonDoc.clear();
    jsonDoc["type"] = "heartbeat";
    jsonDoc["timestamp"] = millis();
    jsonDoc["uptime"] = uptime;
    jsonDoc["memory"] = freeMemory;
    jsonDoc["health"] = health;
    
    serializeJson(jsonDoc, Serial);
    Serial.println();
  } else {
    // 하위 호환성: CSV 형태
    char csvContent[64];
    snprintf(csvContent, sizeof(csvContent), "%lu,%d,%s", uptime, freeMemory, health);
    sendCsvMessage("HEARTBEAT", csvContent);
  }
}

void JsonCommunication::sendStatus(const char* status, const char* details) {
  if (jsonMode) {
    jsonDoc.clear();
    jsonDoc["type"] = "status";
    jsonDoc["timestamp"] = millis();
    jsonDoc["status"] = status;
    
    if (strlen(details) > 0) {
      jsonDoc["details"] = details;
    }
    
    serializeJson(jsonDoc, Serial);
    Serial.println();
  } else {
    // 하위 호환성: CSV 형태
    if (strlen(details) > 0) {
      char csvContent[128];
      snprintf(csvContent, sizeof(csvContent), "%s,%s", status, details);
      sendCsvMessage("STATUS", csvContent);
    } else {
      sendCsvMessage("STATUS", status);
    }
  }
}

void JsonCommunication::sendError(const char* error, const char* details) {
  if (jsonMode) {
    jsonDoc.clear();
    jsonDoc["type"] = "error";
    jsonDoc["timestamp"] = millis();
    jsonDoc["error"] = error;
    
    if (strlen(details) > 0) {
      jsonDoc["details"] = details;
    }
    
    serializeJson(jsonDoc, Serial);
    Serial.println();
  } else {
    // 하위 호환성: CSV 형태
    if (strlen(details) > 0) {
      char csvContent[128];
      snprintf(csvContent, sizeof(csvContent), "%s,%s", error, details);
      sendCsvMessage("ERROR", csvContent);
    } else {
      sendCsvMessage("ERROR", error);
    }
  }
}

bool JsonCommunication::hasCommand() {
  while (Serial.available()) {
    char c = Serial.read();
    
    if (c == '\n' || c == '\r') {
      if (bufferIndex > 0) {
        inputBuffer[bufferIndex] = '\0';  // null terminate
        return true;
      }
    } else if (c >= 32 && c <= 126) {  // printable characters only
      if (bufferIndex < BUFFER_SIZE - 1) {
        inputBuffer[bufferIndex++] = c;
      } else {
        // 버퍼 오버플로우 방지
        sendError("BUFFER_OVERFLOW", "Input buffer cleared");
        memset(inputBuffer, 0, BUFFER_SIZE);
        bufferIndex = 0;
      }
    }
  }
  return false;
}

bool JsonCommunication::readCommand(char* output, int maxSize) {
  if (bufferIndex > 0 && maxSize > bufferIndex) {
    strncpy(output, inputBuffer, bufferIndex);
    output[bufferIndex] = '\0';
    
    // 버퍼 초기화
    memset(inputBuffer, 0, BUFFER_SIZE);
    bufferIndex = 0;
    return true;
  }
  return false;
}

bool JsonCommunication::parseJsonCommand(const char* jsonStr, char* type, char* content, int maxTypeSize, int maxContentSize) {
  // ArduinoJson을 사용한 안전한 파싱
  jsonDoc.clear();
  
  DeserializationError error = deserializeJson(jsonDoc, jsonStr);
  if (error) {
    return false;
  }
  
  // type 필드 추출
  const char* typeValue = jsonDoc["type"];
  if (!typeValue) {
    return false;
  }
  
  if (strlen(typeValue) >= maxTypeSize) {
    return false;
  }
  
  strcpy(type, typeValue);
  
  // 전체 내용을 content로 복사
  if (strlen(jsonStr) >= maxContentSize) {
    return false;
  }
  
  strcpy(content, jsonStr);
  
  return true;
}

void JsonCommunication::sendCsvMessage(const char* msgType, const char* content) {
  Serial.print(msgType);
  Serial.print(",");
  Serial.println(content);
}