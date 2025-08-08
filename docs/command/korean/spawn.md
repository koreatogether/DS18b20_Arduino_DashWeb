# /sc:spawn — 사용법 (한글)

원본: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/spawn.md
라이선스: MIT. 요약 번역본.

## 목적
하위 작업 생성 또는 전문 에이전트/페르소나에 위임

## 입력
- 상위 목표, 하위 작업 정의

## 출력
- 할당된 하위 작업, 조정 계획

## 주요 플래그
- --delegate, --persona-*, --seq, --no-mcp(격리 필요시)

## 절차
1) 목표를 독립적 하위 작업으로 분해
2) 작업별 적합 페르소나/서버 할당
3) 인터페이스/동기화점 정의, 충돌 방지
4) 결과 집계, 통합 검증

## 예시
- `/sc:spawn "dash + firmware" --delegate auto --seq`
