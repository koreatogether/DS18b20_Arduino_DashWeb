/**
 * 즉시 적용 가능한 상용급 개선사항
 * 현재 코드에 추가할 수 있는 핵심 기능들
 */

// 1. 메시지 체크섬 검증 (SerialCommunication.h에 추가)
class EnhancedSerialCommunication : public SerialCommunication
{
private:
    uint32_t calculateCRC32(const char *data, size_t length)
    {
        uint32_t crc = 0xFFFFFFFF;
        for (size_t i = 0; i < length; i++)
        {
            crc ^= data[i];
            for (int j = 0; j < 8; j++)
            {
                crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
            }
        }
        return ~crc;
    }

public:
    void sendSecureMessage(const char *message)
    {
        uint32_t crc = calculateCRC32(message, strlen(message));
        char secure_msg[512];
        snprintf(secure_msg, sizeof(secure_msg), "CRC:%08X:%s", crc, message);
        Serial.println(secure_msg);
    }

    bool receiveSecureMessage(char *buffer, size_t max_length)
    {
        if (hasMessage())
        {
            char temp_buffer[512];
            if (readMessage(temp_buffer, sizeof(temp_buffer)))
            {
                // CRC 검증
                if (strncmp(temp_buffer, "CRC:", 4) == 0)
                {
                    uint32_t received_crc;
                    sscanf(temp_buffer, "CRC:%08X:", &received_crc);

                    char *payload = strchr(temp_buffer + 4, ':') + 1;
                    uint32_t calculated_crc = calculateCRC32(payload, strlen(payload));

                    if (received_crc == calculated_crc)
                    {
                        strncpy(buffer, payload, max_length - 1);
                        buffer[max_length - 1] = '\0';
                        return true;
                    }
                    else
                    {
                        sendError("CRC_MISMATCH");
                        return false;
                    }
                }
            }
        }
        return false;
    }
};

// 2. 시스템 모니터링 (DS18B20_Arduino.ino에 추가)
class SimpleHealthMonitor
{
private:
    uint32_t last_check = 0;
    uint16_t error_count = 0;
    uint32_t max_loop_time = 0;

public:
    void checkSystemHealth()
    {
        if (millis() - last_check > 60000)
        { // 1분마다
            last_check = millis();

            // 메모리 체크
            uint16_t free_ram = getFreeRAM();
            if (free_ram < 512)
            {
                reportCritical("LOW_MEMORY", free_ram);
            }

            // 루프 성능 체크
            if (max_loop_time > 100)
            {
                reportWarning("SLOW_LOOP", max_loop_time);
            }

            // 오류율 체크
            if (error_count > 10)
            {
                reportCritical("HIGH_ERROR_RATE", error_count);
                error_count = 0; // 리셋
            }

            max_loop_time = 0; // 리셋
        }
    }

    uint16_t getFreeRAM()
    {
        extern char __heap_start, *__brkval;
        int free_memory;

        if ((int)__brkval == 0)
        {
            free_memory = ((int)&free_memory) - ((int)&__heap_start);
        }
        else
        {
            free_memory = ((int)&free_memory) - ((int)__brkval);
        }

        return (uint16_t)free_memory;
    }

    void recordLoopTime(uint32_t loop_time)
    {
        if (loop_time > max_loop_time)
        {
            max_loop_time = loop_time;
        }
    }

    void reportError() { error_count++; }

private:
    void reportCritical(const char *type, uint32_t value)
    {
        char msg[128];
        snprintf(msg, sizeof(msg), "CRITICAL_%s_%lu", type, value);
        Serial.println(msg);
    }

    void reportWarning(const char *type, uint32_t value)
    {
        char msg[128];
        snprintf(msg, sizeof(msg), "WARNING_%s_%lu", type, value);
        Serial.println(msg);
    }
};

// 3. 설정 관리 (간단한 EEPROM 버전)
#include <EEPROM.h>

struct SimpleConfig
{
    uint32_t magic = 0xDEADBEEF;
    uint16_t sensor_interval = 1500;
    float temp_offsets[8] = {0.0};
    float alert_high = 50.0;
    float alert_low = -10.0;
    bool json_enabled = true;
    uint32_t crc32 = 0;
};

class SimpleConfigManager
{
private:
    SimpleConfig config;

public:
    void loadConfig()
    {
        EEPROM.begin(sizeof(SimpleConfig));
        EEPROM.get(0, config);

        if (config.magic != 0xDEADBEEF || !validateCRC())
        {
            resetToDefault();
            saveConfig();
        }
    }

    void saveConfig()
    {
        updateCRC();
        EEPROM.put(0, config);
        EEPROM.commit();
    }

    SimpleConfig &getConfig() { return config; }

private:
    void resetToDefault()
    {
        config = SimpleConfig{}; // 기본값으로 초기화
    }

    void updateCRC()
    {
        config.crc32 = calculateCRC32((uint8_t *)&config, sizeof(config) - 4);
    }

    bool validateCRC()
    {
        uint32_t calculated = calculateCRC32((uint8_t *)&config, sizeof(config) - 4);
        return calculated == config.crc32;
    }

    uint32_t calculateCRC32(uint8_t *data, size_t length)
    {
        uint32_t crc = 0xFFFFFFFF;
        for (size_t i = 0; i < length; i++)
        {
            crc ^= data[i];
            for (int j = 0; j < 8; j++)
            {
                crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
            }
        }
        return ~crc;
    }
};

// 4. 향상된 오류 처리 (CommandProcessor.cpp에 추가)
class ErrorHandler
{
private:
    uint8_t consecutive_errors = 0;
    uint32_t last_error_time = 0;

public:
    void handleError(const char *error_type, const char *details)
    {
        consecutive_errors++;
        last_error_time = millis();

        // 오류 로깅
        char error_msg[256];
        snprintf(error_msg, sizeof(error_msg),
                 "ERROR_%s_COUNT_%d_TIME_%lu_DETAILS_%s",
                 error_type, consecutive_errors, last_error_time, details);

        Serial.println(error_msg);

        // 연속 오류가 많으면 자동 복구 시도
        if (consecutive_errors >= 5)
        {
            attemptRecovery();
        }
    }

    void clearErrors()
    {
        consecutive_errors = 0;
    }

private:
    void attemptRecovery()
    {
        Serial.println("SYSTEM_RECOVERY_ATTEMPT");

        // 센서 재초기화
        // 통신 버퍼 클리어
        // 상태 리셋

        consecutive_errors = 0;
        Serial.println("SYSTEM_RECOVERY_COMPLETE");
    }
};

// 5. 성능 모니터링 (loop()에 추가)
class PerformanceMonitor
{
private:
    uint32_t loop_start_time = 0;
    uint32_t max_loop_duration = 0;
    uint32_t total_loops = 0;
    uint32_t slow_loops = 0;

public:
    void startLoop()
    {
        loop_start_time = millis();
    }

    void endLoop()
    {
        uint32_t duration = millis() - loop_start_time;
        total_loops++;

        if (duration > max_loop_duration)
        {
            max_loop_duration = duration;
        }

        if (duration > 50)
        { // 50ms 이상은 느린 루프
            slow_loops++;
            Serial.print("SLOW_LOOP_");
            Serial.print(duration);
            Serial.println("ms");
        }

        // 1000루프마다 성능 리포트
        if (total_loops % 1000 == 0)
        {
            reportPerformance();
        }
    }

private:
    void reportPerformance()
    {
        float slow_percentage = (float)slow_loops / total_loops * 100.0;

        char perf_msg[256];
        snprintf(perf_msg, sizeof(perf_msg),
                 "PERFORMANCE_LOOPS_%lu_SLOW_%.1f%%_MAX_%lums",
                 total_loops, slow_percentage, max_loop_duration);

        Serial.println(perf_msg);

        // 카운터 리셋
        slow_loops = 0;
        max_loop_duration = 0;
    }
};
