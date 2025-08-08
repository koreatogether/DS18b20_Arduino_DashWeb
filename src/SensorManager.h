#ifndef SENSOR_MANAGER_H
#define SENSOR_MANAGER_H

#include <OneWire.h>
#include <DallasTemperature.h>
#include "ISensorManager.h"
#include "SerialCommunication.h"

/**
 * DS18B20 센서 관리 클래스 (OOP + SOLID 적용)
 * 센서 스캔, 데이터 읽기, 상태 관리 구현
 */
class SensorManager : public ISensorManager
{
private:
    // 센서 정보 구조체
    struct SensorInfo
    {
        uint8_t address[8];
        int id;
        bool isConnected;
        float lastTemperature;
        unsigned long lastReadTime;
        int errorCount;
        bool hasValidReading;
        unsigned long measurementInterval;
        unsigned long nextMeasurementTime;
    };

    // 하드웨어 객체
    OneWire *oneWire;
    DallasTemperature *sensors;
    SerialCommunication *serialComm;

    // 센서 데이터
    SensorInfo sensorList[8]; // MAX_SENSORS
    int sensorCount;

    // 상수
    static const int MAX_SENSORS = 8;
    static const float MIN_VALID_TEMP;
    static const float MAX_VALID_TEMP;
    static const float MAX_TEMP_CHANGE;
    static const int MAX_ERROR_COUNT = 3;
    static const unsigned long DEFAULT_MEASUREMENT_INTERVAL = 1000;
    static const unsigned long MIN_MEASUREMENT_INTERVAL = 500;
    static const unsigned long MAX_MEASUREMENT_INTERVAL = 60000;

    // 내부 메서드
    void addressToString(const uint8_t *address, char *buffer) const;
    void requestAllSensorsTemperature();
    void readSensorsByInterval();
    int findSensorIndexById(int sensorId) const;

    // DS18B20 사용자 데이터 저장 기능 (Scratchpad 활용)
    bool setUserData(const uint8_t *deviceAddress, uint8_t userData);
    uint8_t getUserData(const uint8_t *deviceAddress);
    bool verifySensorIdChange(int sensorIndex, int newId);

public:
    SensorManager(OneWire *ow, DallasTemperature *ds, SerialCommunication *comm);
    ~SensorManager() = default;

    // ISensorManager 인터페이스 구현
    void initialize() override;
    void scanSensors() override;
    void updateSensorData() override;
    float readSensorTemperature(int sensorIndex) override;
    void monitorHealth() override;
    int getSensorCount() const override { return sensorCount; }
    bool isSensorConnected(int sensorId) const override;
    bool setSensorInterval(int sensorId, unsigned long interval) override;
    unsigned long getSensorInterval(int sensorId) const override;
    void resetSensorErrors() override;
    bool getSensorInfo(int sensorId, char *output, int maxSize) const override;
    bool getAllSensorIntervals(char *output, int maxSize) const override;

    // 센서 ID 변경 기능
    bool changeSensorId(int sensorIndex, int newId);

    // 인덱스 기반 센서 정보 조회
    bool getSensorInfoByIndex(int index, char *output, int maxSize) const;
};

#endif