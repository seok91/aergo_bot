import os

# Exchanges
UPBIT = 'Upbit'
BITHUMB = 'Bithumb'

# All Exchanges
EXCHANGE_LIST = [UPBIT, BITHUMB]

# API KEYS TODO 프로젝트상으로는 없어도 무관함!
UPBIT_API_KEY = os.getenv("UPBIT_API_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")

# TELEGRAM
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_MESSAGE_MAX_SIZE = 4095  # 텔레그렘 메시지 최대길이

# SOCKET
SOCKET_PING_INTERVAL = 20  # 20초
SOCKET_RETRY_TIME = 30     # 30초
SOCKET_PING_TIMEOUT = 30   # 30초

# DELAY
DOLLAR_UPDATE = 60 * 15      # 달러가격 업데이트 주기, 15분
WALLET_STATUS_UPDATE = 60 * 30  # 입출금가능상태 업데이트 주기, 30분
COMPARE_PRICE_DELAY = 10   # 가격비교 최초 실행대기, 10초
TIME_DIFF_CHECK_DELAY = 30 * 60      # 바이낸스 서버와 시간비교 주기, 30분