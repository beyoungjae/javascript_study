from flask import Flask, jsonify
from datetime import datetime
import asyncio
import json
import os
from aooootu import StockAlert

app = Flask(__name__)
messages = []  # 최근 메시지를 저장할 리스트

# Flask 라우트 설정
@app.route('/messages', methods=['GET'])
def get_messages():
    """최근 10개 메시지를 반환하는 API"""
    return jsonify(messages)

class StockAlertWithFlask(StockAlert):
    async def send_discord_embed(self, title, description, color=0x00ff00, fields=None):
        # 기존 디스코드 알림 전송 기능 유지
        await super().send_discord_embed(title, description, color, fields)

        # 메시지를 Flask 서버에 저장
        message_data = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.now().isoformat(),
            "fields": fields
        }

        # 최근 10개 메시지만 유지하도록 설정
        if len(messages) >= 10:
            messages.pop(0)
        messages.append(message_data)

# Flask와 asyncio 통합 실행
async def run_flask_and_stock_alert():
    stock_alert = StockAlertWithFlask()

    # Flask 서버를 비동기적으로 실행
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, app.run, '0.0.0.0', 5000)

    await stock_alert.start()

if __name__ == "__main__":
    asyncio.run(run_flask_and_stock_alert())
