# /sc:document — 사용법 (한글)

원본: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/document.md
라이선스: MIT. 요약 번역본.

## 목적
문서(README, 가이드, API 문서 등) 작성/업데이트

## 입력
- 대상 독자, 목적, 범위

## 출력
- 마크다운 등 문서 파일

## 주요 플래그
- --persona-scribe=ko|en, --c7(문서), --validate

## 절차
1) 독자/목표 파악
2) 섹션 구조화, 사실/참고자료 수집
3) 예시 포함 초안 작성, 간결하게
4) 정확성 검토, 출처 링크

## 예시
- `/sc:document docs/guide.md --persona-scribe=ko --c7`
