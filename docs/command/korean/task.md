# /sc:task — 사용법 (한글)

원본: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/task.md
라이선스: MIT. 요약 번역본.

## 목적
명확한 완료 기준이 있는 구조화된 작업 생성/추적/완료

## 입력
- 제목, 설명, 범위, 완료 정의

## 출력
- 작업 계획, 체크리스트, 결과 요약

## 주요 플래그
- --persona-architect|qa, --validate, --seq

## 절차
1) 결과/완료 기준 정의
2) 체크리스트로 분해, 의존성 순서화
3) 실행, 증거 수집
4) 기준 충족/검증 시 완료 처리

## 예시
- `/sc:task "cppcheck fix" --persona-qa --validate`
