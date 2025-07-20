#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
코스피 200 RSI 데이터 자동 업데이트 스케줄러

매일 오후 4시에 데이터 업데이트
매월 1일에 새로운 파일 생성

설치 필요 패키지:
pip install schedule requests beautifulsoup4 pandas numpy

실행 방법:
python scheduler.py
"""

import schedule
import time
import os
import shutil
from datetime import datetime, date
import logging
from data_collector import NaverStockDataCollector
import pandas as pd

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kospi200_scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class KOSPI200Scheduler:
    def __init__(self):
        self.collector = NaverStockDataCollector()
        self.base_filename = "results_코스피_200"
        self.current_filename = None
        
    def get_current_filename(self):
        """현재 월에 해당하는 파일명을 반환합니다."""
        current_date = datetime.now()
        return f"{self.base_filename}_{current_date.year}_{current_date.month:02d}.csv"
    
    def get_display_filename(self):
        """웹페이지에서 사용할 기본 파일명을 반환합니다."""
        return f"{self.base_filename}.csv"
    
    def create_monthly_file(self):
        """매월 1일에 새로운 파일을 생성합니다."""
        try:
            current_filename = self.get_current_filename()
            display_filename = self.get_display_filename()
            
            # 이전 월 파일이 있다면 아카이브
            if os.path.exists(display_filename):
                previous_date = datetime.now().replace(day=1) - pd.DateOffset(days=1)
                archive_filename = f"{self.base_filename}_{previous_date.year}_{previous_date.month:02d}.csv"
                
                if not os.path.exists(archive_filename):
                    shutil.copy2(display_filename, archive_filename)
                    logging.info(f"이전 월 파일 아카이브 완료: {archive_filename}")
            
            # 새로운 월 파일 생성
            logging.info(f"새로운 월 파일 생성: {current_filename}")
            self.collect_and_update_data(is_new_month=True)
            
        except Exception as e:
            logging.error(f"월별 파일 생성 오류: {e}")
    
    def collect_and_update_data(self, is_new_month=False):
        """데이터를 수집하고 CSV 파일을 업데이트합니다."""
        try:
            logging.info("=== 코스피 200 RSI 데이터 수집 시작 ===")
            
            # 데이터 수집
            results = self.collector.collect_all_data()
            
            if not results:
                logging.warning("수집된 데이터가 없습니다.")
                return False
            
            # DataFrame 생성
            df_new = pd.DataFrame(results)
            display_filename = self.get_display_filename()
            current_filename = self.get_current_filename()
            
            if is_new_month or not os.path.exists(display_filename):
                # 새로운 파일 생성 (새로운 월 또는 파일이 없는 경우)
                df_new.to_csv(display_filename, index=False, encoding='utf-8-sig')
                df_new.to_csv(current_filename, index=False, encoding='utf-8-sig')
                logging.info(f"새로운 파일 생성: {display_filename}")
                
            else:
                # 기존 파일에 데이터 추가
                try:
                    df_existing = pd.read_csv(display_filename, encoding='utf-8-sig')
                    
                    # 오늘 날짜의 기존 데이터가 있다면 제거
                    today = datetime.now().strftime('%Y-%m-%d')
                    df_existing = df_existing[df_existing['Date'] != today]
                    
                    # 새로운 데이터 추가
                    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                    
                    # 날짜순으로 정렬
                    df_combined['Date'] = pd.to_datetime(df_combined['Date'])
                    df_combined = df_combined.sort_values('Date', ascending=False)
                    df_combined['Date'] = df_combined['Date'].dt.strftime('%Y-%m-%d')
                    
                    # 파일 저장
                    df_combined.to_csv(display_filename, index=False, encoding='utf-8-sig')
                    df_combined.to_csv(current_filename, index=False, encoding='utf-8-sig')
                    
                    logging.info(f"데이터 업데이트 완료: {len(results)}개 종목, 총 {len(df_combined)}개 레코드")
                    
                except Exception as e:
                    logging.error(f"기존 파일 읽기 오류: {e}, 새로운 파일로 생성합니다.")
                    df_new.to_csv(display_filename, index=False, encoding='utf-8-sig')
                    df_new.to_csv(current_filename, index=False, encoding='utf-8-sig')
            
            # 파일 크기 관리 (최대 1000개 레코드 유지)
            self.manage_file_size(display_filename)
            self.manage_file_size(current_filename)
            
            logging.info("=== 데이터 수집 및 업데이트 완료 ===")
            return True
            
        except Exception as e:
            logging.error(f"데이터 수집 및 업데이트 오류: {e}")
            return False
    
    def manage_file_size(self, filename):
        """파일 크기를 관리합니다. (최대 1000개 레코드 유지)"""
        try:
            if os.path.exists(filename):
                df = pd.read_csv(filename, encoding='utf-8-sig')
                
                if len(df) > 1000:
                    # 최신 1000개 레코드만 유지
                    df['Date'] = pd.to_datetime(df['Date'])
                    df = df.sort_values('Date', ascending=False).head(1000)
                    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
                    
                    df.to_csv(filename, index=False, encoding='utf-8-sig')
                    logging.info(f"파일 크기 관리: {filename} - 최신 1000개 레코드 유지")
                    
        except Exception as e:
            logging.error(f"파일 크기 관리 오류: {e}")
    
    def manual_update(self):
        """수동 업데이트 (테스트용)"""
        logging.info("수동 업데이트 실행")
        return self.collect_and_update_data()
    
    def get_status(self):
        """현재 상태 정보를 반환합니다."""
        display_filename = self.get_display_filename()
        current_filename = self.get_current_filename()
        
        status = {
            'display_file': display_filename,
            'current_file': current_filename,
            'display_exists': os.path.exists(display_filename),
            'current_exists': os.path.exists(current_filename),
            'last_modified': None,
            'record_count': 0
        }
        
        if os.path.exists(display_filename):
            status['last_modified'] = datetime.fromtimestamp(
                os.path.getmtime(display_filename)
            ).strftime('%Y-%m-%d %H:%M:%S')
            
            try:
                df = pd.read_csv(display_filename, encoding='utf-8-sig')
                status['record_count'] = len(df)
            except:
                pass
        
        return status

def job_daily_update():
    """매일 오후 4시에 실행되는 작업"""
    logging.info("📅 일일 업데이트 작업 시작")
    scheduler = KOSPI200Scheduler()
    success = scheduler.collect_and_update_data()
    
    if success:
        logging.info("✅ 일일 업데이트 완료")
    else:
        logging.error("❌ 일일 업데이트 실패")

def job_monthly_reset():
    """매월 1일에 실행되는 작업"""
    logging.info("📅 월별 파일 생성 작업 시작")
    scheduler = KOSPI200Scheduler()
    scheduler.create_monthly_file()
    logging.info("✅ 월별 파일 생성 완료")

def main():
    """메인 스케줄러 실행 함수"""
    print("🚀 코스피 200 RSI 자동 업데이트 스케줄러 시작")
    print("=" * 50)
    
    # 스케줄 설정
    schedule.every().day.at("16:00").do(job_daily_update)  # 매일 오후 4시
    
    # 매월 1일 체크 함수
    def check_monthly_reset():
        if datetime.now().day == 1:  # 매월 1일에만 실행
            job_monthly_reset()
    
    schedule.every().day.at("09:00").do(check_monthly_reset)  # 매일 오전 9시에 체크
    
    # 현재 상태 출력
    scheduler = KOSPI200Scheduler()
    status = scheduler.get_status()
    
    print(f"📁 표시 파일: {status['display_file']} ({'존재' if status['display_exists'] else '없음'})")
    print(f"📁 현재 파일: {status['current_file']} ({'존재' if status['current_exists'] else '없음'})")
    print(f"📊 레코드 수: {status['record_count']}")
    print(f"🕐 마지막 수정: {status['last_modified'] or '정보 없음'}")
    print("=" * 50)
    print("⏰ 스케줄:")
    print("   - 매일 오후 4시: 데이터 업데이트")
    print("   - 매월 1일 오전 9시: 새로운 파일 생성")
    print("=" * 50)
    print("종료하려면 Ctrl+C를 누르세요...")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
            
    except KeyboardInterrupt:
        print("\n⏹️ 스케줄러가 중단되었습니다.")
        logging.info("스케줄러가 사용자에 의해 중단되었습니다.")

if __name__ == "__main__":
    # 명령줄 인자 처리
    import sys
    
    if len(sys.argv) > 1:
        scheduler = KOSPI200Scheduler()
        
        if sys.argv[1] == "update":
            # 수동 업데이트
            print("🔄 수동 업데이트 실행...")
            success = scheduler.manual_update()
            print("✅ 완료" if success else "❌ 실패")
            
        elif sys.argv[1] == "status":
            # 상태 확인
            status = scheduler.get_status()
            print("📊 현재 상태:")
            for key, value in status.items():
                print(f"   {key}: {value}")
                
        elif sys.argv[1] == "newmonth":
            # 새로운 월 파일 생성
            print("📅 새로운 월 파일 생성...")
            scheduler.create_monthly_file()
            print("✅ 완료")
            
    else:
        # 기본 스케줄러 실행
        main() 