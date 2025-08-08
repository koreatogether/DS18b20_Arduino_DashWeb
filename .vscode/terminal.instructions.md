유닛테스트시 
pio test -e native -v 2>&1 | tee test/logs/test_results_clean.txt
식의 결과물도 저장하고 터미널에서도 결과를 확인할 수 있도록 한다.

컴파일 시에도 같다.
pio run -e uno_r4_wifi -v 2>&1 | tee logs/comfile/compile_results.txt
를 쓰면된다.
