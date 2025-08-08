#ifndef COMMAND_PROCESSOR_H
#define COMMAND_PROCESSOR_H

#include "ICommandProcessor.h"
#include "ISensorManager.h"
#include "SystemState.h"
#include "SerialCommunication.h"

/**
 * 명령 처리 클래스 (OOP + SOLID 적용)
 * 명령 파싱, 검증, 실행 구현
 */
class CommandProcessor : public ICommandProcessor
{
private:
    // 의존성 주입 (DIP 적용)
    SerialCommunication *serialComm;
    ISensorManager *sensorManager;
    SystemState *systemState;

    // 명령 처리 상수
    static const int MAX_COMMAND_LENGTH = 64;
    static const int COMMAND_TIMEOUT = 5000;

    // 지원되는 명령어 목록
    static const char *SUPPORTED_COMMANDS[];
    static const int COMMAND_COUNT;

    // 내부 메서드
    void processBasicCommands(const char* command);
    void processSensorCommands(const char* command);
    void processSystemCommands(const char* command);
    void processSensorIntervalCommand(const char* command);
    void processSensorIdCommand(const char* command);
    void processSensorThresholdCommand(const char* command);
    bool parseIntervalCommand(const char* command, int &sensorId, unsigned long &interval) const;
    bool parseIdCommand(const char* command, int &sensorId, int &newId) const;
    bool getBaseCommand(const char* command, char* output, int maxSize) const;

public:
    CommandProcessor(SerialCommunication *comm, ISensorManager *sensorMgr, SystemState *state);
    ~CommandProcessor() = default;

    // ICommandProcessor 인터페이스 구현
    void processIncomingCommands() override;
    bool isValidCommand(const char* command) const override;
    bool validateParameters(const char* command) const override;
    void executeCommand(const char* command) override;
    void sendHelpMessage() const override;
    bool getSystemStatus(char* output, int maxSize) const override;
    void resetSystem() override;
};

#endif