from consts import *
import telegram  # TODO pip install python-telegram-bot
import time
from datetime import datetime, timedelta

bot = None

# 입출금상태 매핑
status_convert = {
    '11': "working",
    "10": "deposit_only",
    "01": "withdraw_only",
    "00": "paused"
}


# 입출금상태
wallet_status_map = {
    'working': '정상',
    'deposit_only': '입금만지원(출금불가)',
    'withdraw_only': '출금만지원(입금불가)',
    'unsupported': '입출금불가',
    'paused': '입출금불가'}


def send_to_telegram(message):
    """
    텔레그렘 메시지 전송함수, 최대 3회 재전송 수행
    :param message:
    :return:
    """
    global bot
    if not bot:
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        else:
            raise Exception("consts.py > TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID")

    retries = 0
    max_retries = 3

    while retries < max_retries and bot:
        try:
            print(message)
            bot.send_message(text=message[:TELEGRAM_MESSAGE_MAX_SIZE], chat_id=TELEGRAM_CHAT_ID)
            return True
        except telegram.error.TimedOut as timeout:
            time.sleep(5 * retries)
            retries += 1
            print("Telegram got a error! retry...")
        except Exception as e:
            bot = None
            retries = max_retries

    if retries == max_retries:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        print("Telegram failed to retry...")


def clear_exchange_price(exchange, exchange_price):
    """
    소켓연결이 끊어진 경우, 이전까지 받아온 데이터들은 더이상 유효하지 않기 때문에 삭제하는 역할을 하는 함수
    :param exchange:
    :param exchange_price:
    :return:
    """
    for ticker in exchange_price:
        if exchange in exchange_price[ticker]:
            del exchange_price[ticker][exchange]



def is_need_reset_socket(start_time):
    """
    매일 오전 9시인지 확인해 9시가 넘었다면 True를 반환 (Websocket 재연결 목적)
    :param start_time:
    :return:
    """
    now = datetime.now()
    start_date_base_time = start_time.replace(hour=9, minute=0, second=0, microsecond=0)
    next_base_time = (start_time + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    if start_time < start_date_base_time:
        if start_date_base_time < now:
            return True
        else:
            return

    if next_base_time < now:
        return True
    else:
        return