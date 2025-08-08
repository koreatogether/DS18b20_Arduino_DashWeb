import cv2
import os
import numpy as np
from datetime import datetime

def analyze_image_basic(image_path):
    """
    이미지의 기본 정보를 분석하고 반환합니다.
    OCR 없이 이미지 속성과 특성을 추출합니다.
    
    :param image_path: (str) 분석할 이미지 파일의 경로
    :return: (dict) 이미지 분석 결과
    """
    if not os.path.exists(image_path):
        print(f"[오류] 파일을 찾을 수 없습니다: {image_path}")
        return None
    
    try:
        # 이미지 불러오기
        image = cv2.imread(image_path)
        if image is None:
            print(f"[오류] 이미지를 불러올 수 없습니다: {image_path}")
            return None
        
        # 파일 정보
        file_size = os.path.getsize(image_path)
        file_name = os.path.basename(image_path)
        
        # 이미지 속성
        height, width, channels = image.shape
        total_pixels = height * width
        
        # 색상 분석
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 밝기 통계
        mean_brightness = np.mean(gray)
        std_brightness = np.std(gray)
        min_brightness = np.min(gray)
        max_brightness = np.max(gray)
        
        # 히스토그램 분석
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        
        # 텍스트 영역 추정 (에지 검출을 통한 대략적인 추정)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        edge_count = np.sum(edges > 0)
        edge_density = edge_count / total_pixels
        
        # 대비 분석 (Michelson contrast)
        contrast = (max_brightness - min_brightness) / (max_brightness + min_brightness) if (max_brightness + min_brightness) > 0 else 0
        
        # 이미지 품질 추정
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        analysis_result = {
            'file_info': {
                'name': file_name,
                'size_bytes': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2)
            },
            'image_properties': {
                'width': width,
                'height': height,
                'channels': channels,
                'total_pixels': total_pixels,
                'aspect_ratio': round(width / height, 2)
            },
            'brightness_stats': {
                'mean': round(mean_brightness, 2),
                'std': round(std_brightness, 2),
                'min': int(min_brightness),
                'max': int(max_brightness),
                'contrast': round(contrast, 3)
            },
            'quality_metrics': {
                'edge_density': round(edge_density, 4),
                'blur_score': round(blur_score, 2),
                'estimated_quality': 'Good' if blur_score > 100 else 'Poor'
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
            f.write(f"- **해상도**: {analysis_result['image_properties']['width']} × {analysis_result['image_properties']['height']}\n")
            f.write(f"- **종횡비**: {analysis_result['image_properties']['aspect_ratio']}\n")
            f.write(f"- **채널 수**: {analysis_result['image_properties']['channels']}\n")
            f.write(f"- **총 픽셀 수**: {analysis_result['image_properties']['total_pixels']:,}\n\n")
            
            # 밝기 통계
            f.write("## 💡 밝기 분석\n\n")
            f.write(f"- **평균 밝기**: {analysis_result['brightness_stats']['mean']}\n")
            f.write(f"- **밝기 표준편차**: {analysis_result['brightness_stats']['std']}\n")
            f.write(f"- **최소 밝기**: {analysis_result['brightness_stats']['min']}\n")
            f.write(f"- **최대 밝기**: {analysis_result['brightness_stats']['max']}\n")
            f.write(f"- **대비도**: {analysis_result['brightness_stats']['contrast']}\n\n")
            
            # 품질 지표
            f.write("## 📊 품질 지표\n\n")
            f.write(f"- **에지 밀도**: {analysis_result['quality_metrics']['edge_density']}\n")
            f.write(f"- **선명도 점수**: {analysis_result['quality_metrics']['blur_score']}\n")
            f.write(f"- **추정 품질**: {analysis_result['quality_metrics']['estimated_quality']}\n\n")
            
            # 분석 노트
            f.write("## 📝 분석 노트\n\n")
            if analysis_result['quality_metrics']['blur_score'] < 100:
                f.write("⚠️ **주의**: 이미지가 흐릿하거나 품질이 낮을 수 있습니다. OCR 분석 시 정확도가 떨어질 수 있습니다.\n\n")
            else:
                f.write("✅ **양호**: 이미지 품질이 OCR 분석에 적합해 보입니다.\n\n")
            
            if analysis_result['brightness_stats']['contrast'] < 0.3:
                f.write("⚠️ **주의**: 대비도가 낮습니다. 텍스트 인식이 어려울 수 있습니다.\n\n")
            else:
                f.write("✅ **양호**: 대비도가 적절합니다.\n\n")
                
            f.write("---\n\n")
            f.write("*이 분석은 Tesseract OCR 없이 수행되었습니다. 텍스트 추출을 위해서는 Tesseract OCR 엔진 설치가 필요합니다.*\n")
        
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
        print(f"해상도: {result['image_properties']['width']}×{result['image_properties']['height']}")
        print(f"파일 크기: {result['file_info']['size_mb']} MB")
        print(f"평균 밝기: {result['brightness_stats']['mean']}")
        print(f"선명도: {result['quality_metrics']['blur_score']} ({result['quality_metrics']['estimated_quality']})")
        
        # MD 파일로 저장
        if save_analysis_to_md(result, target_image_path, output_md_path):
            print(f"\n--- 📝 결과가 저장되었습니다: {output_md_path} ---")
        else:
            print("\n--- ❌ MD 파일 저장 실패 ---")
    else:
        print("\n--- ❌ 분석 실패 ---")
