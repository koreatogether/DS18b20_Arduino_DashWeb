# /sc:build — 사용법 (한글)

원본: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/build.md
라이선스: MIT. 요약 번역본.

## 목적
계획 또는 명세에 따라 기능/컴포넌트/서비스/문서 등을 빌드합니다.

## 입력
- 대상 모듈 또는 경로
- 빌드 유형: 기능 | 컴포넌트 | 서비스 | 문서 사이트

## 출력
- 새 파일/업데이트 파일, 빌드 로그

## 사전 조건
- 명확한 요구사항 또는 명세
- 툴체인 준비(패키지 매니저, 컴파일러 등)

## 주요 플래그
- 페르소나: --persona-frontend | --persona-backend | --persona-architect
- MCP: --magic(UI), --seq(분석), --c7(문서)
- 안전: --safe-mode, --validate

## 절차
1) 요구사항/범위 확인, 의존성 목록 작성
2) 파일 생성/업데이트, 저장소 규칙 준수
3) 빌드 검증, 간단 셀프체크
4) 결과 및 다음 단계 요약

## 예시
- UI: `/sc:build ui/button/ --persona-frontend --magic --c7`
- 백엔드: `/sc:build api/session/ --persona-backend --seq --validate`
