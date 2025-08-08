import cv2
import pytesseract
import pandas as pd
import re
import os
import numpy as np

# --- Tesseract OCR 엔진의 설치 경로를 지정해야 할 경우 ---
# 시스템 환경변수에 경로가 등록되어 있지 않다면 아래 코드의 주석을 풀고 경로를 입력하세요.
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def process_error_image(image_path, scale_factor=2.0, psm=6):
    """
    이미지에서 에러 로그를 추출하고 파싱하여 pandas DataFrame으로 반환합니다.
    OCR 정확도를 높이기 위해 이미지 전처리 과정을 포함합니다.

    :param image_path: (str) 분석할 이미지 파일의 경로
    :param scale_factor: (float) 이미지 확대 비율. 글씨가 작을 경우 값을 높이면 인식률이 개선될 수 있습니다.
    :param psm: (int) Tesseract의 페이지 세분화 모드 (Page Segmentation Mode). 기본값 6은 텍스트가 균일한 블록이라고 가정합니다.
    :return: (pd.DataFrame) 파싱된 에러 목록. 실패 시 None을 반환합니다.
    """
    # 1. 파일 존재 여부 확인
    if not os.path.exists(image_path):
        print(f"[오류] 파일을 찾을 수 없습니다: {image_path}")
        return None

    try:
        # 2. 이미지 불러오기 및 전처리 (OpenCV 사용)
        image = cv2.imread(image_path)
        if image is None:
            print(f"[오류] 이미지를 불러올 수 없습니다: {image_path}")
            return None

        # 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 이미지 확대 (작은 글씨 인식률 향상)
        if scale_factor > 1:
            width = int(gray.shape[1] * scale_factor)
            height = int(gray.shape[0] * scale_factor)
            gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)

        # 이진화 (Otsu's Binarization) : 글자와 배경을 명확히 분리
        # 약간의 블러 처리를 통해 노이즈를 제거한 후 이진화하면 결과가 더 좋아질 수 있습니다.
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        _, processed_image = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # 3. Tesseract OCR로 텍스트 추출
        config = f'--psm {psm}'
        extracted_text = pytesseract.image_to_string(processed_image, lang='eng+kor', config=config)

        # 4. 텍스트 파싱 (더 견고한 정규식 사용)
        lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]
        parsed_entries = []
        # 파일 경로에 '/', '\', ':', '.', '-', '_' 등을 포함할 수 있도록 개선
        regex = r'(.+?)\s+([\w.:\\/-]+)\s+(\d+)$'

        for line in lines:
            match = re.search(regex, line)
            if match:
                error_msg = match.group(1).strip()
                file_name = match.group(2).strip()
                line_number = int(match.group(3).strip())
                parsed_entries.append((file_name, error_msg, line_number))

        if not parsed_entries:
            print("[경고] 이미지에서 유효한 에러 형식의 텍스트를 찾지 못했습니다. 이미지 품질이나 내용을 확인해주세요.")
            return None

        # 5. DataFrame 생성 및 반환
        df_errors = pd.DataFrame(parsed_entries, columns=["File", "Error", "Line"])
        return df_errors

    except pytesseract.TesseractNotFoundError:
        print("[치명적 오류] Tesseract OCR 엔진을 찾을 수 없습니다.")
        print("Tesseract를 시스템에 설치하고, 필요한 경우 위 코드에서 경로를 직접 지정해주세요.")
        return None
    except Exception as e:
        print(f"[알 수 없는 오류] 처리 중 오류가 발생했습니다: {e}")
        return None


# --- 사용 예시 ---
if __name__ == "__main__":
    # 1. 분석할 이미지 파일 경로 지정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_image_path = os.path.join(current_dir, "target.png")

    # 2. 함수 호출
    print(f"'{target_image_path}' 이미지 분석을 시작합니다...")
    error_dataframe = process_error_image(target_image_path, scale_factor=2.0)

    # 3. 결과 확인 및 저장
    if error_dataframe is not None:
        print("\n--- ✅ 분석 완료: 파싱된 에러 목록 ---")
        print(error_dataframe.to_string()) # 모든 행이 보이도록 .to_string() 사용
        
        # 4. MD 파일로 저장
        output_md_path = os.path.join(current_dir, "analysis_result.md")
        with open(output_md_path, 'w', encoding='utf-8') as f:
            f.write("# 이미지 OCR 분석 결과\n\n")
            f.write(f"**분석 대상 이미지**: {os.path.basename(target_image_path)}\n\n")
            f.write(f"**분석 시간**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## 추출된 에러 목록\n\n")
            
            if len(error_dataframe) > 0:
                # DataFrame을 마크다운 테이블로 변환
                f.write(error_dataframe.to_markdown(index=False))
                f.write(f"\n\n**총 {len(error_dataframe)}개의 에러가 발견되었습니다.**\n\n")
                
                # 파일별 에러 개수 통계
                f.write("## 파일별 에러 통계\n\n")
                file_counts = error_dataframe['File'].value_counts()
                for file_name, count in file_counts.items():
                    f.write(f"- `{file_name}`: {count}개\n")
            else:
                f.write("추출된 에러가 없습니다.\n")
        
        print(f"\n--- 📝 결과가 저장되었습니다: {output_md_path} ---")
    else:
        print("\n--- ❌ 분석 실패 ---")