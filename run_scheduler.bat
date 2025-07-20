@echo off
chcp 65001
echo 🚀 코스피 200 RSI 자동 업데이트 스케줄러 시작
echo.

REM Python 가상환경 활성화 (필요시 주석 해제)
REM call venv\Scripts\activate

REM 필요한 패키지 설치 확인
echo 📦 필요한 패키지 설치 확인...
pip install schedule requests beautifulsoup4 pandas numpy

echo.
echo 🔄 스케줄러 실행 중...
echo 종료하려면 Ctrl+C를 누르세요.
echo.

python scheduler.py

pause 