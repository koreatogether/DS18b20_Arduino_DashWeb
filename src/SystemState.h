#ifndef SYSTEM_STATE_H
#define SYSTEM_STATE_H

#include <Arduino.h>

/**
 * 시스템 상태 관리 클래스 (상태 기반 구조)
 * 전역 상태와 통계를 중앙 집중식으로 관리
 */
class SystemState {
private:
    // 시스템 상태
    unsigned long systemStartTime;
    int testCounter;
    bool systemInitialized;
    
    // 타이밍 관리
    unsigned long lastTestMessage;
    unsigned long lastHealthCheck;
    
    // 상수
    static const unsigned long TEST_INTERVAL = 2000;
    static const unsigned long HEALTH_CHECK_INTERVAL = 30000;

public:
    SystemState();
    
    // 시스템 초기화
    void initialize();
    bool isInitialized() const { return systemInitialized; }
    
    // 테스트 카운터 관리
    void incrementTestCounter() { testCounter++; }
    void resetTestCounter() { testCounter = 0; }
    int getTestCounter() const { return testCounter; }
    
    // 타이밍 관리
    bool isTimeForTestMessage();
    bool isTimeForHealthCheck();
    void updateTestMessageTime() { lastTestMessage = millis(); }
    void updateHealthCheckTime() { lastHealthCheck = millis(); }
    
    // 시스템 정보
    unsigned long getUptime() const { return millis() - systemStartTime; }
    bool getSystemInfo(char* output, int maxSize) const;
    
    // 상태 리셋
    void reset();
};

#endif