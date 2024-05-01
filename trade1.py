import json
import logging
import datetime
import time
import yaml
import model
import common
import database
import util
import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
# 로깅 설정
with open('config.yaml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)
APP_KEY = _cfg['APP_KEY']
APP_SECRET = _cfg['APP_SECRET']
ACCESS_TOKEN = ""
CANO = _cfg['CANO']
ACNT_PRDT_CD = _cfg['ACNT_PRDT_CD']
DISCORD_WEBHOOK_URL = _cfg['DISCORD_WEBHOOK_URL']
URL_BASE = _cfg['URL_BASE']

async def send_message(msg):
    """디스코드 메세지 전송 (비동기)"""
    now = datetime.datetime.now()
    message = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {str(msg)}"}
    async with aiohttp.ClientSession() as session:
        async with session.post(DISCORD_WEBHOOK_URL, data=message) as response:
            if response.status != 204:
                raise Exception(f"Failed to send message, status code: {response.status}")
            print(message)

async def get_access_token():
    """토큰 발급 (비동기)"""
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    url = f"{URL_BASE}/oauth2/tokenP"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=body) as response:
            if response.status == 200:
                res = await response.json()
                return res["access_token"]
            else:
                raise Exception(f"Failed to get access token, status code: {response.status}")

    
async def hashkey(datas):
    """암호화 (비동기)"""
    url = f"{URL_BASE}/uapi/hashkey"
    headers = {
        'Content-Type': 'application/json',
        'appKey': APP_KEY,
        'appSecret': APP_SECRET,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=datas) as response:
            if response.status == 200:
                res = await response.json()
                return res["HASH"]
            else:
                raise Exception(f"Failed to generate hashkey, status code: {response.status}")


async def get_price(code="005930"):
    """현재가 조회 (비동기)"""
    url = f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id": "FHKST01010100"
    }
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": code
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                res = await response.json()
                current_price = int(res['output']['stck_prpr'])
                high_price = int(res['output']['stck_hgpr'])
                low_price = int(res['output']['stck_lwpr'])
                return current_price, high_price, low_price
            else:
                raise Exception(f"Failed to retrieve stock prices, status code: {response.status}")


async def get_target_price(code="005930"):
    """변동성 돌파 전략으로 매수 목표가 조회 (비동기)"""
    url = f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-daily-price"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id": "FHKST01010400"
    }
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": code,
        "fid_org_adj_prc": "1",
        "fid_period_div_code": "D"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                res = await response.json()
                stck_oprc = int(res['output'][0]['stck_oprc'])  # 오늘 시가
                stck_hgpr = int(res['output'][1]['stck_hgpr'])  # 전일 고가
                stck_lwpr = int(res['output'][1]['stck_lwpr'])  # 전일 저가
                target_price = stck_oprc + (stck_hgpr - stck_lwpr) * 0.5
                return target_price, stck_oprc
            else:
                raise Exception(f"Failed to retrieve target price, status code: {response.status}")

async def get_stock_balance():
    """주식 잔고조회 (비동기)"""
    url = f"{URL_BASE}/uapi/domestic-stock/v1/trading/inquire-balance"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id": "TTTC8434R",
        "custtype": "P",
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "01",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                res = await response.json()
                stock_list = res['output1']
                evaluation = res['output2']
                stock_dict = {}
                for stock in stock_list:
                    if int(stock['hldg_qty']) > 0:
                        stock_dict[stock['pdno']] = {'name': stock['prdt_name'], 'qty': int(stock['hldg_qty']), 'price': int(float(stock['pchs_avg_pric']))}
                # Async call to send_message, needs to be defined or adapted for asynchronous handling
                await send_message(f"====주식 보유잔고====")
                await send_message(f"주식 평가 금액: {evaluation[0]['scts_evlu_amt']}원")
                await send_message(f"평가 손익 합계: {evaluation[0]['evlu_pfls_smtl_amt']}원")
                await send_message(f"총 평가 금액: {evaluation[0]['tot_evlu_amt']}원")
                await send_message(f"=================")
                return stock_dict
            else:
                raise Exception(f"Failed to retrieve stock balance, status code: {response.status}")

async def get_balance():
    """현금 잔고조회 (비동기)"""
    url = f"{URL_BASE}/uapi/domestic-stock/v1/trading/inquire-psbl-order"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id": "TTTC8908R",
        "custtype": "P"
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": "005930",
        "ORD_UNPR": "65500",
        "ORD_DVSN": "01",
        "CMA_EVLU_AMT_ICLD_YN": "Y",
        "OVRS_ICLD_YN": "Y"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                res = await response.json()
                cash = int(res['output']['ord_psbl_cash'])  # 주문가능현금잔고
                amt_cash = int(res['output']['ruse_psbl_amt'])  # 재사용가능잔고
                cash = cash + amt_cash
                await send_message(f"매수가능금액: {cash}원")  # 거래가능잔고
                return cash
            else:
                raise Exception(f"Failed to retrieve balance, status code: {response.status}")
            
async def buy(code="005930", qty="1"):
    """주식 시장가 매수 (비동기)"""
    path = "uapi/domestic-stock/v1/trading/order-cash"
    url = f"{URL_BASE}/{path}"
    hash_key = await hashkey({
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "01",
        "ORD_QTY": str(int(qty)),
        "ORD_UNPR": "0",
    })
    data = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "01",
        "ORD_QTY": str(int(qty)),
        "ORD_UNPR": "0",
        "hashkey": hash_key
    }
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id": "TTTC0802U",
        "custtype": "P"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            res = await response.json()
            if res['rt_cd'] == '0':
                await send_message(f"[매수 성공]{str(res)}")
                return True
            else:
                await send_message(f"[매수 실패]{str(res)}")
                return False

async def sell(code="005930", qty="1"):
    """주식 시장가 매도 (비동기)"""
    path = "uapi/domestic-stock/v1/trading/order-cash"
    url = f"{URL_BASE}/{path}"
    hash_key = await hashkey({
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "01",
        "ORD_QTY": qty,
        "ORD_UNPR": "0",
    })
    data = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "01",
        "ORD_QTY": qty,
        "ORD_UNPR": "0",
        "hashkey": hash_key
    }
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id": "TTTC0801U",
        "custtype": "P"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            res = await response.json()
            if res['rt_cd'] == '0':
                await send_message(f"[매도 성공]{str(res)}")
                return True
            else:
                await send_message(f"[매도 실패]{str(res)}")
                return False

async def get_access_token_if_needed():
    """Token retrieval or update, done asynchronously."""
    now = datetime.datetime.now().date()
    if await common.istoken():  # Assuming istoken is an async function now
        token = await common.read('token')[-1]  # Assuming read is adapted to be async
        if token[0] == str(now):
            access_token = token[1]
            print('Token loaded')
        else:
            access_token = await get_access_token()
            await common.write('token', str(now), access_token)  # Assuming write is async
            print('Token exists, reissued')
    else:
        access_token = await get_access_token()
        await common.write('token', str(now), access_token)  # Assuming write is async
        print('Token created and issued')

    return access_token

async def iscode(sym):
    query_data = await database.queryByField('trades', 'code', sym)
    if len(query_data) > 0:
        return True
    return False



async def decide_transaction(sym, start_price, current_price, buy_price, high_price):
    if buy_price != 0:
        percent = ((current_price - buy_price) / buy_price) * 100
        
        # 손실률에 따른 매도 조건
        if percent <= -5:
            return 'buy', 0.3
        elif percent <= -3:
            return 'sell', 0.5
        elif percent <= -2:
            return 'sell', 0.2
        elif percent <= -1.7:
            return 'sell', 0.1
        
        # 수익률에 따른 매도 조건
        elif percent >= 3:
            return 'sell', 0.3 
        elif percent >= 2:
            return 'sell', 0.15
        elif percent >= 1.5:
            return 'sell', 0.1
        elif percent >= 1:
            return 'sell', 0.1
        
    else:
        # 초기 매수
        return 'buy', 0.2

    return 'hold', 0.0  # 해당 조건 없을 때 홀드

# 로깅 설정 초기화
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(threadName)s - %(message)s',
                    filename='logfile.log')
async def handle_stock_transaction(sym, name, have_qty, start_price, current_price, buy_price, high_price):
    global stock_dict
    decision, percent = await decide_transaction(sym, start_price, current_price, buy_price, high_price)
    
    if decision == "sell":
        profit = current_price - buy_price
        profit_desc = '수익' if profit > 0 else '손실'
        sell_qty = have_qty if percent == 1.0 else max(int(have_qty * percent), 1)

        if await sell(sym, sell_qty):
            sell_amount = profit * sell_qty
            logging.info(f'*** {("전량" if percent == 1.0 else "분할")}매도 *** {sym} - {profit_desc}, 매도금액: {sell_amount}원, 매도수량: {sell_qty}')
            if percent == 1.0:
                await database.deleteData('trades', "code", sym)
            else:
                await database.updateData('trades', {'qty': have_qty - sell_qty}, "code", sym)
        else:
            logging.error(f'매도 실패: {sym}')

    elif decision == "buy":
        buy_qty = max(int((have_qty * percent) // current_price), 1)
        if await buy(sym, buy_qty):
            stock_dict = await get_stock_balance()
            have_qty = stock_dict.get(sym, {}).get('qty', 0)
            buy_price = stock_dict.get(sym, {}).get('price', 0)
            if await iscode(sym):
                await database.deleteData('trades', "code", sym)
            await database.insertData('trades', {
                'code': sym,
                'trade_date': str(datetime.datetime.now().date()),
                'buy_price': buy_price,
                'sell_price': 0,
                'start_price': start_price,
                'high_price': high_price,
                'qty': buy_qty
            })
            logging.info(f'매수 성공: {sym} - 매수수량: {buy_qty}, 매수가격: {buy_price}원')
        else:
            logging.error(f'매수 실패: {sym}')

    else:
        logging.info(f"{sym} {name} 주식 거래 보류: 현재 가격 {current_price}원, 매수가격: {buy_price}원, 보유수량: {have_qty}, 예상금액: {(current_price - buy_price) * have_qty}원")
        await database.updateData('trades', {'qty': have_qty, 'buy_price': buy_price, 'sell_price': current_price, 'high_price': high_price}, "code", sym)

async def symbol_list_load(isai):
    if isai:
        sym_list = await model.buy_companies()  # Assume this now performs async operations
    else:
        sym_list = await database.codes()  # Assume this is also converted to async
    return sym_list
        

async def buy_amount_load(count):
    if count == 0:
        return 0
    cash = await get_balance()  # Directly await the asynchronous version of get_balance
    percent = 1.0 / count
    amount = cash * percent
    return amount


async def gen_time():
    t_now = datetime.datetime.now()
    t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
    t_start = t_now.replace(hour=9, minute=1, second=0, microsecond=0)
    t_ai = t_now.replace(hour=9, minute=30, second=0,microsecond=0)
    t_sell = t_now.replace(hour=15, minute=15, second=0, microsecond=0)
    t_exit = t_now.replace(hour=15, minute=20, second=0,microsecond=0)
    return t_9,t_start,t_sell,t_exit,t_ai

async def total_sell():
    stock_dict = await get_stock_balance()  # Assume get_stock_balance is now an async function
    syms = stock_dict.keys()
    for sym in syms:
        have_qty = stock_dict[sym]['qty']
        await sell(sym, have_qty)  # Assume sell is now an async function
        await database.deleteData('trades', 'code', sym)  # Assume deleteData is now an async function
    await asyncio.sleep(1)  # Sleep if necessary, although typically you might not need this in an async workflow


async def isweekday():
    today = datetime.datetime.today().weekday()
    if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
        await asyncio.sleep(.1)
        return True
    return False

async def stock_buy():
    global symbol_list, stock_dict, target_buy_count, t_ai, t_now, t_sell, stocks_to_trade, buy_amount
    stocks_to_trade = []
    for sym in symbol_list:
        current_stock_count = len(stock_dict)
        if current_stock_count >= target_buy_count:
            break
        if await iscode(sym):
            continue
        print('*** 매수체결 시도 ***')
        target_price, start_price = await get_target_price(sym)
        current_price, high_price, low_price = await get_price(sym)
        if t_ai < t_now < t_sell: 
            if target_price < current_price:
                stocks_to_trade.append((sym, '', 0, buy_amount, current_price, 0, high_price))
        else:
            stocks_to_trade.append((sym, '', buy_amount, start_price, current_price, 0, high_price))

async def stock_sell():
    global stock_dict, stocks_to_trade
    stocks_to_trade = []
    syms = stock_dict.keys()
    for sym in syms:
        have_qty = stock_dict[sym]['qty']
        buy_price = stock_dict[sym]['price']
        name = stock_dict[sym]['name']
        start_price, current_price, high_price, low_price = await get_price(sym)
        stocks_to_trade.append((sym, name, have_qty, start_price, current_price, buy_price, high_price))


async def main():
    global ACCESS_TOKEN, symbol_list, stock_dict, buy_amount, stocks_to_trade
    try:
        isweek = await asyncio.to_thread(isweekday)
        if isweek:
            await send_message("주말이므로 프로그램을 종료합니다.")
            return

        ACCESS_TOKEN = await get_access_token_if_needed()
        isAi = False  # 인공지능: True, 다음 순위: False 9시에서 9시30분까지는 피크타임 적용 다음으로
        target_buy_count = 3  # 주식거래 종목수 설정
        t_9, t_start, t_sell, t_exit, t_ai = await gen_time()  # 거래시간대별 계산

        await send_message("===국내 주식 자동매매 프로그램을 시작합니다===")
        while True:
            stocks_to_trade = []
            t_now = datetime.datetime.now()

            if t_9 < t_now < t_start:  # 잔여 수량 매도
                await total_sell()

            if t_ai < t_now < t_sell:
                isAi = True  # 인공지능: True

            if t_start < t_now < t_sell:  # AM 09:05 ~ PM 03:15 : 매수
                stock_dict = await get_stock_balance()
                if not stock_dict:
                    symbol_list = await symbol_list_load(isAi)
                    buy_amount = await buy_amount_load(len(symbol_list))

                if len(stock_dict) < target_buy_count:
                    await stock_buy()
                else:
                    await stock_sell()
                await asyncio.gather(*(handle_stock_transaction(sym, name, have_qty, start_price, current_price, buy_price, high_price)
                                        for sym, name, have_qty, start_price, current_price, buy_price, high_price in stocks_to_trade))
                await asyncio.sleep(1)

                if t_now.minute == 30 and t_now.second <= 5:
                    stock_dict = await get_stock_balance()
                    await asyncio.sleep(5)

            if t_sell < t_now < t_exit:  # PM 03:15 ~ PM 03:20 : 일괄 매도
                await total_sell()

            if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
                await send_message("프로그램을 종료합니다.")
                break
    except Exception as e:
        await send_message(f"[오류 발생]{e}")
        await asyncio.sleep(1)

symbol_list = None
stock_dict = None
buy_amount = None
stocks_to_trade = None
ACCESS_TOKEN = None

if __name__ == "__main__":
    asyncio.run(main())
