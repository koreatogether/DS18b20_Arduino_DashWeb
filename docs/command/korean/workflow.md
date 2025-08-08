# /sc:workflow — 사용법 (한글)

원본: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/workflow.md
라이선스: MIT. 요약 번역본.

## 목적
다단계 플로우(웨이브, 루프, 페르소나/MCP 조정 등) 오케스트레이션

## 입력
- 목표, 단계, 검증 게이트

## 출력
- 각 단계별 증거가 포함된 실행 계획

## 주요 플래그
- --wave-mode, --loop, --delegate, --all-mcp | --no-mcp, --validate

## 절차
1) 단계/품질 게이트 정의
2) 페르소나/서버 조정
3) 단계별 실행, 증거 수집
4) 리뷰/반복/최종화

## 예시
- `/sc:workflow "migrate project to prod" --wave-mode auto --validate`
