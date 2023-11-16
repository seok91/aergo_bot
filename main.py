import asyncio
from api import upbit, bithumb
import util
import traceback
import time
import requests
from consts import *
from datetime import datetime, timedelta

class Premium:
    def __init__(self):
        self.exchange_price = {}

    async def compare_price(self):

        myToken = "xoxb-5734472648193-6184610018119-eDzfqrLIFkiIgMuY9KCF1xee"  # 슬랙 토근

        def post_message(channel, text):
            response = requests.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": "Bearer " + myToken},
                data={"channel": channel, "text": text}
            )
            if response.status_code == 200:
                print("메시지가 성공적으로 전송되었습니다.")
            else:
                print("메시지 전송이 실패하였습니다. 오류 코드:", response.status_code)
            time.sleep(1)

        while True:
            try:
                await asyncio.sleep(COMPARE_PRICE_DELAY)  # 거래소별 connect_socket를 통해 가져와야할 코인정보가 있어서 대기
                exchange_price = self.exchange_price.copy()  # 거래소에서 얻어온 가격데이터 복사

                base_exchange_price = float(exchange_price['AERGO']['Bithumb']["ask_price"]) \
                    if float(exchange_price['AERGO']['Bithumb']["ask_price"]) > 0 else float(
                    exchange_price['AERGO']['Bithumb']["ask_price"])

                base_volume = float(exchange_price['AERGO']['Bithumb']["ask_size"]) * base_exchange_price

                compare_exchange_price = float(exchange_price['AERGO']['Upbit']["bid_price"]) \
                    if float(exchange_price['AERGO']['Upbit']["bid_price"]) > 0 else float(
                    exchange_price['AERGO']['Upbit']["bid_price"])

                compare_volume = float(exchange_price['AERGO']['Upbit']["bid_size"]) * compare_exchange_price

                # 거래소간의 가격차이(%)
                diff = round((compare_exchange_price - base_exchange_price) / compare_exchange_price * 100, 3) if base_exchange_price else 0

                current_time = datetime.now().strftime('%H:%M:%S')
                message = (f"[{current_time}] {'AERGO'} [[{diff:.1f}%]] \n")

                # message += (f"({'Bithumb'}) {base_exchange_price:,.1f}원 / {(base_volume / 1000000):.1f} 백만\n"
                #             f"({'Upbit'}) {compare_exchange_price:,.0f}원 / {(compare_volume / 1000000):.1f} 백만\n"
                #             f"--------------------------------\n\n")
                # print(message)

                if base_volume >= 2000000:  # 최우선 호가 거래 대금이 200만 이상인 경우
                    message += (f"({'Bithumb'}) {base_exchange_price:,.1f}원 / {(base_volume / 1000000):.1f} 백만\n"
                                f"({'Upbit'}) {compare_exchange_price:,.0f}원 / {(compare_volume / 1000000):.1f} 백만\n"
                                f"--------------------------------\n\n")

                    if diff > 3:  # 미리 설정한 알림기준을 넘으면 출력
                        print(message)
                        post_message("매크로-알림", message)  # 슬랙 전송


            except Exception as e:
                util.send_to_telegram(traceback.format_exc())
                print(e)

    async def send_periodic_message(self):
        while True:
            util.send_to_telegram("AERGO[빗썸→업비트] 추적 매크로 동작 중...")
            await asyncio.sleep(3600)  # 1시간 마다 실행

    async def run(self):
        util.send_to_telegram("AERGO[빗썸→업비트] 추적 매크로 시작")
        await asyncio.wait([
            asyncio.create_task(upbit.connect_socket(self.exchange_price)),  # upbit websocket 연결 및 가격정보 조회&저장
            asyncio.create_task(bithumb.connect_socket(self.exchange_price)),  # bithumb websocket 연결 및 가격정보 조회&저장
            asyncio.create_task(self.compare_price()),  # 거래소별 정방향 가격비교 후 알림
            asyncio.create_task(self.send_periodic_message())  # 주기적인 메세지 전송 / 프로그램 동작 확인
        ])

if __name__ == "__main__":
    premium = Premium()
    asyncio.run(premium.run())