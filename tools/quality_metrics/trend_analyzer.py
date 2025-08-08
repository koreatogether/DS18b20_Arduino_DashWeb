#!/usr/bin/env python3
"""
DS18B20 Embedded Application - Quality Metrics Trend Analysis
============================================================

품질 메트릭의 변화를 추적하고 트렌드를 분석하는 도구입니다.
"""

 
import json
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class QualityTrendAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.quality_logs_dir = self.project_root / "logs" / "quality"
        
    def load_historical_metrics(self) -> List[Dict[str, Any]]:
        """과거 품질 메트릭 데이터 로드"""
        metrics_files = glob.glob(str(self.quality_logs_dir / "metrics_*.json"))
        metrics_history = []
        
        for file_path in sorted(metrics_files):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    metrics_history.append(data)
            except Exception as e:
                print(f"❌ Error loading {file_path}: {e}")
                
        return metrics_history
    
    def _compare_metrics(self, latest, previous, trends):
        categories = ["code_metrics", "architecture_metrics", "build_metrics"]  # test_metrics removed
        for category in categories:
            if category in latest and category in previous:
                trends["metrics_comparison"][category] = {
                    "latest": latest[category],
                    "previous": previous[category],
                    "changes": {}
                }
                latest_cat = latest[category]
                previous_cat = previous[category]
                for key in latest_cat:
                    if key in previous_cat and isinstance(latest_cat[key], (int, float)):
                        change = latest_cat[key] - previous_cat[key]
                        if abs(change) > 0.1:
                            trends["metrics_comparison"][category]["changes"][key] = change

    def _generate_recommendations(self, trends, latest, previous):
        if trends["score_change"] > 5:
            trends["recommendations"].append("✅ Quality score improved significantly!")
        elif trends["score_change"] < -5:
            trends["recommendations"].append("⚠️ Quality score decreased. Review recent changes.")

    def _check_thresholds(self, trends, latest):
        ram_usage = latest.get("build_metrics", {}).get("ram_usage_percent", 0)
        if ram_usage > 80:
            trends["recommendations"].append(f"💾 RAM usage is high ({ram_usage}%). Consider optimization.")

    def analyze_trends(self) -> Dict[str, Any]:
        """품질 메트릭 트렌드 분석"""
        history = self.load_historical_metrics()
        if len(history) < 2:
            return {"message": "Not enough historical data for trend analysis"}
        latest = history[-1]
        previous = history[-2]
        trends = {
            "analysis_date": datetime.now().isoformat(),
            "data_points": len(history),
            "latest_score": latest.get("quality_score", 0),
            "previous_score": previous.get("quality_score", 0),
            "score_change": latest.get("quality_score", 0) - previous.get("quality_score", 0),
            "metrics_comparison": {},
            "recommendations": []
        }
        self._compare_metrics(latest, previous, trends)
        self._generate_recommendations(trends, latest, previous)
        self._check_thresholds(trends, latest)
        return trends
    
    def _trend_report_header(self, trends):
        return f"""
# DS18B20 Quality Metrics Trend Analysis
Generated: {trends['analysis_date']}

## 📈 Overall Quality Score Trend
- **Latest Score**: {trends['latest_score']:.1f}/100
- **Previous Score**: {trends['previous_score']:.1f}/100
- **Change**: {trends['score_change']:+.1f} points

## 📊 Historical Data Points
- **Total Measurements**: {trends['data_points']}

## 🔍 Detailed Changes
"""

    def _trend_report_changes(self, trends):
        report = ""
        for category, data in trends["metrics_comparison"].items():
            if "changes" in data and data["changes"]:
                report += f"\n### {category.replace('_', ' ').title()}\n"
                for metric, change in data["changes"].items():
                    direction = "📈" if change > 0 else "📉"
                    report += f"- **{metric}**: {direction} {change:+.2f}\n"
        return report

    def _trend_report_recommendations(self, trends):
        if trends["recommendations"]:
            recs = "\n## 💡 Recommendations\n"
            for rec in trends["recommendations"]:
                recs += f"- {rec}\n"
            return recs
        return ""

    def generate_trend_report(self) -> str:
        """트렌드 분석 리포트 생성"""
        trends = self.analyze_trends()
        
        if "message" in trends:
            return f"# Quality Trends Analysis\n\n{trends['message']}\n"
        
        report = self._trend_report_header(trends)
        report += self._trend_report_changes(trends)
        report += self._trend_report_recommendations(trends)
        
        return report
    
    def save_trend_analysis(self):
        """트렌드 분석 결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 데이터 저장
        trends = self.analyze_trends()
        json_path = self.quality_logs_dir / f"trend_analysis_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(trends, f, indent=2, ensure_ascii=False)
        
        # 마크다운 리포트 저장
        report = self.generate_trend_report()
        md_path = self.quality_logs_dir / f"trend_report_{timestamp}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print("📊 Trend analysis saved:")
        print(f"  JSON: {json_path}")
        print(f"  Report: {md_path}")
        
        return trends

def main():
    """메인 실행 함수"""
    # 프로젝트 루트 디렉토리 찾기
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    
    print(f"📈 Analyzing quality trends for: {project_root}")
    
    # 트렌드 분석기 초기화
    analyzer = QualityTrendAnalyzer(str(project_root))
    
    # 트렌드 분석 실행
    trends = analyzer.save_trend_analysis()
    
    # 결과 출력
    if "message" not in trends:
        print(f"\n📊 Quality Score: {trends['latest_score']:.1f}/100 ({trends['score_change']:+.1f})")
        print(f"📋 Data Points: {trends['data_points']}")
        if trends["recommendations"]:
            print("\n💡 Key Recommendations:")
            for rec in trends["recommendations"][:3]:  # 상위 3개만 출력
                print(f"  {rec}")
    
    print("\n✅ Trend analysis complete!")

if __name__ == "__main__":
    main()
