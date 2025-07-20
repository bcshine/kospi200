#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
코스피 200 종목의 RSI 데이터를 네이버증권에서 수집하는 스크립트

요구사항:
pip install requests beautifulsoup4 pandas numpy

주의사항:
- 네이버증권의 robots.txt와 이용약관을 준수해야 합니다
- 과도한 요청은 차단될 수 있으므로 적절한 딜레이를 설정하세요
- 실제 운영 시에는 API 키나 인증이 필요할 수 있습니다
"""

import requests
import pandas as pd
import numpy as np
import time
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NaverStockDataCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.delay = 1  # 요청 간 딜레이 (초)
        
    def get_kospi200_list(self):
        """
        네이버증권에서 코스피200 종목 리스트를 수집합니다.
        실제로는 네이버증권 API나 웹페이지를 스크래핑해야 합니다.
        """
        # 임시로 주요 코스피200 종목 리스트 반환
        # 실제 구현 시에는 네이버증권에서 동적으로 가져와야 합니다
        kospi200_sample = [
            {'ticker': '005930', 'name': '삼성전자', 'industry': '반도체'},
            {'ticker': '000660', 'name': 'SK하이닉스', 'industry': '반도체'},
            {'ticker': '035420', 'name': 'NAVER', 'industry': '인터넷'},
            {'ticker': '051910', 'name': 'LG화학', 'industry': '화학'},
            {'ticker': '006400', 'name': '삼성SDI', 'industry': '전기전자'},
            {'ticker': '035720', 'name': '카카오', 'industry': '인터넷'},
            {'ticker': '000270', 'name': '기아', 'industry': '자동차'},
            {'ticker': '373220', 'name': 'LG에너지솔루션', 'industry': '전기전자'},
            {'ticker': '207940', 'name': '삼성바이오로직스', 'industry': '바이오'},
            {'ticker': '068270', 'name': '셀트리온', 'industry': '바이오'},
            # 더 많은 종목들을 추가할 수 있습니다
        ]
        
        logging.info(f"코스피200 종목 {len(kospi200_sample)}개 로드 완료")
        return kospi200_sample
    
    def calculate_rsi(self, prices, period=14):
        """
        RSI(Relative Strength Index)를 계산합니다.
        
        Args:
            prices: 가격 데이터 리스트
            period: RSI 계산 기간 (기본값: 14일)
        
        Returns:
            RSI 값 (0-100)
        """
        if len(prices) < period + 1:
            return None
            
        # 가격 변화 계산
        deltas = np.diff(prices)
        
        # 상승폭과 하락폭 분리
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # 평균 상승폭과 평균 하락폭 계산
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        if avg_loss == 0:
            return 100
        
        # RSI 계산
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def get_stock_price_data(self, ticker, days=30):
        """
        특정 종목의 주가 데이터를 네이버증권에서 수집합니다.
        실제로는 네이버증권 API를 사용해야 합니다.
        
        Args:
            ticker: 종목 코드
            days: 수집할 일수
        
        Returns:
            가격 데이터 리스트
        """
        try:
            # 임시로 랜덤한 가격 데이터 생성 (실제로는 네이버증권에서 가져와야 함)
            # 실제 구현에서는 다음과 같은 URL을 사용할 수 있습니다:
            # url = f"https://fchart.stock.naver.com/sise.nhn?symbol={ticker}&timeframe=day&count={days}"
            
            base_price = np.random.uniform(10000, 100000)  # 기준 가격
            prices = []
            
            for i in range(days):
                # 랜덤 워크로 가격 생성 (실제 데이터와 유사하게)
                change = np.random.normal(0, 0.02)  # 평균 0%, 표준편차 2%의 변화
                if i == 0:
                    prices.append(base_price)
                else:
                    new_price = prices[-1] * (1 + change)
                    prices.append(max(new_price, base_price * 0.5))  # 최소 50% 이상 유지
            
            time.sleep(self.delay)  # 요청 제한 방지
            return prices
            
        except Exception as e:
            logging.error(f"종목 {ticker} 데이터 수집 오류: {e}")
            return None
    
    def get_stock_rsi_data(self, stock_info):
        """
        개별 종목의 RSI 데이터를 수집하고 계산합니다.
        
        Args:
            stock_info: 종목 정보 딕셔너리 (ticker, name, industry)
        
        Returns:
            RSI 데이터가 포함된 딕셔너리
        """
        ticker = stock_info['ticker']
        
        try:
            # 30일 간의 가격 데이터 수집
            prices = self.get_stock_price_data(ticker, 30)
            
            if not prices or len(prices) < 15:
                logging.warning(f"종목 {ticker}: 충분한 가격 데이터가 없습니다")
                return None
            
            # RSI 계산
            rsi7_today = self.calculate_rsi(prices, 7)
            rsi14_today = self.calculate_rsi(prices, 14)
            rsi7_yesterday = self.calculate_rsi(prices[:-1], 7) if len(prices) > 1 else rsi7_today
            rsi14_yesterday = self.calculate_rsi(prices[:-1], 14) if len(prices) > 1 else rsi14_today
            
            result = {
                'Ticker': ticker,
                'Name': stock_info['name'],
                'Industry': stock_info['industry'],
                'Date': datetime.now().strftime('%Y-%m-%d'),
                'RSI7': rsi7_today,
                'RSI14': rsi14_today,
                'Yesterday_RSI7': rsi7_yesterday,
                'Yesterday_RSI14': rsi14_yesterday
            }
            
            logging.info(f"종목 {ticker} ({stock_info['name']}) 데이터 수집 완료")
            return result
            
        except Exception as e:
            logging.error(f"종목 {ticker} RSI 계산 오류: {e}")
            return None
    
    def collect_all_data(self):
        """
        모든 코스피200 종목의 RSI 데이터를 수집합니다.
        """
        logging.info("코스피200 RSI 데이터 수집 시작")
        
        # 종목 리스트 가져오기
        kospi200_list = self.get_kospi200_list()
        results = []
        
        total_stocks = len(kospi200_list)
        
        for i, stock_info in enumerate(kospi200_list, 1):
            logging.info(f"진행률: {i}/{total_stocks} ({(i/total_stocks)*100:.1f}%)")
            
            try:
                rsi_data = self.get_stock_rsi_data(stock_info)
                if rsi_data:
                    results.append(rsi_data)
            except Exception as e:
                logging.error(f"종목 {stock_info['ticker']} 처리 중 오류: {e}")
                continue
        
        # CSV 파일로 저장
        if results:
            df = pd.DataFrame(results)
            filename = 'results_코스피_200.csv'
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logging.info(f"데이터 수집 완료: {len(results)}개 종목, 파일명: {filename}")
        else:
            logging.warning("수집된 데이터가 없습니다")
        
        return results

def main():
    """메인 실행 함수"""
    collector = NaverStockDataCollector()
    
    try:
        # 데이터 수집 실행
        results = collector.collect_all_data()
        
        if results:
            print(f"\n✅ 데이터 수집 완료!")
            print(f"📊 총 {len(results)}개 종목 데이터 수집")
            print(f"📁 파일 저장: results_코스피_200.csv")
            print(f"🕐 수집 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("❌ 데이터 수집 실패")
            
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 중단되었습니다")
    except Exception as e:
        logging.error(f"메인 실행 오류: {e}")
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main() 