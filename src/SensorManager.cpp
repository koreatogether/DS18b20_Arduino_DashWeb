#include "SensorManager.h"

// 상수 정의
const float SensorManager::MIN_VALID_TEMP = -55.0;
const float SensorManager::MAX_VALID_TEMP = 125.0;
const float SensorManager::MAX_TEMP_CHANGE = 10.0;

SensorManager::SensorManager(OneWire *ow, DallasTemperature *ds, SerialCommunication *comm)
    : oneWire(ow), sensors(ds), serialComm(comm), sensorCount(0)
{
}

void SensorManager::initialize()
{
    sensors->begin();
    serialComm->sendSystemMessage(F("DS18B20_SENSORS_INITIALIZED"));
    scanSensors();
}

void SensorManager::scanSensors()
{
    serialComm->sendSystemMessage("SCANNING_DS18B20_SENSORS");

    int deviceCount = sensors->getDeviceCount();
    char deviceMsg[32];
    snprintf(deviceMsg, sizeof(deviceMsg), "FOUND_%d_SENSORS", deviceCount);
    serialComm->sendSystemMessage(deviceMsg);

    if (deviceCount == 0)
    {
        serialComm->sendSystemMessage("NO_SENSORS_FOUND");
        sensorCount = 0;
        return;
    }

    sensorCount = min(deviceCount, MAX_SENSORS);

    for (int i = 0; i < sensorCount; i++)
    {
        if (sensors->getAddress(sensorList[i].address, i))
        {
            sensorList[i].id = i + 1;
            sensorList[i].isConnected = true;
            sensorList[i].lastTemperature = 0.0;
            sensorList[i].lastReadTime = 0;
            sensorList[i].errorCount = 0;
            sensorList[i].hasValidReading = false;
            sensorList[i].measurementInterval = DEFAULT_MEASUREMENT_INTERVAL;
            sensorList[i].nextMeasurementTime = millis();

            char addressStr[24];
            addressToString(sensorList[i].address, addressStr);
            char sensorMsg[64];
            snprintf(sensorMsg, sizeof(sensorMsg), "SENSOR_%d_ADDRESS_%s", sensorList[i].id, addressStr);
            serialComm->sendSystemMessage(sensorMsg);

            sensors->setResolution(sensorList[i].address, 12);
        }
        else
        {
            sensorList[i].isConnected = false;
            sensorList[i].errorCount = MAX_ERROR_COUNT;
            char errorMsg[64];
            snprintf(errorMsg, sizeof(errorMsg), "FAILED_TO_GET_ADDRESS_FOR_SENSOR_%d", i);
            serialComm->sendError(errorMsg);
        }
    }

    char completeMsg[48];
    snprintf(completeMsg, sizeof(completeMsg), "SENSOR_SCAN_COMPLETE_%d_SENSORS_READY", sensorCount);
    serialComm->sendSystemMessage(completeMsg);
}

void SensorManager::updateSensorData()
{
    if (sensorCount == 0)
        return;

    static unsigned long lastGlobalRequest = 0;
    unsigned long currentTime = millis();

    if (currentTime - lastGlobalRequest >= 1000)
    {
        requestAllSensorsTemperature();
        lastGlobalRequest = currentTime;
        delay(750); // 12-bit resolution conversion time
    }

    readSensorsByInterval();
}

float SensorManager::readSensorTemperature(int sensorIndex)
{
    if (sensorIndex < 0 || sensorIndex >= sensorCount)
    {
        return DEVICE_DISCONNECTED_C;
    }

    if (!sensorList[sensorIndex].isConnected)
    {
        return DEVICE_DISCONNECTED_C;
    }

    float temperature = sensors->getTempC(sensorList[sensorIndex].address);
    unsigned long currentTime = millis();

    if (temperature == DEVICE_DISCONNECTED_C)
    {
        sensorList[sensorIndex].errorCount++;
        char errorMsg[64];
        snprintf(errorMsg, sizeof(errorMsg), "SENSOR_%d_READ_ERROR_%d", sensorList[sensorIndex].id, sensorList[sensorIndex].errorCount);
        serialComm->sendError(errorMsg);

        if (sensorList[sensorIndex].errorCount >= MAX_ERROR_COUNT)
        {
            sensorList[sensorIndex].isConnected = false;
            char disconnectMsg[64];
            snprintf(disconnectMsg, sizeof(disconnectMsg), "SENSOR_%d_DISCONNECTED_AFTER_%d_ERRORS", sensorList[sensorIndex].id, MAX_ERROR_COUNT);
            serialComm->sendError(disconnectMsg);
        }
        return DEVICE_DISCONNECTED_C;
    }

    if (temperature < MIN_VALID_TEMP || temperature > MAX_VALID_TEMP)
    {
        sensorList[sensorIndex].errorCount++;
        char rangeMsg[64];
        snprintf(rangeMsg, sizeof(rangeMsg), "SENSOR_%d_TEMP_OUT_OF_RANGE_%.1f", sensorList[sensorIndex].id, temperature);
        serialComm->sendError(rangeMsg);
        return DEVICE_DISCONNECTED_C;
    }

    if (sensorList[sensorIndex].hasValidReading)
    {
        float tempChange = abs(temperature - sensorList[sensorIndex].lastTemperature);
        if (tempChange > MAX_TEMP_CHANGE)
        {
            sensorList[sensorIndex].errorCount++;
            char changeMsg[64];
            snprintf(changeMsg, sizeof(changeMsg), "SENSOR_%d_SUDDEN_CHANGE_%.1fC", sensorList[sensorIndex].id, tempChange);
            serialComm->sendError(changeMsg);
            if (sensorList[sensorIndex].errorCount < MAX_ERROR_COUNT)
            {
                return sensorList[sensorIndex].lastTemperature;
            }
        }
    }

    sensorList[sensorIndex].errorCount = 0;
    sensorList[sensorIndex].lastTemperature = temperature;
    sensorList[sensorIndex].lastReadTime = currentTime;
    sensorList[sensorIndex].hasValidReading = true;

    return temperature;
}

void SensorManager::monitorHealth()
{
    int connectedCount = 0;
    int disconnectedCount = 0;

    for (int i = 0; i < sensorCount; i++)
    {
        if (sensorList[i].isConnected)
        {
            connectedCount++;
        }
        else
        {
            disconnectedCount++;

            if (sensorList[i].errorCount >= MAX_ERROR_COUNT)
            {
                float testTemp = sensors->getTempC(sensorList[i].address);
                if (testTemp != DEVICE_DISCONNECTED_C && testTemp >= MIN_VALID_TEMP && testTemp <= MAX_VALID_TEMP)
                {
                    sensorList[i].isConnected = true;
                    sensorList[i].errorCount = 0;
                    char reconnectMsg[32];
                    snprintf(reconnectMsg, sizeof(reconnectMsg), "SENSOR_%d_RECONNECTED", sensorList[i].id);
                    serialComm->sendSystemMessage(reconnectMsg);
                }
            }
        }
    }

    char healthMsg[64];
    snprintf(healthMsg, sizeof(healthMsg), "HEALTH_CHECK_CONNECTED_%d_DISCONNECTED_%d", connectedCount, disconnectedCount);
    serialComm->sendSystemMessage(healthMsg);
}

bool SensorManager::isSensorConnected(int sensorId) const
{
    int index = findSensorIndexById(sensorId);
    return (index != -1) ? sensorList[index].isConnected : false;
}

bool SensorManager::setSensorInterval(int sensorId, unsigned long interval)
{
    if (interval < MIN_MEASUREMENT_INTERVAL || interval > MAX_MEASUREMENT_INTERVAL)
    {
        return false;
    }

    int index = findSensorIndexById(sensorId);
    if (index == -1)
        return false;

    sensorList[index].measurementInterval = interval;
    sensorList[index].nextMeasurementTime = millis() + interval;
    return true;
}

unsigned long SensorManager::getSensorInterval(int sensorId) const
{
    int index = findSensorIndexById(sensorId);
    return (index != -1) ? sensorList[index].measurementInterval : 0;
}

void SensorManager::resetSensorErrors()
{
    for (int i = 0; i < sensorCount; i++)
    {
        sensorList[i].errorCount = 0;
        sensorList[i].isConnected = true;
    }
}

bool SensorManager::getSensorInfo(int sensorId, char *output, int maxSize) const
{
    int index = findSensorIndexById(sensorId);
    if (index == -1)
        return false;

    return getSensorInfoByIndex(index, output, maxSize);
}

bool SensorManager::getSensorInfoByIndex(int index, char *output, int maxSize) const
{
    if (index < 0 || index >= sensorCount || !sensorList[index].isConnected)
    {
        return false;
    }

    char addressStr[24];
    addressToString(sensorList[index].address, addressStr);
    const char *statusStr = sensorList[index].isConnected ? "CONNECTED" : "DISCONNECTED";
    char tempStr[8];

    if (sensorList[index].hasValidReading)
    {
        dtostrf(sensorList[index].lastTemperature, 4, 2, tempStr);
    }
    else
    {
        strcpy(tempStr, "NO_DATA");
    }

    int result = snprintf(output, maxSize, "SENSOR_INFO_%d_%s_%s_ERRORS_%d_LAST_%s",
                          sensorList[index].id, addressStr, statusStr,
                          sensorList[index].errorCount, tempStr);

    return result > 0 && result < maxSize;
}

bool SensorManager::getAllSensorIntervals(char *output, int maxSize) const
{
    int pos = 0;
    for (int i = 0; i < sensorCount; i++)
    {
        if (i > 0 && pos < maxSize - 1)
        {
            output[pos++] = '\n';
        }

        int written = snprintf(output + pos, maxSize - pos,
                               "SENSOR_%d_INTERVAL_%lums",
                               sensorList[i].id, sensorList[i].measurementInterval);

        if (written < 0 || pos + written >= maxSize)
        {
            return false;
        }
        pos += written;
    }

    if (pos < maxSize)
    {
        output[pos] = '\0';
        return true;
    }
    return false;
}

// Private methods
void SensorManager::addressToString(const uint8_t *address, char *buffer) const
{
    char *ptr = buffer;
    for (int i = 0; i < 8; i++)
    {
        if (address[i] < 16)
            *ptr++ = '0';
        sprintf(ptr, "%X", address[i]);
        ptr += strlen(ptr);
        if (i < 7)
            *ptr++ = ':';
    }
    *ptr = '\0';
}

void SensorManager::requestAllSensorsTemperature()
{
    if (sensorCount == 0)
        return;
    sensors->requestTemperatures();
}

void SensorManager::readSensorsByInterval()
{
    unsigned long currentTime = millis();

    for (int i = 0; i < sensorCount; i++)
    {
        if (currentTime >= sensorList[i].nextMeasurementTime)
        {
            if (sensorList[i].isConnected || sensorList[i].errorCount < MAX_ERROR_COUNT)
            {
                float temperature = readSensorTemperature(i);

                if (temperature != DEVICE_DISCONNECTED_C)
                {
                    serialComm->sendSensorData(sensorList[i].id, temperature);
                }

                sensorList[i].nextMeasurementTime = currentTime + sensorList[i].measurementInterval;
            }
        }
    }
}

int SensorManager::findSensorIndexById(int sensorId) const
{
    for (int i = 0; i < sensorCount; i++)
    {
        if (sensorList[i].id == sensorId)
        {
            return i;
        }
    }
    return -1;
}

// DS18B20 Scratchpad의 TH 영역(byte[2])에 사용자 데이터 저장
bool SensorManager::setUserData(const uint8_t *deviceAddress, uint8_t userData)
{
    // Scratchpad 읽기
    uint8_t scratchPad[9];
    if (!sensors->readScratchPad(deviceAddress, scratchPad))
    {
        serialComm->sendError("FAILED_TO_READ_SCRATCHPAD");
        return false;
    }

    // TH(byte[2]) 영역에 사용자 데이터 저장
    // TL(byte[3])은 하한 임계값으로 사용하므로 TH만 사용
    scratchPad[2] = userData; // TH 영역에 센서 ID 저장

    // Scratchpad에 쓰기 (전체 scratchpad 배열 사용)
    sensors->writeScratchPad(deviceAddress, scratchPad);

    // 30ms 대기 (메모리 안정화)
    delay(30);

    // EEPROM에 영구 저장 (saveScratchPad 사용)
    if (!sensors->saveScratchPad(deviceAddress))
    {
        serialComm->sendError("FAILED_TO_SAVE_SCRATCHPAD");
        return false;
    }

    // 추가 30ms 대기 (EEPROM 쓰기 완료)
    delay(30);

    return true;
}

// DS18B20 Scratchpad의 TH 영역(byte[2])에서 사용자 데이터 읽기
uint8_t SensorManager::getUserData(const uint8_t *deviceAddress)
{
    uint8_t scratchPad[9];
    if (!sensors->readScratchPad(deviceAddress, scratchPad))
    {
        serialComm->sendError("FAILED_TO_READ_SCRATCHPAD_FOR_USERDATA");
        return 0;
    }

    // TH 영역(byte[2])에서 사용자 데이터 반환
    return scratchPad[2];
}

// 센서 ID 변경 및 검증
bool SensorManager::verifySensorIdChange(int sensorIndex, int newId)
{
    if (sensorIndex < 0 || sensorIndex >= sensorCount)
    {
        char errorMsg[64];
        snprintf(errorMsg, sizeof(errorMsg), "INVALID_SENSOR_INDEX_%d", sensorIndex);
        serialComm->sendError(errorMsg);
        return false;
    }

    // 센서 주소 가져오기
    uint8_t *deviceAddress = sensorList[sensorIndex].address;

    // 새 ID를 센서 EEPROM에 저장
    if (!setUserData(deviceAddress, (uint8_t)newId))
    {
        char errorMsg[64];
        snprintf(errorMsg, sizeof(errorMsg), "FAILED_TO_SET_SENSOR_ID_%d", newId);
        serialComm->sendError(errorMsg);
        return false;
    }

    // 저장된 값 다시 읽어서 검증
    uint8_t storedId = getUserData(deviceAddress);
    if (storedId != (uint8_t)newId)
    {
        char errorMsg[128];
        snprintf(errorMsg, sizeof(errorMsg), "ID_VERIFICATION_FAILED_EXPECTED_%d_GOT_%d", newId, storedId);
        serialComm->sendError(errorMsg);
        return false;
    }

    // 메모리 상의 센서 정보 업데이트
    sensorList[sensorIndex].id = newId;

    char successMsg[128];
    snprintf(successMsg, sizeof(successMsg), "SENSOR_ID_CHANGED_SUCCESS_INDEX_%d_NEW_ID_%d", sensorIndex, newId);
    serialComm->sendSystemMessage(successMsg);
    return true;
}

// 센서 ID 변경 메인 함수
bool SensorManager::changeSensorId(int sensorIndex, int newId)
{
    char debugMsg[128];
    snprintf(debugMsg, sizeof(debugMsg), "DEBUG_CHANGE_SENSOR_ID_CALLED_INDEX_%d_TO_%d", sensorIndex, newId);
    serialComm->sendSystemMessage(debugMsg);

    char countMsg[64];
    snprintf(countMsg, sizeof(countMsg), "DEBUG_SENSOR_COUNT_%d", sensorCount);
    serialComm->sendSystemMessage(countMsg);

    // ID 유효성 검사
    if (newId < 1 || newId > 8)
    {
        char errorMsg[64];
        snprintf(errorMsg, sizeof(errorMsg), "INVALID_ID_RANGE_%d_VALID_1_TO_8", newId);
        serialComm->sendError(errorMsg);
        return false;
    }

    // 센서 인덱스 유효성 검사
    if (sensorIndex < 0 || sensorIndex >= sensorCount)
    {
        char errorMsg[128];
        snprintf(errorMsg, sizeof(errorMsg), "INVALID_SENSOR_INDEX_%d_MAX_%d", sensorIndex, sensorCount - 1);
        serialComm->sendError(errorMsg);
        return false;
    }

    // 센서 연결 상태 확인
    char statusMsg[128];
    snprintf(statusMsg, sizeof(statusMsg), "DEBUG_SENSOR_CONNECTION_STATUS_%d", sensorList[sensorIndex].isConnected);
    serialComm->sendSystemMessage(statusMsg);

    if (!sensorList[sensorIndex].isConnected)
    {
        char errorMsg[64];
        snprintf(errorMsg, sizeof(errorMsg), "SENSOR_NOT_CONNECTED_INDEX_%d", sensorIndex);
        serialComm->sendError(errorMsg);
        return false;
    }

    // 현재 센서 ID 출력
    char currentIdMsg[128];
    snprintf(currentIdMsg, sizeof(currentIdMsg), "DEBUG_CURRENT_SENSOR_ID_%d", sensorList[sensorIndex].id);
    serialComm->sendSystemMessage(currentIdMsg);

    // ID 변경 및 검증 수행
    serialComm->sendSystemMessage("DEBUG_CALLING_VERIFY_SENSOR_ID_CHANGE");
    if (verifySensorIdChange(sensorIndex, newId))
    {
        // 성공 시 Processing에 알림
        char successMsg[128];
        snprintf(successMsg, sizeof(successMsg), "ID_CHANGE_COMPLETED_SENSOR_%d_NEW_ID_%d", sensorIndex + 1, newId);
        serialComm->sendSystemMessage(successMsg);
        return true;
    }
    else
    {
        // 실패 시 Processing에 알림
        char errorMsg[64];
        snprintf(errorMsg, sizeof(errorMsg), "ID_CHANGE_FAILED_SENSOR_%d", sensorIndex + 1);
        serialComm->sendError(errorMsg);
        return false;
    }
}