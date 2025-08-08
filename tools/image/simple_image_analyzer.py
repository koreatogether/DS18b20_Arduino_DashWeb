import os
from datetime import datetime
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def analyze_image_basic(image_path):
    """
    이미지의 기본 정보를 분석하고 반환합니다.
    PIL을 사용하여 기본적인 이미지 속성을 추출합니다.
    
    :param image_path: (str) 분석할 이미지 파일의 경로
    :return: (dict) 이미지 분석 결과
    """
    if not os.path.exists(image_path):
        print(f"[오류] 파일을 찾을 수 없습니다: {image_path}")
        return None
    
    try:
        if not PIL_AVAILABLE:
            print("[경고] PIL/Pillow가 설치되지 않았습니다. 기본 파일 정보만 제공합니다.")
            file_size = os.path.getsize(image_path)
            file_name = os.path.basename(image_path)
            
            return {
                'file_info': {
                    'name': file_name,
                    'size_bytes': file_size,
                    'size_mb': round(file_size / (1024 * 1024), 2)
                },
                'image_properties': {
                    'width': 'Unknown (PIL not available)',
                    'height': 'Unknown (PIL not available)',
                    'mode': 'Unknown (PIL not available)',
                    'format': 'Unknown (PIL not available)'
                },
                'analysis_note': 'PIL/Pillow 라이브러리가 필요합니다. pip install Pillow 로 설치하세요.'
            }
        
        # PIL을 사용한 이미지 분석
        with Image.open(image_path) as img:
            file_size = os.path.getsize(image_path)
            file_name = os.path.basename(image_path)
            
            width, height = img.size
            mode = img.mode
            format_name = img.format
            
            # 색상 통계 (가능한 경우)
            try:
                # 그레이스케일로 변환
                if mode != 'L':
                    gray_img = img.convert('L')
                else:
                    gray_img = img
                
                # 픽셀 값들을 리스트로 변환
                pixels = list(gray_img.getdata())
                
                # 통계 계산
                mean_brightness = sum(pixels) / len(pixels)
                min_brightness = min(pixels)
                max_brightness = max(pixels)
                
                # 간단한 대비도 계산
                contrast = (max_brightness - min_brightness) / 255.0 if max_brightness != min_brightness else 0
                
            except Exception as e:
                print(f"[경고] 색상 분석 중 오류: {e}")
                mean_brightness = None
                min_brightness = None
                max_brightness = None
                contrast = None
            
            analysis_result = {
                'file_info': {
                    'name': file_name,
                    'size_bytes': file_size,
                    'size_mb': round(file_size / (1024 * 1024), 2)
                },
                'image_properties': {
                    'width': width,
                    'height': height,
                    'mode': mode,
                    'format': format_name,
                    'total_pixels': width * height,
                    'aspect_ratio': round(width / height, 2) if height != 0 else None
                },
                'brightness_stats': {
                    'mean': round(mean_brightness, 2) if mean_brightness is not None else 'N/A',
                    'min': int(min_brightness) if min_brightness is not None else 'N/A',
                    'max': int(max_brightness) if max_brightness is not None else 'N/A',
                    'contrast': round(contrast, 3) if contrast is not None else 'N/A'
                }
            }
            
            return analysis_result
        
    except Exception as e:
        print(f"[오류] 이미지 분석 중 오류 발생: {e}")
        return None

def save_analysis_to_md(analysis_result, image_path, output_path):
    """
    분석 결과를 마크다운 파일로 저장합니다.
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 이미지 분석 결과\n\n")
            f.write(f"**분석 대상**: {analysis_result['file_info']['name']}\n\n")
            f.write(f"**분석 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 파일 정보
            f.write("## 📁 파일 정보\n\n")
            f.write(f"- **파일명**: {analysis_result['file_info']['name']}\n")
            f.write(f"- **파일 크기**: {analysis_result['file_info']['size_bytes']:,} bytes ({analysis_result['file_info']['size_mb']} MB)\n\n")
            
            # 이미지 속성
            f.write("## 🖼️ 이미지 속성\n\n")
            if isinstance(analysis_result['image_properties']['width'], int):
                f.write(f"- **해상도**: {analysis_result['image_properties']['width']} × {analysis_result['image_properties']['height']}\n")
                f.write(f"- **종횡비**: {analysis_result['image_properties']['aspect_ratio']}\n")
                f.write(f"- **색상 모드**: {analysis_result['image_properties']['mode']}\n")
                f.write(f"- **파일 형식**: {analysis_result['image_properties']['format']}\n")
                f.write(f"- **총 픽셀 수**: {analysis_result['image_properties']['total_pixels']:,}\n\n")
            else:
                f.write(f"- **해상도**: {analysis_result['image_properties']['width']}\n")
                f.write(f"- **높이**: {analysis_result['image_properties']['height']}\n")
                f.write(f"- **색상 모드**: {analysis_result['image_properties']['mode']}\n")
                f.write(f"- **파일 형식**: {analysis_result['image_properties']['format']}\n\n")
            
            # 밝기 통계 (가능한 경우)
            if 'brightness_stats' in analysis_result:
                f.write("## 💡 밝기 분석\n\n")
                f.write(f"- **평균 밝기**: {analysis_result['brightness_stats']['mean']}\n")
                f.write(f"- **최소 밝기**: {analysis_result['brightness_stats']['min']}\n")
                f.write(f"- **최대 밝기**: {analysis_result['brightness_stats']['max']}\n")
                f.write(f"- **대비도**: {analysis_result['brightness_stats']['contrast']}\n\n")
            
            # 분석 노트
            f.write("## 📝 분석 노트\n\n")
            if 'analysis_note' in analysis_result:
                f.write(f"⚠️ **주의**: {analysis_result['analysis_note']}\n\n")
            else:
                f.write("✅ **완료**: 기본 이미지 분석이 완료되었습니다.\n\n")
                
            f.write("---\n\n")
            f.write("*더 자세한 분석을 위해서는 OpenCV와 Tesseract OCR 설치가 권장됩니다.*\n")
        
        return True
    except Exception as e:
        print(f"[오류] MD 파일 저장 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    # 현재 스크립트가 있는 디렉토리
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_image_path = os.path.join(current_dir, "target.png")
    output_md_path = os.path.join(current_dir, "image_analysis_result.md")
    
    print(f"'{target_image_path}' 이미지 분석을 시작합니다...")
    
    # 이미지 분석
    result = analyze_image_basic(target_image_path)
    
    if result:
        print("\n--- ✅ 분석 완료 ---")
        print(f"파일명: {result['file_info']['name']}")
        print(f"파일 크기: {result['file_info']['size_mb']} MB")
        
        if isinstance(result['image_properties']['width'], int):
            print(f"해상도: {result['image_properties']['width']}×{result['image_properties']['height']}")
            print(f"색상 모드: {result['image_properties']['mode']}")
            print(f"파일 형식: {result['image_properties']['format']}")
        
        # MD 파일로 저장
        if save_analysis_to_md(result, target_image_path, output_md_path):
            print(f"\n--- 📝 결과가 저장되었습니다: {output_md_path} ---")
        else:
            print("\n--- ❌ MD 파일 저장 실패 ---")
    else:
        print("\n--- ❌ 분석 실패 ---")
