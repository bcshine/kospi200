# 📊 코스피 200 RSI 분석 웹 애플리케이션 완벽 제작 지침서

## 🎯 프로젝트 개요

한국 주식시장 코스피 200 종목의 RSI(Relative Strength Index) 지표를 실시간으로 분석하고 표시하는 웹 애플리케이션입니다. 네이버증권 데이터를 기반으로 매일 자동 업데이트되며, 월별 아카이브 관리 기능을 포함합니다.

## ⚠️ 중요한 실수 방지 체크리스트

### 🔴 **절대 피해야 할 실수들**

1. **테이블 구조 불일치**
   - ❌ HTML 헤더와 JavaScript 컬럼 배열이 다름
   - ❌ CSS nth-child 순서와 실제 테이블 구조 불일치
   - ✅ **해결**: 9개 열 구조로 완전 통일

2. **파일명 관련 실수**
   - ❌ `results_나스닥_100.csv` (잘못된 데이터 소스)
   - ❌ `results_코스피_200(2).csv` (중복 파일)
   - ✅ **해결**: `results_코스피_200.csv` 단일 메인 파일

3. **스케줄러 API 오류**
   - ❌ `schedule.every().month.at("01")` (존재하지 않는 API)
   - ✅ **해결**: 매일 체크해서 1일인지 확인하는 방식

4. **날짜 포맷 불일치**
   - ❌ 하드코딩된 과거 날짜
   - ✅ **해결**: 동적 날짜 생성 및 한국어 포맷

## 📁 완벽한 파일 구조

```
프로젝트_루트/
├── 📄 index.html                    # 메인 웹페이지
├── 🎨 style.css                     # 스타일시트  
├── ⚙️ script.js                     # 프론트엔드 로직
├── 📊 results_코스피_200.csv         # 웹페이지용 메인 데이터 파일
├── 📊 results_코스피_200_YYYY_MM.csv # 월별 아카이브 파일
├── 🤖 data_collector.py             # 네이버증권 데이터 수집
├── ⏰ scheduler.py                  # 자동 업데이트 스케줄러
├── 🗂️ file_manager.py              # 파일 관리 도구
├── 🚀 run_scheduler.bat            # Windows 실행 스크립트
├── 📝 README_스케줄러.md            # 사용법 문서
├── 📋 kospi200_scheduler.log       # 로그 파일
└── 💾 backups/                     # 백업 폴더
    └── results_코스피_200_YYYYMMDD_HHMMSS.csv
```

## 🔧 단계별 구현 가이드

### 1단계: 기본 웹페이지 구조 (index.html)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>코스피 200 RSI 조건 분석</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>코스피 200 RSI 조건 분석</h1>
        
        <!-- 새로고침 컨트롤 (날짜 표시 제거됨) -->
        <div class="controls">
            <button id="refresh-btn">새로고침</button>
        </div>
        
        <!-- 통계 정보 표시 -->
        <div class="stats">
            <div class="stat-item">
                <span class="stat-label">총 종목 수:</span>
                <span id="total-stocks">0</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">평균 RSI(7):</span>
                <span id="avg-rsi">0</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">마지막 업데이트:</span>
                <span id="last-update">-</span>
            </div>
        </div>
        
        <!-- 상태 메시지 -->
        <div id="loading-message" class="message">데이터를 불러오는 중입니다...</div>
        <div id="error-message" class="message">데이터를 불러오는 중 오류가 발생했습니다.</div>
        <div id="no-data-message" class="message">조건에 맞는 종목이 없습니다.</div>
        
        <!-- ⭐ 중요: 9개 열 구조 정확히 매치 -->
        <table id="results-table">
            <thead>
                <tr>
                    <th>종목명</th>
                    <th>티커</th>
                    <th>산업군</th>
                    <th>RSI7</th>
                    <th>RSI14</th>
                    <th>RSI7 어제</th>
                    <th>RSI14 어제</th>
                    <th>RSI7 차이</th>
                    <th>RSI14 차이</th>
                </tr>
            </thead>
            <tbody id="results-body">
                <!-- 동적 생성 -->
            </tbody>
        </table>
    </div>
    
    <script src="script.js"></script>
</body>
</html>
```

### 2단계: 스타일링 (style.css)

**핵심 주의사항**: 
- 9개 열 구조에 맞는 `nth-child` 선택자 사용
- 반응형 디자인 고려
- 색상 구분 (양수: 녹색, 음수: 빨간색)

```css
/* ⭐ 중요: 9개 열 구조에 맞는 CSS */
th:nth-child(1), td:nth-child(1) { width: 15%; } /* 종목명 */
th:nth-child(2), td:nth-child(2) { width: 8%; }  /* 티커 */
th:nth-child(3), td:nth-child(3) { width: 12%; } /* 산업군 */
th:nth-child(4), td:nth-child(4),
th:nth-child(5), td:nth-child(5),
th:nth-child(6), td:nth-child(6),
th:nth-child(7), td:nth-child(7),
th:nth-child(8), td:nth-child(8),
th:nth-child(9), td:nth-child(9) { width: 9%; } /* RSI 관련 열 */

/* 정렬 화살표 */
th.sortable::after {
    content: '⇅';
    display: inline-block;
    margin-left: 5px;
    opacity: 0.5;
    font-size: 0.8em;
}

th.sort-asc::after {
    content: '↑';
    opacity: 1;
}

th.sort-desc::after {
    content: '↓';
    opacity: 1;
}

/* 변화량 색상 구분 */
.positive-change {
    color: #27ae60;
    font-weight: bold;
    background-color: rgba(39, 174, 96, 0.05);
}

.negative-change {
    color: #e74c3c;
    font-weight: bold;
    background-color: rgba(231, 76, 60, 0.05);
}
```

### 3단계: 프론트엔드 로직 (script.js)

**핵심 주의사항**:
- 9개 컬럼 배열 정확히 매치
- 한국어 날짜 포맷 사용
- 에러 처리 강화

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // ⭐ 중요: 9개 열 구조 정확히 매치
    const columns = ['Name', 'Ticker', 'Industry', 'RSI7', 'RSI14', 'Yesterday_RSI7', 'Yesterday_RSI14', 'RSI7_Change', 'RSI14_Change'];
    
    // ⭐ 중요: 정확한 파일명 사용
    const csvFile = 'results_코스피_200.csv';
    
    // RSI 차이 계산 및 색상 적용
    function renderChangeCell(change, cell) {
        if (change) {
            const changeValue = parseFloat(change);
            cell.textContent = changeValue > 0 ? `+${changeValue.toFixed(2)}` : changeValue.toFixed(2);
            if (changeValue > 0) {
                cell.classList.add('positive-change');
            } else if (changeValue < 0) {
                cell.classList.add('negative-change');
            }
        } else {
            cell.textContent = '0.00';
        }
    }
    
    // ⭐ 중요: 한국어 날짜 포맷
    function updateLastUpdated() {
        const now = new Date();
        lastUpdate.textContent = now.toLocaleString('ko-KR');
    }
});
```

### 4단계: 데이터 수집 스크립트 (data_collector.py)

**핵심 주의사항**:
- RSI 계산 알고리즘 정확성
- 네이버증권 접속 제한 고려
- 에러 처리 및 로깅

```python
import numpy as np
import pandas as pd
from datetime import datetime
import logging

class NaverStockDataCollector:
    def __init__(self):
        self.delay = 1  # ⭐ 중요: 요청 간 딜레이 설정
        
    def calculate_rsi(self, prices, period=14):
        """⭐ 중요: 정확한 RSI 계산 알고리즘"""
        if len(prices) < period + 1:
            return None
            
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def collect_all_data(self):
        """⭐ 중요: 현재 날짜 자동 설정"""
        results = []
        for stock_info in self.get_kospi200_list():
            result = {
                'Ticker': stock_info['ticker'],
                'Name': stock_info['name'],
                'Industry': stock_info['industry'],
                'Date': datetime.now().strftime('%Y-%m-%d'),  # 동적 날짜
                'RSI7': self.calculate_rsi(prices, 7),
                'RSI14': self.calculate_rsi(prices, 14),
                'Yesterday_RSI7': self.calculate_rsi(prices[:-1], 7),
                'Yesterday_RSI14': self.calculate_rsi(prices[:-1], 14)
            }
            results.append(result)
        
        # ⭐ 중요: 정확한 파일명으로 저장
        df = pd.DataFrame(results)
        df.to_csv('results_코스피_200.csv', index=False, encoding='utf-8-sig')
        
        return results
```

### 5단계: 자동 스케줄러 (scheduler.py)

**핵심 주의사항**:
- 올바른 schedule API 사용
- 파일 관리 로직
- 로깅 시스템

```python
import schedule
import time
from datetime import datetime
import logging

# ⭐ 중요: 올바른 스케줄링 방법
def main():
    # 매일 오후 4시 데이터 업데이트
    schedule.every().day.at("16:00").do(job_daily_update)
    
    # ⭐ 중요: 매월 1일 체크 (month.at() API는 존재하지 않음)
    def check_monthly_reset():
        if datetime.now().day == 1:  # 매월 1일에만 실행
            job_monthly_reset()
    
    schedule.every().day.at("09:00").do(check_monthly_reset)
    
    # 무한 루프로 스케줄 실행
    while True:
        schedule.run_pending()
        time.sleep(60)

def job_daily_update():
    """매일 실행되는 업데이트 작업"""
    logging.info("=== 코스피 200 RSI 데이터 수집 시작 ===")
    scheduler = KOSPI200Scheduler()
    success = scheduler.collect_and_update_data()
    
def job_monthly_reset():
    """매월 1일 실행되는 파일 생성 작업"""
    scheduler = KOSPI200Scheduler()
    scheduler.create_monthly_file()
```

### 6단계: 파일 관리 시스템

**핵심 주의사항**:
- 메인 파일과 아카이브 파일 구분
- 백업 시스템
- 파일 크기 관리

```python
class KOSPI200FileManager:
    def __init__(self):
        # ⭐ 중요: 정확한 파일명 패턴
        self.base_filename = "results_코스피_200"
        self.display_filename = f"{self.base_filename}.csv"  # 웹페이지용
        
    def get_monthly_filename(self, year=None, month=None):
        """⭐ 중요: 월별 파일명 패턴"""
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        return f"{self.base_filename}_{year}_{month:02d}.csv"
    
    def manage_file_size(self, filename):
        """⭐ 중요: 파일 크기 관리 (최대 1000개 레코드)"""
        df = pd.read_csv(filename, encoding='utf-8-sig')
        if len(df) > 1000:
            df = df.sort_values('Date', ascending=False).head(1000)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
```

## 🚨 실수 방지를 위한 테스트 체크리스트

### ✅ **구현 완료 후 반드시 확인할 것들**

1. **테이블 구조 일치성 확인**
   ```bash
   # HTML 헤더 개수와 JavaScript columns 배열 길이 일치하는지 확인
   ```

2. **파일명 일관성 확인**
   ```bash
   # script.js에서 로드하는 파일명이 실제 생성되는 파일명과 일치하는지 확인
   ```

3. **날짜 포맷 확인**
   ```bash
   # CSV 데이터의 날짜가 현재 날짜로 올바르게 생성되는지 확인
   ```

4. **스케줄러 정상 작동 확인**
   ```bash
   python scheduler.py status
   python scheduler.py update  # 수동 테스트
   ```

5. **웹페이지 기능 확인**
   ```bash
   python -m http.server 8000
   # 브라우저에서 http://localhost:8000 접속하여 확인
   ```

## 🔧 설치 및 실행 가이드

### 필수 패키지 설치
```bash
pip install schedule requests beautifulsoup4 pandas numpy
```

### Windows 자동 실행
```batch
# run_scheduler.bat 실행
@echo off
chcp 65001
echo 🚀 코스피 200 RSI 자동 업데이트 스케줄러 시작
pip install schedule requests beautifulsoup4 pandas numpy
python scheduler.py
pause
```

### 수동 명령어
```bash
# 즉시 업데이트
python scheduler.py update

# 상태 확인
python scheduler.py status

# 새로운 월 파일 생성
python scheduler.py newmonth

# 파일 관리
python file_manager.py list
python file_manager.py backup
python file_manager.py cleanup
```

## 🎯 코딩 스타일 가이드

### 변수명 일관성 [[memory:2608108]]
- 애플리케이션 코드와 데이터 소스 간 변수명 통일
- 한국어 컬럼명과 영어 키값 매핑 명확히

### 상세한 주석 작성 [[memory:2705318]]
- 모든 함수에 한 줄 설명 주석
- 중요한 로직에는 라인별 주석
- 에러 처리 부분 상세 설명

### 파일 포맷 고려 [[memory:2340846]]
- CSV 파일은 UTF-8-sig 인코딩 사용
- 날짜 형식은 YYYY-MM-DD 표준 사용

## 🚀 배포 및 운영 가이드

### 로컬 환경
```bash
# 개발 서버 실행
python -m http.server 8000

# 스케줄러 백그라운드 실행 (Linux/Mac)
nohup python scheduler.py &

# Windows 서비스 등록
nssm install KOSPI200Scheduler
```

### 모니터링
```bash
# 로그 확인
tail -f kospi200_scheduler.log

# 파일 상태 확인
python file_manager.py stats

# 시스템 상태 확인
python scheduler.py status
```

## 💡 고급 확장 기능

### 추가 가능한 기능들
1. **필터링 시스템**: RSI 값 범위별 필터
2. **알림 시스템**: 특정 조건 만족 시 이메일/SMS 알림  
3. **차트 시각화**: Chart.js를 활용한 RSI 트렌드 차트
4. **다크 모드**: 사용자 설정 저장
5. **데이터 내보내기**: Excel, PDF 형식 지원

### 성능 최적화
1. **가상 스크롤링**: 대용량 데이터 처리
2. **데이터 캐싱**: 브라우저 로컬 스토리지 활용
3. **웹 워커**: 백그라운드 데이터 처리
4. **CDN 활용**: 정적 자원 최적화

## 📞 문제 해결 가이드

### 자주 발생하는 문제들

1. **"데이터를 불러오는 중 오류가 발생했습니다"**
   - 원인: CSV 파일 없음 또는 파일명 불일치
   - 해결: `python scheduler.py update`로 데이터 생성

2. **테이블이 제대로 표시되지 않음**
   - 원인: HTML, JavaScript, CSS 컬럼 수 불일치
   - 해결: 9개 열 구조 정확히 맞추기

3. **스케줄러 AttributeError**
   - 원인: `schedule.every().month.at()` API 없음
   - 해결: 매일 체크해서 1일인지 확인하는 방식 사용

4. **데이터가 업데이트되지 않음**
   - 원인: 네트워크 연결 또는 네이버증권 접속 제한
   - 해결: 딜레이 시간 증가, 재시도 로직 추가

## 🎉 결론

이 지침서를 따라 구현하면 **완벽하게 작동하는 코스피 200 RSI 분석 시스템**을 구축할 수 있습니다. 

### ⭐ 핵심 성공 요소
1. **테이블 구조 일치성** - HTML, JavaScript, CSS 완벽 동기화
2. **파일명 통일성** - 메인 파일과 아카이브 파일 명확한 구분
3. **올바른 API 사용** - schedule 라이브러리 정확한 활용
4. **한국 시장 특성** - 한국어 포맷과 코스피 데이터 구조 이해
5. **자동화 시스템** - 안정적인 스케줄링과 에러 처리

이 지침서는 실제 개발 과정에서 발생한 모든 실수와 해결책을 담고 있어, 동일한 문제를 반복하지 않고 효율적으로 개발할 수 있습니다.

**Happy Coding! 🚀** 