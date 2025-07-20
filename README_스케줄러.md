# 코스피 200 RSI 자동 업데이트 시스템

## 📋 개요

매일 오후 4시에 자동으로 코스피 200 종목의 RSI 데이터를 업데이트하고, 매월 1일에 새로운 파일을 생성하는 자동화 시스템입니다.

## 🔧 설치 및 설정

### 1. 필요한 패키지 설치

```bash
pip install schedule requests beautifulsoup4 pandas numpy
```

### 2. 파일 구조

```
프로젝트/
├── scheduler.py              # 메인 스케줄러
├── data_collector.py         # 데이터 수집 스크립트
├── file_manager.py          # 파일 관리 도구
├── results_코스피_200.csv    # 웹페이지용 메인 파일
├── results_코스피_200_YYYY_MM.csv  # 월별 아카이브 파일
├── backups/                 # 백업 파일 저장 폴더
├── kospi200_scheduler.log   # 로그 파일
└── run_scheduler.bat        # Windows 실행 파일
```

## 🚀 실행 방법

### Windows에서 실행
```bash
run_scheduler.bat
```

### 직접 실행
```bash
python scheduler.py
```

### 백그라운드 실행 (Linux/Mac)
```bash
nohup python scheduler.py &
```

## ⏰ 스케줄

- **매일 오후 4시**: 코스피 200 RSI 데이터 자동 업데이트
- **매월 1일 오전 9시**: 새로운 월별 파일 생성 및 이전 파일 아카이브

## 📊 파일 관리

### 자동 관리 기능

1. **월별 파일 생성**: 매월 1일에 `results_코스피_200_YYYY_MM.csv` 형식의 새 파일 생성
2. **메인 파일 유지**: `results_코스피_200.csv`는 항상 웹페이지에서 사용 가능
3. **백업 생성**: 중요한 변경 전 자동 백업
4. **파일 크기 관리**: 최대 1000개 레코드 유지 (오래된 데이터 자동 삭제)

### 수동 관리 명령어

#### 스케줄러 명령어
```bash
# 수동 업데이트
python scheduler.py update

# 상태 확인
python scheduler.py status

# 새로운 월 파일 생성
python scheduler.py newmonth
```

#### 파일 관리 명령어
```bash
# 파일 목록 조회
python file_manager.py list

# 백업 생성
python file_manager.py backup

# 오래된 파일 정리
python file_manager.py cleanup

# 통계 정보 확인
python file_manager.py stats

# 파일명 수정
python file_manager.py fix results_코스피_200(2).csv
```

## 📝 로그 확인

### 로그 파일 위치
- `kospi200_scheduler.log`: 모든 스케줄러 활동 기록

### 로그 레벨
- **INFO**: 일반적인 작업 진행 상황
- **WARNING**: 주의가 필요한 상황
- **ERROR**: 오류 발생 상황

### 로그 예시
```
2025-07-20 16:00:01 - INFO - === 코스피 200 RSI 데이터 수집 시작 ===
2025-07-20 16:00:15 - INFO - 종목 005930 (삼성전자) 데이터 수집 완료
2025-07-20 16:02:30 - INFO - 데이터 업데이트 완료: 30개 종목, 총 150개 레코드
2025-07-20 16:02:31 - INFO - === 데이터 수집 및 업데이트 완료 ===
```

## 🔍 모니터링

### 상태 확인 방법

1. **웹페이지에서 확인**: 마지막 업데이트 시간 확인
2. **로그 파일 확인**: 상세한 작업 기록 검토
3. **파일 수정 시간 확인**: CSV 파일의 수정 시간 확인

### 문제 해결

#### 데이터 업데이트가 안 될 때
```bash
# 수동으로 업데이트 시도
python scheduler.py update

# 상태 확인
python scheduler.py status

# 로그 확인
tail -f kospi200_scheduler.log
```

#### 파일 문제가 있을 때
```bash
# 파일 목록 및 상태 확인
python file_manager.py list

# 백업에서 복구
python file_manager.py backup

# 파일 동기화
python file_manager.py sync
```

## 🛠️ 커스터마이징

### 스케줄 변경
`scheduler.py` 파일에서 다음 부분 수정:

```python
# 매일 오후 4시 → 다른 시간으로 변경
schedule.every().day.at("16:00").do(job_daily_update)

# 예: 매일 오후 5시 30분
schedule.every().day.at("17:30").do(job_daily_update)
```

### 데이터 보관 기간 변경
```python
# 최대 1000개 레코드 → 다른 개수로 변경
if len(df) > 1000:

# 예: 최대 2000개 레코드
if len(df) > 2000:
```

### 백업 보관 기간 변경
```python
# 6개월 → 다른 기간으로 변경
removed = manager.cleanup_old_files(keep_months=6)

# 예: 12개월
removed = manager.cleanup_old_files(keep_months=12)
```

## ⚠️ 주의사항

1. **네트워크 연결**: 네이버증권 데이터 수집을 위해 안정적인 인터넷 연결 필요
2. **서버 가동 시간**: 매일 오후 4시에 컴퓨터가 켜져 있어야 함
3. **디스크 공간**: 월별 파일 누적으로 인한 디스크 공간 관리 필요
4. **권한 설정**: 파일 쓰기 권한 확인 필요

## 🔧 고급 설정

### 서비스로 등록 (Windows)

1. `nssm` (Non-Sucking Service Manager) 설치
2. 서비스 등록:
```cmd
nssm install KOSPI200Scheduler
```
3. 실행 파일 경로: `python.exe`
4. 인자: `전체경로\scheduler.py`

### Cron으로 등록 (Linux/Mac)

```bash
# crontab 편집
crontab -e

# 매일 오후 4시 실행 (한 번만 실행)
0 16 * * * /usr/bin/python3 /path/to/scheduler.py update

# 매월 1일 오전 9시 새 파일 생성
0 9 1 * * /usr/bin/python3 /path/to/scheduler.py newmonth
```

## 📞 문의 및 지원

시스템 운영 중 문제가 발생하면 로그 파일(`kospi200_scheduler.log`)을 확인하여 오류 원인을 파악할 수 있습니다. 