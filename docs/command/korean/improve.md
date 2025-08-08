# /sc:improve — 사용법 (한글)

원본: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/improve.md
라이선스: MIT. 요약 번역본.

## 목적
품질(가독성, 성능, 보안, 문서 등) 점진적 개선

## 입력
- 개선 대상, 집중 영역

## 출력
- 점진적 개선 내역, 검증 결과

## 주요 플래그
- --persona-refactorer | --persona-performance | --persona-security, --seq, --validate, --loop

## 절차
1) 개선 기회/지표 파악
2) 작은 안전한 변경 적용, 측정
3) 검증, 회귀 발생시 되돌림
4) 목표 달성까지 반복

## 예시
- `/sc:improve src/ --focus quality --persona-refactorer --validate --loop`
