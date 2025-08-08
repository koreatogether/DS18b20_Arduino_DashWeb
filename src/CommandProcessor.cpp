#include "CommandProcessor.h"
#include "SensorManager.h"

// 지원되는 명령어 목록
const char *CommandProcessor::SUPPORTED_COMMANDS[] = {
    "PING",
    "STATUS",
    "RESET",
    "SCAN_SENSORS",
    "GET_SENSORS",
    "RESET_SENSORS",
    "SET_INTERVAL",
    "SET_ID",
    "SET_THRESHOLD",
    "GET_INTERVALS",
    "GET_MSG_STATS",
    "GET_CONN_STATUS",
    "RESET_CONN_STATS",
    "ECHO",
    "HELP"};

const int CommandProcessor::COMMAND_COUNT = sizeof(SUPPORTED_COMMANDS) / sizeof(SUPPORTED_COMMANDS[0]);

CommandProcessor::CommandProcessor(SerialCommunication *comm, ISensorManager *sensorMgr, SystemState *state)
    : serialComm(comm), sensorManager(sensorMgr), systemState(state)
{
}

void CommandProcessor::processIncomingCommands()
{
    if (serialComm->hasMessage())
    {
        char message[MAX_COMMAND_LENGTH];
        if (serialComm->readMessage(message, sizeof(message)))
        {
            // 메시지 trim (?�뒤 공백 ?�거)
            char *start = message;
            while (*start == ' ' || *start == '\t')
                start++;

            char *end = start + strlen(start) - 1;
            while (end > start && (*end == ' ' || *end == '\t' || *end == '\r' || *end == '\n'))
            {
                *end = '\0';
                end--;
            }

            if (strlen(start) > 0)
            {
                char receivedMsg[MAX_COMMAND_LENGTH + 16];
                snprintf(receivedMsg, sizeof(receivedMsg), "RECEIVED: %s", start);
                serialComm->sendSystemMessage(receivedMsg);

                if (!isValidCommand(start))
                {
                    char errorMsg[MAX_COMMAND_LENGTH + 32];
                    snprintf(errorMsg, sizeof(errorMsg), "INVALID_COMMAND: %s", start);
                    serialComm->sendError(errorMsg);
                    serialComm->sendSystemMessage("USE_HELP_FOR_AVAILABLE_COMMANDS");
                    return;
                }

                if (!validateParameters(start))
                {
                    char errorMsg[MAX_COMMAND_LENGTH + 32];
                    snprintf(errorMsg, sizeof(errorMsg), "INVALID_PARAMETERS: %s", start);
                    serialComm->sendError(errorMsg);
                    return;
                }

                unsigned long commandStartTime = millis();
                executeCommand(start);

                unsigned long processingTime = millis() - commandStartTime;
                if (processingTime > 100)
                {
                    char timeMsg[64];
                    snprintf(timeMsg, sizeof(timeMsg), "COMMAND_PROCESSING_TIME: %lums", processingTime);
                    serialComm->sendSystemMessage(timeMsg);
                }
            }
        }
    }
}

bool CommandProcessor::isValidCommand(const char *command) const
{
    int len = strlen(command);
    if (len == 0 || len > MAX_COMMAND_LENGTH)
    {
        return false;
    }

    char baseCommand[MAX_COMMAND_LENGTH];
    if (!getBaseCommand(command, baseCommand, sizeof(baseCommand)))
    {
        return false;
    }

    for (int i = 0; i < COMMAND_COUNT; i++)
    {
        if (strcmp(baseCommand, SUPPORTED_COMMANDS[i]) == 0)
        {
            return true;
        }
    }

    return false;
}

bool CommandProcessor::validateParameters(const char *command) const
{
    if (strncmp(command, "SET_INTERVAL,", 13) == 0)
    {
        int sensorId;
        unsigned long interval;
        return parseIntervalCommand(command, sensorId, interval);
    }
    else if (strncmp(command, "SET_ID,", 7) == 0)
    {
        // SET_ID,oldId,newId ?�식 검�?
        const char *comma1 = strchr(command, ',');
        if (!comma1)
            return false;

        const char *comma2 = strchr(comma1 + 1, ',');
        if (!comma2)
            return false;

        int oldId = atoi(comma1 + 1);
        int newId = atoi(comma2 + 1);
        return (oldId >= 1 && oldId <= 8 && newId >= 1 && newId <= 8);
    }
    else if (strncmp(command, "SET_THRESHOLD,", 14) == 0)
    {
        // SET_THRESHOLD,sensorId,upperLimit,lowerLimit ?�식 검�?
        int commaCount = 0;
        for (int i = 0; command[i] != '\0'; i++)
        {
            if (command[i] == ',')
                commaCount++;
        }
        return commaCount == 3; // SET_THRESHOLD + 3�??�라미터
    }

    return true;
}

void CommandProcessor::executeCommand(const char *command)
{
    if (strcmp(command, "PING") == 0 || strcmp(command, "STATUS") == 0 ||
        strcmp(command, "RESET") == 0 || strcmp(command, "HELP") == 0)
    {
        processBasicCommands(command);
    }
    else if (strcmp(command, "SCAN_SENSORS") == 0 || strcmp(command, "GET_SENSORS") == 0 ||
             strcmp(command, "RESET_SENSORS") == 0 || strcmp(command, "GET_INTERVALS") == 0)
    {
        processSensorCommands(command);
    }
    else if (strcmp(command, "GET_MSG_STATS") == 0 || strcmp(command, "GET_CONN_STATUS") == 0 ||
             strcmp(command, "RESET_CONN_STATS") == 0)
    {
        processSystemCommands(command);
    }
    else if (strncmp(command, "SET_INTERVAL,", 13) == 0)
    {
        processSensorIntervalCommand(command);
    }
    else if (strncmp(command, "SET_ID,", 7) == 0)
    {
        processSensorIdCommand(command);
    }
    else if (strncmp(command, "SET_THRESHOLD,", 14) == 0)
    {
        processSensorThresholdCommand(command);
    }
    else if (strncmp(command, "ECHO,", 5) == 0)
    {
        const char *echoMessage = command + 5;
        char responseMsg[MAX_COMMAND_LENGTH + 32];
        snprintf(responseMsg, sizeof(responseMsg), "ECHO_RESPONSE: %s", echoMessage);
        serialComm->sendSystemMessage(responseMsg);
        serialComm->sendAck("ECHO_COMPLETED");
    }
}

void CommandProcessor::processBasicCommands(const char *command)
{
    if (strcmp(command, "PING") == 0)
    {
        serialComm->sendAck("PONG");
    }
    else if (strcmp(command, "STATUS") == 0)
    {
        char systemStatus[128];
        char statusMsg[256];

        if (getSystemStatus(systemStatus, sizeof(systemStatus)))
        {
            snprintf(statusMsg, sizeof(statusMsg), "%s,SENSORS_%d",
                     systemStatus, sensorManager->getSensorCount());
            serialComm->sendStatus(statusMsg);
        }
    }
    else if (strcmp(command, "RESET") == 0)
    {
        resetSystem();
        serialComm->sendAck("COUNTER_RESET");
        serialComm->sendSystemMessage("TEST_COUNTER_RESET_TO_ZERO");
    }
    else if (strcmp(command, "HELP") == 0)
    {
        sendHelpMessage();
        serialComm->sendAck("HELP_SENT");
    }
}

void CommandProcessor::processSensorCommands(const char *command)
{
    if (strcmp(command, "SCAN_SENSORS") == 0)
    {
        sensorManager->scanSensors();
        serialComm->sendAck("SENSOR_SCAN_COMPLETED");
    }
    else if (strcmp(command, "GET_SENSORS") == 0)
    {
        // ?�결???�서 개수 먼�? ?�송
        char countMsg[64];
        snprintf(countMsg, sizeof(countMsg), "CONNECTED_SENSOR_COUNT_%d", sensorManager->getSensorCount());
        serialComm->sendSystemMessage(countMsg);

        // ?�제 ?�결???�서?�의 ID�?기�??�로 ?�보 ?�송
        SensorManager *sensorMgr = static_cast<SensorManager *>(sensorManager);
        for (int i = 0; i < sensorManager->getSensorCount(); i++)
        {
            // ?�서 ?�덱??기�??�로 ?�보 가?�오�?
            char info[128];
            if (sensorMgr->getSensorInfoByIndex(i, info, sizeof(info)))
            {
                serialComm->sendSystemMessage(info);
            }
        }
        serialComm->sendAck("SENSOR_INFO_SENT");
    }
    else if (strcmp(command, "RESET_SENSORS") == 0)
    {
        sensorManager->resetSensorErrors();
        serialComm->sendAck("SENSOR_ERRORS_RESET");
        serialComm->sendSystemMessage("ALL_SENSOR_ERRORS_CLEARED");
    }
    else if (strcmp(command, "GET_INTERVALS") == 0)
    {
        char intervals[512];
        if (sensorManager->getAllSensorIntervals(intervals, sizeof(intervals)))
        {
            // Split by newlines and send each line
            char *line = strtok(intervals, "\n");
            while (line != nullptr)
            {
                serialComm->sendSystemMessage(line);
                line = strtok(nullptr, "\n");
            }
        }
        serialComm->sendAck("INTERVALS_INFO_SENT");
    }
}

void CommandProcessor::processSystemCommands(const char *command)
{
    if (strcmp(command, "GET_MSG_STATS") == 0)
    {
        serialComm->printMessageStats();
        serialComm->sendAck("MESSAGE_STATS_SENT");
    }
    else if (strcmp(command, "GET_CONN_STATUS") == 0)
    {
        serialComm->printConnectionStatus();
        serialComm->sendAck("CONNECTION_STATUS_SENT");
    }
    else if (strcmp(command, "RESET_CONN_STATS") == 0)
    {
        serialComm->resetConnectionStats();
        serialComm->sendAck("CONNECTION_STATS_RESET");
    }
}

void CommandProcessor::processSensorIntervalCommand(const char *command)
{
    int sensorId;
    unsigned long interval;

    if (!parseIntervalCommand(command, sensorId, interval))
    {
        serialComm->sendError("INVALID_INTERVAL_COMMAND_FORMAT");
        return;
    }

    if (sensorId < 1 || sensorId > sensorManager->getSensorCount())
    {
        char errorMsg[64];
        snprintf(errorMsg, sizeof(errorMsg), "INVALID_SENSOR_ID_%d", sensorId);
        serialComm->sendError(errorMsg);
        return;
    }

    if (sensorManager->setSensorInterval(sensorId, interval))
    {
        char ackMsg[128];
        char sysMsg[128];
        snprintf(ackMsg, sizeof(ackMsg), "SENSOR_%d_INTERVAL_SET_%lums", sensorId, interval);
        snprintf(sysMsg, sizeof(sysMsg), "SENSOR_%d_NEW_INTERVAL_%lums", sensorId, interval);
        serialComm->sendAck(ackMsg);
        serialComm->sendSystemMessage(sysMsg);
    }
    else
    {
        char errorMsg[64];
        snprintf(errorMsg, sizeof(errorMsg), "FAILED_TO_SET_INTERVAL_FOR_SENSOR_%d", sensorId);
        serialComm->sendError(errorMsg);
    }
}

void CommandProcessor::sendHelpMessage() const
{
    serialComm->sendSystemMessage(F("AVAILABLE_COMMANDS:"));
    serialComm->sendSystemMessage(F("PING - Test connection"));
    serialComm->sendSystemMessage(F("STATUS - Get system status"));
    serialComm->sendSystemMessage(F("RESET - Reset test counter"));
    serialComm->sendSystemMessage(F("SCAN_SENSORS - Rescan DS18B20 sensors"));
    serialComm->sendSystemMessage(F("GET_SENSORS - Get sensor information"));
    serialComm->sendSystemMessage(F("RESET_SENSORS - Reset sensor errors"));
    serialComm->sendSystemMessage(F("SET_INTERVAL,ID,MS - Set sensor interval"));
    serialComm->sendSystemMessage(F("SET_ID,OLDID,NEWID - Change sensor ID"));
    serialComm->sendSystemMessage(F("SET_THRESHOLD,ID,UPPER,LOWER - Set temperature thresholds"));
    serialComm->sendSystemMessage(F("GET_INTERVALS - Get all sensor intervals"));
    serialComm->sendSystemMessage(F("GET_MSG_STATS - Get message statistics"));
    serialComm->sendSystemMessage(F("GET_CONN_STATUS - Get connection status"));
    serialComm->sendSystemMessage(F("RESET_CONN_STATS - Reset connection stats"));
    serialComm->sendSystemMessage(F("ECHO,TEXT - Echo back text"));
    serialComm->sendSystemMessage(F("HELP - Show this help"));
}

bool CommandProcessor::getSystemStatus(char *output, int maxSize) const
{
    return systemState->getSystemInfo(output, maxSize);
}

void CommandProcessor::resetSystem()
{
    systemState->resetTestCounter();
}

// Private methods
bool CommandProcessor::parseIntervalCommand(const char *command, int &sensorId, unsigned long &interval) const
{
    const char *firstComma = strchr(command, ',');
    if (!firstComma)
        return false;

    const char *secondComma = strchr(firstComma + 1, ',');
    if (!secondComma)
        return false;

    sensorId = 0;
    interval = 0;

    // Parse sensor ID
    for (const char *p = firstComma + 1; p < secondComma; p++)
    {
        if (*p >= '0' && *p <= '9')
        {
            sensorId = sensorId * 10 + (*p - '0');
        }
    }

    // Parse interval
    for (const char *p = secondComma + 1; *p != '\0'; p++)
    {
        if (*p >= '0' && *p <= '9')
        {
            interval = interval * 10 + (*p - '0');
        }
    }

    return (sensorId > 0 && interval > 0);
}

bool CommandProcessor::getBaseCommand(const char *command, char *output, int maxSize) const
{
    const char *commaPos = strchr(command, ',');
    int len;

    if (commaPos != nullptr)
    {
        len = commaPos - command;
    }
    else
    {
        len = strlen(command);
    }

    if (len >= maxSize)
    {
        return false;
    }

    strncpy(output, command, len);
    output[len] = '\0';
    return true;
}

/**
 * SET_ID 명령 처리: SET_ID,sensorId,newId
 */
void CommandProcessor::processSensorIdCommand(const char *command)
{
    int sensorId;
    int newId;

    if (!parseIdCommand(command, sensorId, newId))
    {
        serialComm->sendError("INVALID_ID_COMMAND_FORMAT");
        return;
    }

    // ?�서 ID ?�효??검??
    if (sensorId < 1 || sensorId > sensorManager->getSensorCount())
    {
        char errorMsg[64];
        snprintf(errorMsg, sizeof(errorMsg), "INVALID_SENSOR_ID_%d", sensorId);
        serialComm->sendError(errorMsg);
        return;
    }

    // ??ID ?�효??검??
    if (newId < 1 || newId > 8)
    {
        char errorMsg[64];
        snprintf(errorMsg, sizeof(errorMsg), "INVALID_NEW_ID_RANGE_%d_VALID_1_TO_8", newId);
        serialComm->sendError(errorMsg);
        return;
    }

    // ?�버�?출력 추�?
    char debugMsg[128];
    snprintf(debugMsg, sizeof(debugMsg), "DEBUG_CALLING_CHANGE_SENSOR_ID_INDEX_%d_TO_%d", sensorId - 1, newId);
    serialComm->sendSystemMessage(debugMsg);

    // SensorManager�??�해 ID 변�?(?�서 ?�덱?�는 ID-1)
    SensorManager *sensorMgr = static_cast<SensorManager *>(sensorManager);
    if (sensorMgr->changeSensorId(sensorId - 1, newId))
    {
        serialComm->sendAck("SENSOR_ID_CHANGED_SUCCESS");
        char successMsg[64];
        snprintf(successMsg, sizeof(successMsg), "SENSOR_%d_ID_CHANGED_TO_%d", sensorId, newId);
        serialComm->sendSystemMessage(successMsg);
    }
    else
    {
        serialComm->sendError("SENSOR_ID_CHANGE_FAILED");
    }
}

/**
 * SET_THRESHOLD 명령 처리: SET_THRESHOLD,sensorId,upperLimit,lowerLimit
 */
void CommandProcessor::processSensorThresholdCommand(const char *command)
{
    const char *comma1 = strchr(command, ',');
    if (!comma1)
    {
        serialComm->sendError("INVALID_SET_THRESHOLD_FORMAT_USE_SET_THRESHOLD_ID_UPPER_LOWER");
        return;
    }

    const char *comma2 = strchr(comma1 + 1, ',');
    if (!comma2)
    {
        serialComm->sendError("INVALID_SET_THRESHOLD_FORMAT_USE_SET_THRESHOLD_ID_UPPER_LOWER");
        return;
    }

    const char *comma3 = strchr(comma2 + 1, ',');
    if (!comma3)
    {
        serialComm->sendError("INVALID_SET_THRESHOLD_FORMAT_USE_SET_THRESHOLD_ID_UPPER_LOWER");
        return;
    }

    int sensorId = atoi(comma1 + 1);
    float upperLimit = atof(comma2 + 1);
    float lowerLimit = atof(comma3 + 1);

    // ?�서 ID �??�계�??�효??검??
    if (sensorId >= 1 && sensorId <= 8 && upperLimit > lowerLimit)
    {
        // ?�계�??�정 (?�제 구현?� ?�서 매니?�???�임)
        char ackMsg[64];
        char sysMsg[128];
        snprintf(ackMsg, sizeof(ackMsg), "THRESHOLD_SET_SENSOR_%d", sensorId);
        snprintf(sysMsg, sizeof(sysMsg), "THRESHOLD_UPDATED,SENSOR_%d,UPPER_%.2f,LOWER_%.2f",
                 sensorId, upperLimit, lowerLimit);
        serialComm->sendAck(ackMsg);
        serialComm->sendSystemMessage(sysMsg);
    }
    else
    {
        serialComm->sendError("INVALID_THRESHOLD_PARAMETERS");
    }
}

bool CommandProcessor::parseIdCommand(const char *command, int &sensorId, int &newId) const
{
    // SET_ID,?�서ID,?�ID ?�식 ?�싱
    const char *firstComma = strchr(command, ',');
    if (!firstComma)
        return false;

    const char *secondComma = strchr(firstComma + 1, ',');
    if (!secondComma)
        return false;

    sensorId = 0;
    newId = 0;

    // ?�서 ID ?�싱
    for (const char *p = firstComma + 1; p < secondComma; p++)
    {
        if (*p >= '0' && *p <= '9')
        {
            sensorId = sensorId * 10 + (*p - '0');
        }
    }

    // ??ID ?�싱
    for (const char *p = secondComma + 1; *p != '\0'; p++)
    {
        if (*p >= '0' && *p <= '9')
        {
            newId = newId * 10 + (*p - '0');
        }
    }

    return (sensorId > 0 && newId > 0);
}
