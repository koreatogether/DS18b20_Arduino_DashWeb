
#!/usr/bin/env python3
import subprocess
import sys
import os

def run_command(command, log_file=None):
    print(f"Running: {command}")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    output, _ = process.communicate()
    output = output.decode(errors='replace')
    print(output)
    if log_file:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(output)
    return process.returncode


def main():
    # 1. PlatformIO 빌드
    build_cmd = "pio run -e uno_r4_wifi -v"
    build_log = "logs/comfile/compile_results.txt"
    if run_command(f"{build_cmd} 2>&1", build_log) != 0:
        print("[ERROR] Build failed.")
        sys.exit(1)

    # 2. 유닛 테스트
    test_cmd = "pio test -e native -v"
    test_log = "logs/test_results_clean.txt"
    if run_command(f"{test_cmd} 2>&1", test_log) != 0:
        print("[ERROR] Unit tests failed.")
        sys.exit(1)

    # 3. 민감정보(시크릿) 자동 검사 (git + filesystem)
    print("[INFO] Running secret scan (trufflehog_gitscan.py)...")
    secret_scan_script = os.path.join(
        os.path.dirname(__file__), "trufflehog_gitscan.py"
    )
    result = subprocess.run(
        f'python "{secret_scan_script}"', shell=True
    )
    if result.returncode != 0:
        print("[ERROR] Secret scan failed.")
        sys.exit(1)

    # 4. git add (모든 변경/신규 파일 포함)
    subprocess.run("git add .", shell=True)

    # 5. 커밋/푸시는 수동으로 진행
    diff_result = subprocess.run(
        "git diff --cached --quiet", shell=True
    )
    if diff_result.returncode == 0:
        print("[INFO] 커밋할 변경사항이 없습니다.")
        sys.exit(0)

    print(
        "[INFO] 변경 파일이 스테이징되었습니다. "
        "커밋 메시지 작성 및 git commit/push는 수동으로 진행하세요."
    )

if __name__ == "__main__":
    main()
