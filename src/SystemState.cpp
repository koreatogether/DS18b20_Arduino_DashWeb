#include "SystemState.h"

SystemState::SystemState() 
    : systemStartTime(0), testCounter(0), systemInitialized(false),
      lastTestMessage(0), lastHealthCheck(0) {
}

void SystemState::initialize() {
    systemStartTime = millis();
    testCounter = 0;
    lastTestMessage = 0;
    lastHealthCheck = 0;
    systemInitialized = true;
}

bool SystemState::isTimeForTestMessage() {
    return (millis() - lastTestMessage >= TEST_INTERVAL);
}

bool SystemState::isTimeForHealthCheck() {
    return (millis() - lastHealthCheck >= HEALTH_CHECK_INTERVAL);
}

bool SystemState::getSystemInfo(char* output, int maxSize) const {
    int result = snprintf(output, maxSize, "COUNTER_%d,UPTIME_%lu,INITIALIZED_%s",
                         testCounter, getUptime(), systemInitialized ? "TRUE" : "FALSE");
    return result > 0 && result < maxSize;
}

void SystemState::reset() {
    testCounter = 0;
    lastTestMessage = 0;
    lastHealthCheck = 0;
}