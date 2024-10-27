import os
import yfinance as yf
from datetime import datetime, timedelta, timezone 
import pandas as pd
import numpy as np
import aiohttp
import asyncio
import pytz
import holidays
import logging
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import configparser

class StockAlert:
    def __init__(self, config_file='config.ini'):
        # 환경 변수 및 설정 로드
        load_dotenv()
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self.NEWS_API_KEY = self.config['API']['NEWS_API_KEY']
        self.DISCORD_WEBHOOK_URL = self.config['API']['DISCORD_WEBHOOK_URL']
        self.STOCK_SYMBOLS = [symbol.strip() for symbol in self.config['SETTINGS']['STOCK_SYMBOLS'].split(',')]
        self.CHECK_INTERVAL_MINUTES = int(self.config['SETTINGS']['CHECK_INTERVAL_MINUTES'])
        self.COOLDOWN_PERIOD_MINUTES = int(self.config['SETTINGS']['COOLDOWN_PERIOD_MINUTES'])

        # 로그 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("stock_alerts.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # 미국 공휴일 설정
        self.us_holidays = holidays.US()
        self.EXCLUDED_HOLIDAYS = {"Columbus Day", "Veterans Day"}

        # VADER 감성 분석기 초기화
        self.analyzer = SentimentIntensityAnalyzer()

        # 이전 신호 및 쿨다운 타임 저장
        self.previous_signals = {}
        self.signal_cooldowns = {}
        self.COOLDOWN_PERIOD = timedelta(minutes=self.COOLDOWN_PERIOD_MINUTES)

        # Initialize aiohttp session as None
        self.session = None

    async def send_discord_embed(self, title, description, color=0x00ff00, fields=None):
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.now(timezone.utc).isoformat(),  # 수정된 부분
            "fields": []
        }
        if fields:
            for field in fields:
                embed["fields"].append({
                    "name": field["name"],
                    "value": field["value"],
                    "inline": field.get("inline", False)
                })
        data = {"embeds": [embed]}
        try:
            async with self.session.post(self.DISCORD_WEBHOOK_URL, json=data) as response:
                if response.status == 204:
                    self.logger.info(f"디스코드 임베드 전송 성공: {title}")
                else:
                    response_text = await response.text()
                    self.logger.error(f"디스코드 임베드 전송 실패: {response.status} - {response_text}")
        except Exception as e:
            self.logger.error(f"디스코드 임베드 전송 중 오류 발생: {e}")

    def get_stock_data(self, symbol, use_cache=True):
        cache_dir = "cache"
        os.makedirs(cache_dir, exist_ok=True)  # 캐시 디렉토리 생성
        cache_file = os.path.join(cache_dir, f"{symbol}_data.csv")
        cache_expiry = 60 * 30  # 30분 (초 단위)

        try:
            if use_cache and os.path.exists(cache_file):
                last_modified_time = os.path.getmtime(cache_file)
                current_time = time.time()
                if (current_time - last_modified_time) < cache_expiry:
                    data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                    self.logger.info(f"{symbol} 데이터를 캐시에서 불러왔습니다.")
                    return data
                else:
                    self.logger.info(f"{symbol} 캐시가 만료되었습니다. 데이터를 새로 가져옵니다.")
            else:
                if use_cache:
                    self.logger.info(f"{symbol} 캐시 파일이 존재하지 않습니다. 데이터를 새로 가져옵니다.")

            # 실시간 데이터 가져오기
            data = yf.download(symbol, period='1y', interval='1d')
            if data.empty:
                self.logger.error(f"{symbol} 데이터를 가져오지 못했습니다.")
                return None
            if use_cache:
                data.to_csv(cache_file)
                self.logger.info(f"{symbol} 데이터를 새로 가져와서 캐시에 저장했습니다.")
            return data
        except Exception as e:
            self.logger.error(f"{symbol} 데이터를 가져오는 중 오류 발생: {str(e)}")
            return None
    
    async def analyze_news(self, stock_symbol):
        url = f'https://newsapi.org/v2/everything?q={stock_symbol}&apiKey={self.NEWS_API_KEY}&language=en&sortBy=publishedAt'
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    self.logger.error(f"뉴스 API 호출 실패: {response.status}")
                    return "뉴스 가져오기 실패", None, 0x000000, None

                data = await response.json()
                articles = data.get('articles', [])
                if not articles:
                    return "뉴스 없음", None, 0x000000, None

                positive, negative, neutral = 0, 0, 0
                total_sentiment = 0

                for article in articles[:5]:  # 최대 5개 기사
                    title = article['title']
                    sentiment = self.analyzer.polarity_scores(title)['compound']
                    total_sentiment += sentiment

                    if sentiment >= 0.05:
                        sentiment_label = "긍정"
                        positive += 1
                    elif sentiment <= -0.05:
                        sentiment_label = "부정"
                        negative += 1
                    else:
                        sentiment_label = "중립"
                        neutral += 1

                total_articles = positive + negative + neutral
                if total_articles == 0:
                    positive_pct = negative_pct = neutral_pct = 0
                else:
                    positive_pct = (positive / total_articles) * 100
                    negative_pct = (negative / total_articles) * 100
                    neutral_pct = (neutral / total_articles) * 100

                news_summary = (
                    f"**긍정 기사**: {positive} ({positive_pct:.1f}%)\n"
                    f"**부정 기사**: {negative} ({negative_pct:.1f}%)\n"
                    f"**중립 기사**: {neutral} ({neutral_pct:.1f}%)\n"
                )

                avg_sentiment = total_sentiment / total_articles if total_articles > 0 else 0

                if avg_sentiment > 0.2:
                    summary = "📈  호재"
                    color = 0x00ff00
                elif avg_sentiment < -0.2:
                    summary = "📉  악재"
                    color = 0xff0000
                else:
                    summary = "⚪  중립"
                    color = 0x808080

                fields = [
                    {"name": "긍정 기사", "value": f"{positive} ({positive_pct:.1f}%)", "inline": True},
                    {"name": "부정 기사", "value": f"{negative} ({negative_pct:.1f}%)", "inline": True},
                    {"name": "중립 기사", "value": f"{neutral} ({neutral_pct:.1f}%)", "inline": True},
                ]

                return summary, news_summary, color, fields
        except Exception as e:
            self.logger.error(f"뉴스 분석 중 오류 발생: {e}")
            return "뉴스 분석 오류", None, 0x000000, None
        
    def calculate_rsi(self, data, period=14):
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(0)

    def calculate_macd(self, data, short_window=12, long_window=26, signal_window=9):
        short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
        long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()
        macd = short_ema - long_ema
        signal = macd.ewm(span=signal_window, adjust=False).mean()
        return macd, signal

    def calculate_bollinger_bands(self, data, window=20, num_std=2):
        rolling_mean = data['Close'].rolling(window).mean()
        rolling_std = data['Close'].rolling(window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        return rolling_mean, upper_band, lower_band
    
    async def analyze_stock(self, symbol):
        self.logger.info(f"{symbol} 분석 시작")
        data = self.get_stock_data(symbol)
        if data is None:
            self.logger.error(f"{symbol} 데이터를 가져오지 못했습니다. 분석을 중단합니다.")
            return

        # 지표 계산
        data['RSI'] = self.calculate_rsi(data)
        data['MACD'], data['Signal'] = self.calculate_macd(data)
        data['MA50'] = data['Close'].rolling(window=50).mean()
        data['MA200'] = data['Close'].rolling(window=200).mean()
        data['RollingMean'], data['UpperBB'], data['LowerBB'] = self.calculate_bollinger_bands(data)

        # 최근 데이터에서 지표 추출
        latest = data.tail(1)
        rsi = latest['RSI'].values[0]
        macd = latest['MACD'].values[0]
        signal_line = latest['Signal'].values[0]
        close_price = latest['Close'].values[0]
        ma50 = latest['MA50'].values[0]
        ma200 = latest['MA200'].values[0]
        upper_bb = latest['UpperBB'].values[0]
        lower_bb = latest['LowerBB'].values[0]

        self.logger.info(f"{symbol} 지표 계산 완료: RSI={rsi:.2f}, MACD={macd:.2f}, Signal={signal_line:.2f}")

        # 뉴스 감성 분석
        sentiment_summary, news_details, sentiment_color, sentiment_fields = await self.analyze_news(symbol)
        self.logger.info(f"{symbol} 뉴스 감성 분석 완료: {sentiment_summary}")

        # 현재 신호 결정
        current_signal = None
        color = 0x000000
        if rsi < 30 and macd < signal_line:
            current_signal = "📈  강력 매수 신호"
            color = 0x00ff00
        elif 30 <= rsi < 40 and macd < signal_line:
            current_signal = "🟢  매수 관찰 신호"
            color = 0x00ff00
        elif rsi > 70 and macd > signal_line:
            current_signal = "📉  강력 매도 신호"
            color = 0xff0000
        elif 60 < rsi <= 70 and macd > signal_line:
            current_signal = "🔴  매도 관찰 신호"
            color = 0xff0000
        elif close_price > upper_bb:
            current_signal = "🟡  볼린저 밴드 상단 돌파"
            color = 0xffff00
        elif close_price < lower_bb:
            current_signal = "🔵  볼린저 밴드 하단 돌파"
            color = 0x0000ff
        else:
            current_signal = "⚪  지켜보는 단계"
            color = 0x808080

        self.logger.info(f"{symbol} 신호 결정: {current_signal}")

        now = datetime.now(pytz.timezone('America/New_York'))
        cooldown_key = f"{symbol}_{current_signal}"
        last_signal_time = self.signal_cooldowns.get(cooldown_key)

        if last_signal_time is None or now - last_signal_time > self.COOLDOWN_PERIOD:
            self.signal_cooldowns[cooldown_key] = now
            self.previous_signals[symbol] = current_signal

            # 메시지 생성 및 전송
            title = f"{symbol} - {current_signal}"
            description = (
                f"**RSI**: {rsi:.2f}\n"
                f"**MACD**: {macd:.2f} | **Signal**: {signal_line:.2f}\n"
                f"**종가**: ${close_price:.2f}\n"
                f"**MA50**: ${ma50:.2f} | **MA200**: ${ma200:.2f}\n"
                f"**볼린저 밴드**: Upper ${upper_bb:.2f}, Lower ${lower_bb:.2f}\n"
                f"**감성 분석**: {sentiment_summary}"
            )

            if news_details:
                description += f"\n\n**뉴스 감성 분포:**\n{news_details}"

            self.logger.info(f"{symbol} 알림 전송 준비: {title}")
            await self.send_discord_embed(title, description, color=color, fields=sentiment_fields)
        else:
            self.logger.info(f"{symbol}: {current_signal}에 대한 쿨다운 기간 중. 메시지 전송 생략.")

    def is_market_open(self):
        now = datetime.now(pytz.timezone('America/New_York'))
        today = now.date()
        holiday_name = self.us_holidays.get(today)

        if holiday_name and holiday_name not in self.EXCLUDED_HOLIDAYS:
            self.logger.info(f"오늘은 휴장일입니다: {holiday_name}")
            return False
        if now.weekday() >= 5:
            self.logger.info("주말입니다.")
            return False

        market_open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
        is_open = market_open_time <= now <= market_close_time
        self.logger.info(f"시장 개장 여부: {'열림' if is_open else '닫힘'}")
        return is_open

    async def run_analysis(self):
        self.logger.info("분석 작업 시작")
        if self.is_market_open():
            tasks = [self.analyze_stock(symbol) for symbol in self.STOCK_SYMBOLS]
            await asyncio.gather(*tasks)
        else:
            self.logger.info("미국 주식 시장이 열리지 않음. 대기 중...")

    async def start(self):
        # Initialize aiohttp session
        self.session = aiohttp.ClientSession()

        # Initialize and start the scheduler
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            self.run_analysis,
            IntervalTrigger(minutes=self.CHECK_INTERVAL_MINUTES),
            next_run_time=datetime.now(timezone.utc)  # 첫 실행을 즉시 트리거
        )
        scheduler.start()
        self.logger.info("주식 알림 프로그램이 시작되었습니다.")

        try:
            # Keep the program running indefinitely
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            self.logger.info("프로그램 종료")
        finally:
            await self.session.close()

def main():
    stock_alert = StockAlert()
    asyncio.run(stock_alert.start())

if __name__ == "__main__":
    main()