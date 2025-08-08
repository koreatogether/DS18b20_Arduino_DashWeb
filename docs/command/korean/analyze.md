# /sc:analyze — 사용법 (한글)

원본: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/analyze.md
라이선스: MIT (SuperClaude Framework). 이 문서는 요약 번역본입니다. 자세한 내용은 원문을 참고하세요.

## 목적
코드베이스, 시스템, 산출물을 분석하여 문제점과 개선안을 도출합니다.

## 입력
- 대상 경로 또는 범위(파일/폴더/패턴)
- 선택적 집중: 성능 | 보안 | 품질 | 아키텍처

## 출력
- 분석 보고서(이슈, 위험, 패턴)
- 권장 조치 및 다음 단계

## 사전 조건
- 저장소/파일 읽기 권한
- 필요시 MCP 서버 활성화(문서/테스트/보안 등)

## 주요 플래그
- 페르소나: --persona-analyzer, --persona-security, --persona-performance
- 사고: --think | --think-hard | --ultrathink
- MCP: --seq(분석), --c7(문서), --no-mcp(비활성화)
- 안전/검증: --safe-mode, --validate

## 절차
1) 범위 지정: 분석 대상 디렉토리/파일 및 집중 영역 결정
2) 컨텍스트 구축: 주요 파일, 의존성, 설정 읽기
3) 분석: 아키텍처, 위험, 복잡도, 코드 스멜 등 평가
4) 검증: 이슈 재현, 증거 수집
5) 보고: 결과 요약 및 우선순위 조치 제안

## 예시
- 종합 분석: `/sc:analyze repo/ --persona-analyzer --think-hard --seq --validate`
- 보안 중심: `/sc:analyze api/ --focus security --persona-security --seq`
