#!/usr/bin/env python3
"""
robust_cppcheck.py
PlatformIO + cppcheck robust 검사 자동화 스크립트 (Python 버전)
- 빌드/업로드 이상 없는 수준의 런타임 robust(잠재적 크래시, null, 미초기화, 포인터, 범위, 스타일 등) 검사
- 로그 파일로 결과 저장 및 요약 출력
"""
import os
import subprocess
from pathlib import Path

def run_and_tee(cmd, logfile, check=True):
    print(f"$ {cmd}")
    with open(logfile, 'w', encoding='utf-8') as f:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
        for line in process.stdout:
            print(line, end='')
            f.write(line)
        process.stdout.close()
        rc = process.wait()
        if check and rc != 0:
            raise SystemExit(rc)
        return rc

def main():
    workdir = Path(__file__).parent.parent.resolve()
    os.chdir(workdir)
    logdir = workdir / 'logs/quality'
    logfile = logdir / 'cppcheck_robust_results.txt'
    logdir.mkdir(parents=True, exist_ok=True)

    # 1. PlatformIO 빌드(에러시 중단)
    print("[1] PlatformIO 빌드...")
    ret = subprocess.run('pio run -e uno_r4_wifi', shell=True)
    if ret.returncode != 0:
        print("❌ 빌드 실패. robust 검사 중단.")
        exit(1)

    # 2. cppcheck 강력 옵션으로 정적 분석 (외부 라이브러리 제외)
    print("[2] cppcheck robust 검사...")
    cppcheck_cmd = 'pio check --flags="--enable=all --inconclusive --force --std=c++17 --exclude=.pio/libdeps --exclude=lib"'
    ret = run_and_tee(cppcheck_cmd, logfile, check=False)

    # 3. 경고/에러 요약
    warn_count = 0
    err_count = 0
    with open(logfile, encoding='utf-8') as f:
        for line in f:
            if '[warning]' in line:
                warn_count += 1
            if '[error]' in line:
                err_count += 1
    if ret != 0:
        print("❌ cppcheck 실행 실패. logs/quality/cppcheck_robust_results.txt를 확인하세요.")
        exit(1)
    elif warn_count == 0 and err_count == 0:
        print("✅ cppcheck: 런타임 robust(잠재적 크래시/버그) 문제 없음!")
    else:
        print(f"⚠️ cppcheck: 경고 {warn_count}건, 에러 {err_count}건 발견. logs/quality/cppcheck_robust_results.txt 확인!")

if __name__ == '__main__':
    main()
