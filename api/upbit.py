import traceback
from consts import *
import util
import asyncio
import websockets
import json
import socket
from datetime import datetime
import uuid

exchange = UPBIT


async def connect_socket(exchange_price):
    """
    UPBIT 소켓연결 후 실시간 가격까지 저장하는 함수
    :param exchange_price: 거래소별 가격 데이터를 저장할 딕셔너리
    :return: None
    """
    global exchange
    while True:
        try:
            util.send_to_telegram('[{}] Creating new connection..'.format(exchange))
            start_time = datetime.now()
            util.clear_exchange_price(exchange, exchange_price)

            async with websockets.connect('wss://api.upbit.com/websocket/v1', ping_interval=None, ping_timeout=30,
                                          max_queue=10000) as websocket:
                subscribe_fmt = [
                    {'ticket': str(uuid.uuid4())[:6]},
                    {
                        'type': 'orderbook',
                        'codes': ['KRW-AERGO'],
                        'isOnlyRealtime': True
                    },
                ]
                subscribe_data = json.dumps(subscribe_fmt)
                await websocket.send(subscribe_data)

                while True:
                    try:
                        data = await websocket.recv()
                        data = json.loads(data)

                        if 'code' not in data:  # 응답 데이터(딕셔너리)에 code가 없는 경우 제외
                            print("[Data error]", data)
                            continue

                        ticker = data['code'].split('-')[1]  # KRW-BTC > BTC(시세조회대상 코인)

                        if ticker not in exchange_price:
                            exchange_price[ticker] = {exchange: None}

                        if data['code'].split('-')[0] == "KRW":
                            orderbook_units = data['orderbook_units'][:1]

                            # 특정 값을 계산하고 딕셔너리에 저장
                            ask_price = float(orderbook_units[0]['ask_price'])
                            bid_price = float(orderbook_units[0]['bid_price'])
                            ask_size = orderbook_units[0]['ask_size']
                            bid_size = orderbook_units[0]['bid_size']
                            exchange_price[ticker][exchange] = {'ask_price': ask_price, 'bid_price': bid_price,
                                                                'ask_size': ask_size, 'bid_size': bid_size}

                        if util.is_need_reset_socket(start_time):  # 매일 아침 9시 소켓 재연결
                            util.send_to_telegram('[{}] Time to new connection...'.format(exchange))
                            break

                    except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed):
                        try:
                            util.send_to_telegram('[{}] Ping OK, keeping connection alive...'.format(exchange))
                            pong = await websocket.ping()

                            await asyncio.wait_for(pong, timeout=SOCKET_PING_TIMEOUT)
                        except:
                            util.send_to_telegram(
                                '[{}] Ping error. retrying connection'.format(exchange, SOCKET_RETRY_TIME))
                            await asyncio.sleep(SOCKET_RETRY_TIME)
                            break
                    except:
                        print(traceback.format_exc())
                await websocket.close()
        except socket.gaierror:
            util.send_to_telegram('[{}}] Socket error - retrying connection in {} sec (Ctrl-F2 to quit)'.format(exchange, SOCKET_RETRY_TIME))
            await asyncio.sleep(SOCKET_RETRY_TIME)
        except ConnectionRefusedError:
            util.send_to_telegram('[{}}] Retrying connection in {} sec (Ctrl-F2 to quit)'.format(exchange, SOCKET_RETRY_TIME))
            await asyncio.sleep(SOCKET_RETRY_TIME)



if __name__ == "__main__":
    exchange_price = {}
    asyncio.run(connect_socket(exchange_price))
