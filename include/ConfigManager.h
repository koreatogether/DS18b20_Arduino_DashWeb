/**
 * ConfigManager.h
 * EEPROM 기반 설정 관리 시스템
 */

#ifndef CONFIG_MANAGER_H
#define CONFIG_MANAGER_H

#include <Arduino.h>
#include <EEPROM.h>

class ConfigManager
{
public:
    struct SystemConfig
    {
        // 헤더 정보
        uint32_t magic_number = 0xDEADBEEF;
        uint16_t version = 1;
        uint16_t config_size = sizeof(SystemConfig);

        // 시스템 설정
        char device_name[32] = "DS18B20_Monitor";
        char firmware_version[16] = "1.0.0";
        uint32_t device_serial = 0;

        // 네트워크 설정
        char wifi_ssid[32] = "";
        char wifi_password[64] = "";
        char server_url[128] = "";
        uint16_t server_port = 443;
        bool wifi_enabled = false;

        // 센서 설정
        uint16_t sensor_scan_interval_ms = 1500;
        float temperature_offset[8] = {0.0}; // 센서별 캘리브레이션
        float alert_high_temp = 50.0;
        float alert_low_temp = -10.0;
        bool auto_calibration = true;

        // 통신 설정
        uint32_t heartbeat_interval_ms = 30000;
        uint8_t max_retry_count = 3;
        uint16_t comm_timeout_ms = 5000;
        bool json_mode_enabled = true;

        // 보안 설정
        char api_key[64] = "";
        bool encryption_enabled = false;
        uint32_t session_timeout_ms = 3600000; // 1시간

        // 로깅 설정
        bool logging_enabled = true;
        uint8_t log_level = 2;                // 0=Error, 1=Warning, 2=Info, 3=Debug
        uint32_t log_rotation_size = 1048576; // 1MB

        // 진단 설정
        bool health_monitoring = true;
        uint32_t health_check_interval = 10000;
        bool auto_recovery = true;

        // 무결성 검사
        uint32_t crc32 = 0;
    };

private:
    SystemConfig config;
    bool config_loaded = false;
    bool config_dirty = false;

    static const uint16_t EEPROM_CONFIG_ADDR = 0;
    static const uint16_t EEPROM_SIZE = 4096; // 4KB EEPROM

public:
    ConfigManager();

    // 설정 로드/저장
    bool loadConfig();
    bool saveConfig();
    bool validateConfig();
    void resetToDefault();

    // 설정 접근자
    SystemConfig &getConfig() { return config; }
    const SystemConfig &getConfig() const { return config; }

    // 개별 설정 메서드
    void setDeviceName(const char *name);
    void setWiFiCredentials(const char *ssid, const char *password);
    void setServerEndpoint(const char *url, uint16_t port);
    void setSensorInterval(uint16_t interval_ms);
    void setTemperatureOffset(uint8_t sensor_id, float offset);
    void setAlertTemperatures(float high, float low);
    void setAPIKey(const char *key);

    // 설정 유효성 검사
    bool isConfigValid();
    bool isWiFiConfigured();
    bool isServerConfigured();
    bool isSecurityConfigured();

    // 설정 백업/복원
    bool backupConfig();
    bool restoreConfig();
    void exportConfigJSON(char *json_buffer, size_t buffer_size);
    bool importConfigJSON(const char *json_config);

    // 설정 변경 추적
    void markDirty() { config_dirty = true; }
    bool isDirty() const { return config_dirty; }
    void autoSave(); // 주기적 자동 저장

    // 진단
    void printConfig();
    void getConfigSummary(char *summary, size_t max_length);

private:
    uint32_t calculateCRC32(const void *data, size_t length);
    void updateCRC32();
    bool verifyCRC32();
    void initializeEEPROM();
    void clearEEPROM();
};

#endif // CONFIG_MANAGER_H
