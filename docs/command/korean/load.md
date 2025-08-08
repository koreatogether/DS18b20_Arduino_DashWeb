# /sc:load — 사용법 (한글)

원본: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/load.md
라이선스: MIT. 요약 번역본.

## 목적
분석을 위해 파일, 명세, 데이터셋, 프로젝트 메타데이터 등 컨텍스트를 로드합니다.

## 입력
- 경로/글롭, 컨텍스트 크기 제한, 필터

## 출력
- 컨텍스트 스냅샷, 요약 인덱스

## 주요 플래그
- --uc(압축), --seq, --c7

## 절차
1) 글롭/크기 필터로 관련 파일 선택
2) 요약/메타데이터 추출, 노이즈 최소화
3) 인덱스 저장/반환, 후속 단계에 활용

## 예시
- `/sc:load src/ include/ --uc`
