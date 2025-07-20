#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
코스피 200 RSI 데이터 파일 관리 도구

- 월별 파일 관리
- 파일명 정리
- 백업 및 복구
- 웹페이지용 파일 동기화
"""

import os
import shutil
import pandas as pd
from datetime import datetime, timedelta
import logging
import glob

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KOSPI200FileManager:
    def __init__(self):
        self.base_filename = "results_코스피_200"
        self.display_filename = f"{self.base_filename}.csv"
        self.backup_dir = "backups"
        
        # 백업 디렉토리 생성
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def get_monthly_filename(self, year=None, month=None):
        """특정 년월의 파일명을 반환합니다."""
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        return f"{self.base_filename}_{year}_{month:02d}.csv"
    
    def list_all_files(self):
        """모든 관련 파일 목록을 반환합니다."""
        pattern = f"{self.base_filename}*.csv"
        files = glob.glob(pattern)
        
        file_info = []
        for file in files:
            try:
                stat = os.stat(file)
                df = pd.read_csv(file, encoding='utf-8-sig')
                
                file_info.append({
                    'filename': file,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'records': len(df),
                    'date_range': self.get_date_range(df)
                })
            except Exception as e:
                logging.warning(f"파일 {file} 정보 읽기 실패: {e}")
        
        return sorted(file_info, key=lambda x: x['modified'], reverse=True)
    
    def get_date_range(self, df):
        """DataFrame의 날짜 범위를 반환합니다."""
        try:
            if 'Date' in df.columns and len(df) > 0:
                dates = pd.to_datetime(df['Date'])
                return f"{dates.min().strftime('%Y-%m-%d')} ~ {dates.max().strftime('%Y-%m-%d')}"
        except:
            pass
        return "날짜 정보 없음"
    
    def create_backup(self, filename=None):
        """파일 백업을 생성합니다."""
        if filename is None:
            filename = self.display_filename
        
        if not os.path.exists(filename):
            logging.warning(f"백업할 파일이 없습니다: {filename}")
            return False
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{self.backup_dir}/{os.path.splitext(filename)[0]}_{timestamp}.csv"
            
            shutil.copy2(filename, backup_filename)
            logging.info(f"백업 생성 완료: {backup_filename}")
            return backup_filename
            
        except Exception as e:
            logging.error(f"백업 생성 실패: {e}")
            return False
    
    def restore_from_backup(self, backup_filename, target_filename=None):
        """백업에서 파일을 복구합니다."""
        if target_filename is None:
            target_filename = self.display_filename
        
        try:
            if not os.path.exists(backup_filename):
                logging.error(f"백업 파일이 없습니다: {backup_filename}")
                return False
            
            shutil.copy2(backup_filename, target_filename)
            logging.info(f"복구 완료: {backup_filename} -> {target_filename}")
            return True
            
        except Exception as e:
            logging.error(f"복구 실패: {e}")
            return False
    
    def merge_files(self, file_list, output_filename=None):
        """여러 파일을 병합합니다."""
        if output_filename is None:
            output_filename = f"{self.base_filename}_merged_{datetime.now().strftime('%Y%m%d')}.csv"
        
        try:
            all_data = []
            
            for filename in file_list:
                if os.path.exists(filename):
                    df = pd.read_csv(filename, encoding='utf-8-sig')
                    all_data.append(df)
                    logging.info(f"파일 병합: {filename} ({len(df)} 레코드)")
                else:
                    logging.warning(f"파일이 없습니다: {filename}")
            
            if all_data:
                merged_df = pd.concat(all_data, ignore_index=True)
                
                # 중복 제거 (Ticker + Date 기준)
                merged_df = merged_df.drop_duplicates(subset=['Ticker', 'Date'], keep='last')
                
                # 날짜순 정렬
                merged_df['Date'] = pd.to_datetime(merged_df['Date'])
                merged_df = merged_df.sort_values(['Date', 'Ticker'], ascending=[False, True])
                merged_df['Date'] = merged_df['Date'].dt.strftime('%Y-%m-%d')
                
                # 저장
                merged_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
                logging.info(f"병합 완료: {output_filename} ({len(merged_df)} 레코드)")
                return output_filename
            
        except Exception as e:
            logging.error(f"파일 병합 실패: {e}")
            return False
    
    def cleanup_old_files(self, keep_months=6):
        """오래된 파일들을 정리합니다."""
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_months * 30)
            
            files = self.list_all_files()
            removed_count = 0
            
            for file_info in files:
                if (file_info['filename'] != self.display_filename and 
                    file_info['modified'] < cutoff_date):
                    
                    # 백업 생성 후 삭제
                    backup_file = self.create_backup(file_info['filename'])
                    if backup_file:
                        os.remove(file_info['filename'])
                        removed_count += 1
                        logging.info(f"오래된 파일 삭제: {file_info['filename']}")
            
            logging.info(f"파일 정리 완료: {removed_count}개 파일 삭제")
            return removed_count
            
        except Exception as e:
            logging.error(f"파일 정리 실패: {e}")
            return 0
    
    def sync_display_file(self):
        """현재 월 파일을 표시용 파일과 동기화합니다."""
        try:
            current_monthly_file = self.get_monthly_filename()
            
            if os.path.exists(current_monthly_file):
                shutil.copy2(current_monthly_file, self.display_filename)
                logging.info(f"표시 파일 동기화: {current_monthly_file} -> {self.display_filename}")
                return True
            else:
                logging.warning(f"현재 월 파일이 없습니다: {current_monthly_file}")
                return False
                
        except Exception as e:
            logging.error(f"파일 동기화 실패: {e}")
            return False
    
    def fix_filename(self, old_filename):
        """파일명을 정규화합니다."""
        try:
            # results_코스피_200(2).csv -> results_코스피_200.csv
            if "(2)" in old_filename:
                new_filename = old_filename.replace("(2)", "")
                if os.path.exists(old_filename):
                    shutil.move(old_filename, new_filename)
                    logging.info(f"파일명 수정: {old_filename} -> {new_filename}")
                    return new_filename
            return old_filename
            
        except Exception as e:
            logging.error(f"파일명 수정 실패: {e}")
            return old_filename
    
    def get_statistics(self):
        """파일 통계 정보를 반환합니다."""
        files = self.list_all_files()
        
        total_files = len(files)
        total_records = sum(f['records'] for f in files)
        total_size = sum(f['size'] for f in files)
        
        oldest_date = None
        newest_date = None
        
        for file_info in files:
            if file_info['date_range'] != "날짜 정보 없음":
                try:
                    date_parts = file_info['date_range'].split(' ~ ')
                    start_date = datetime.strptime(date_parts[0], '%Y-%m-%d')
                    end_date = datetime.strptime(date_parts[1], '%Y-%m-%d')
                    
                    if oldest_date is None or start_date < oldest_date:
                        oldest_date = start_date
                    if newest_date is None or end_date > newest_date:
                        newest_date = end_date
                except:
                    pass
        
        return {
            'total_files': total_files,
            'total_records': total_records,
            'total_size_mb': total_size / (1024 * 1024),
            'oldest_date': oldest_date.strftime('%Y-%m-%d') if oldest_date else '정보 없음',
            'newest_date': newest_date.strftime('%Y-%m-%d') if newest_date else '정보 없음',
            'files': files
        }

def main():
    """메인 실행 함수"""
    import sys
    
    manager = KOSPI200FileManager()
    
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python file_manager.py list          - 파일 목록 조회")
        print("  python file_manager.py backup        - 현재 파일 백업")
        print("  python file_manager.py cleanup       - 오래된 파일 정리")
        print("  python file_manager.py sync          - 표시 파일 동기화")
        print("  python file_manager.py stats         - 통계 정보")
        print("  python file_manager.py fix [파일명]   - 파일명 수정")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        files = manager.list_all_files()
        print(f"\n📁 총 {len(files)}개 파일:")
        for file_info in files:
            print(f"  {file_info['filename']}")
            print(f"    레코드: {file_info['records']}, 크기: {file_info['size']:,}bytes")
            print(f"    수정일: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    날짜범위: {file_info['date_range']}")
            print()
    
    elif command == "backup":
        backup_file = manager.create_backup()
        if backup_file:
            print(f"✅ 백업 생성: {backup_file}")
        else:
            print("❌ 백업 실패")
    
    elif command == "cleanup":
        removed = manager.cleanup_old_files()
        print(f"✅ {removed}개 파일 정리 완료")
    
    elif command == "sync":
        success = manager.sync_display_file()
        if success:
            print("✅ 파일 동기화 완료")
        else:
            print("❌ 파일 동기화 실패")
    
    elif command == "stats":
        stats = manager.get_statistics()
        print(f"\n📊 통계 정보:")
        print(f"  총 파일 수: {stats['total_files']}")
        print(f"  총 레코드 수: {stats['total_records']:,}")
        print(f"  총 파일 크기: {stats['total_size_mb']:.2f} MB")
        print(f"  가장 오래된 데이터: {stats['oldest_date']}")
        print(f"  가장 최신 데이터: {stats['newest_date']}")
    
    elif command == "fix":
        if len(sys.argv) > 2:
            old_filename = sys.argv[2]
            new_filename = manager.fix_filename(old_filename)
            print(f"✅ 파일명 수정: {new_filename}")
        else:
            print("❌ 파일명을 지정해주세요")

if __name__ == "__main__":
    main() 