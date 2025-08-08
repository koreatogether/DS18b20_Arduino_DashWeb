# /sc:troubleshoot — 사용법 (한글)

원본: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/troubleshoot.md
라이선스: MIT. 요약 번역본.

## 목적
문제를 체계적으로 조사/해결

## 입력
- 오류 로그, 재현 단계, 환경 정보

## 출력
- 근본 원인 분석, 수정, 검증

## 주요 플래그
- --persona-analyzer, --think, --seq, --validate, --introspect

## 절차
1) 재현, 최소 실패 케이스 격리
2) 가설 수립, 증거 수집
3) 최소 변경으로 수정
4) 검증, 회귀 테스트 추가

## 예시
- `/sc:troubleshoot "serial COM4 timeout" --persona-analyzer --seq --validate`
