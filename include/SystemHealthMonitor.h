/**
 * SystemHealthMonitor.h
 * 시스템 상태 모니터링 및 자동 복구
 */

#ifndef SYSTEM_HEALTH_MONITOR_H
#define SYSTEM_HEALTH_MONITOR_H

#include <Arduino.h>

class SystemHealthMonitor
{
public:
    struct HealthMetrics
    {
        uint32_t uptime_seconds;
        uint16_t free_ram_bytes;
        uint16_t stack_usage_percent;
        uint8_t cpu_usage_percent;
        float internal_temperature;
        uint8_t sensor_error_rate;
        uint8_t comm_error_rate;
        uint32_t total_messages_sent;
        uint32_t total_messages_failed;
        uint32_t watchdog_resets;
        uint32_t soft_resets;
    };

    enum SystemState
    {
        HEALTHY = 0,
        WARNING = 1,
        CRITICAL = 2,
        EMERGENCY = 3
    };

    enum ErrorType
    {
        NONE = 0,
        SENSOR_TIMEOUT = 1,
        COMM_FAILURE = 2,
        MEMORY_LOW = 3,
        STACK_OVERFLOW = 4,
        WATCHDOG_TIMEOUT = 5,
        TEMPERATURE_HIGH = 6
    };

private:
    HealthMetrics current_metrics = {0};
    SystemState current_state = HEALTHY;
    uint32_t last_health_check = 0;
    uint32_t health_check_interval = 10000; // 10초

    // 오류 카운터
    uint16_t error_counts[7] = {0}; // ErrorType별 카운터
    uint32_t last_error_time[7] = {0};

    // 임계값 설정
    static const uint16_t MIN_FREE_RAM = 512;    // 최소 여유 RAM (bytes)
    static const uint8_t MAX_STACK_USAGE = 80;   // 최대 스택 사용률 (%)
    static const uint8_t MAX_CPU_USAGE = 90;     // 최대 CPU 사용률 (%)
    static const float MAX_INTERNAL_TEMP = 70.0; // 최대 내부 온도 (°C)
    static const uint8_t MAX_ERROR_RATE = 10;    // 최대 오류율 (%)

    // 자동 복구 설정
    static const uint8_t MAX_ERRORS_BEFORE_RESET = 5;
    static const uint32_t ERROR_RESET_WINDOW = 300000; // 5분

public:
    SystemHealthMonitor();

    // 주기적 헬스 체크
    void performHealthCheck();
    void updateMetrics();

    // 메트릭 수집
    uint16_t getFreeRAM();
    uint16_t getStackUsage();
    uint8_t getCPUUsage();
    float getInternalTemperature();

    // 상태 관리
    SystemState getCurrentState();
    void reportError(ErrorType error);
    void clearError(ErrorType error);

    // 자동 복구
    void attemptRecovery();
    void performSoftReset();
    void performEmergencyShutdown();

    // 헬스 리포트
    void sendHealthReport();
    void sendCriticalAlert(const char *message);
    void logHealthEvent(const char *event, SystemState state);

    // 설정
    void setHealthCheckInterval(uint32_t interval_ms);
    void setErrorThreshold(ErrorType error, uint8_t threshold);

    // 유틸리티
    const char *getStateString(SystemState state);
    const char *getErrorString(ErrorType error);

private:
    void calculateErrorRates();
    bool isErrorRateHigh(ErrorType error);
    void updateSystemState();
    void handleCriticalState();
    void resetErrorCounters();
};

#endif // SYSTEM_HEALTH_MONITOR_H
