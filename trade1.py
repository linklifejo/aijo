import json
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
with open('config.yaml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)
APP_KEY = _cfg['APP_KEY']
APP_SECRET = _cfg['APP_SECRET']
ACCESS_TOKEN = ""
CANO = _cfg['CANO']
ACNT_PRDT_CD = _cfg['ACNT_PRDT_CD']
DISCORD_WEBHOOK_URL = _cfg['DISCORD_WEBHOOK_URL']
URL_BASE = _cfg['URL_BASE']

def send_message(msg):
    """디스코드 메세지 전송"""
    now = datetime.datetime.now()
    message = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {str(msg)}"}
    requests.post(DISCORD_WEBHOOK_URL, data=message)
    print(message)

def get_access_token():
    """토큰 발급"""
    headers = {"content-type":"application/json"}
    body = {"grant_type":"client_credentials",
    "appkey":APP_KEY, 
    "appsecret":APP_SECRET}
    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    ACCESS_TOKEN = res.json()["access_token"]
    return ACCESS_TOKEN
    
def hashkey(datas):
    """암호화"""
    PATH = "uapi/hashkey"
    URL = f"{URL_BASE}/{PATH}"
    headers = {
    'content-Type' : 'application/json',
    'appKey' : APP_KEY,
    'appSecret' : APP_SECRET,
    }
    res = requests.post(URL, headers=headers, data=json.dumps(datas))
    hashkey = res.json()["HASH"]
    return hashkey

def get_price(code="005930"):
    """현재가 조회"""
    PATH = "uapi/domestic-stock/v1/quotations/inquire-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
            "authorization": f"Bearer {ACCESS_TOKEN}",
            "appKey":APP_KEY,
            "appSecret":APP_SECRET,
            "tr_id":"FHKST01010100"}
    params = {
    "fid_cond_mrkt_div_code":"J",
    "fid_input_iscd":code,
    }
    res = requests.get(URL, headers=headers, params=params)
    start_price = int(res.json()['output']['stck_oprc'])
    current_price = int(res.json()['output']['stck_prpr'])
    high_price = int(res.json()['output']['stck_hgpr'])
    low_price = int(res.json()['output']['stck_lwpr'])
    return start_price, current_price, high_price, low_price

def get_target_price(code="005930"):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    PATH = "uapi/domestic-stock/v1/quotations/inquire-daily-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"FHKST01010400"}
    params = {
    "fid_cond_mrkt_div_code":"J",
    "fid_input_iscd":code,
    "fid_org_adj_prc":"1",
    "fid_period_div_code":"D"
    }
    res = requests.get(URL, headers=headers, params=params)
    stck_oprc = int(res.json()['output'][0]['stck_oprc']) #오늘 시가
    stck_hgpr = int(res.json()['output'][1]['stck_hgpr']) #전일 고가
    stck_lwpr = int(res.json()['output'][1]['stck_lwpr']) #전일 저가
    target_price = stck_oprc + (stck_hgpr - stck_lwpr) * 0.5
    return target_price

def get_stock_balance():
    """주식 잔고조회"""
    PATH = "uapi/domestic-stock/v1/trading/inquire-balance"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC8434R",
        "custtype":"P",
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
    res = requests.get(URL, headers=headers, params=params)
    stock_list = res.json()['output1']
    evaluation = res.json()['output2']
    stock_dict = {}
    send_message(f"====주식 보유잔고====")
    for stock in stock_list:
        if int(stock['hldg_qty']) > 0:
            stock_dict[stock['pdno']] = {int(stock['hldg_qty']), int(stock['pchs_avg_pric'])}
            send_message(f"{stock['prdt_name']}({stock['pdno']})에 대한 보유주식수는 {stock['hldg_qty']}주 이며, 매수단가는 {stock['pchs_avg_pric']}원 입니다.")
            time.sleep(0.1)
    send_message(f"주식 평가 금액: {evaluation[0]['scts_evlu_amt']}원")
    time.sleep(0.1)
    send_message(f"평가 손익 합계: {evaluation[0]['evlu_pfls_smtl_amt']}원")
    time.sleep(0.1)
    send_message(f"총 평가 금액: {evaluation[0]['tot_evlu_amt']}원")
    time.sleep(0.1)
    send_message(f"=================")
    return stock_dict

def get_balance():
    """현금 잔고조회"""
    PATH = "uapi/domestic-stock/v1/trading/inquire-psbl-order"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC8908R",
        "custtype":"P",
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
    res = requests.get(URL, headers=headers, params=params)
    # cash = int(res.json()['output']['max_buy_amt']) / 2
    # send_message(f"매수가능금액: {cash}원") # 미수거래가능잔고
    cash = res.json()['output']['ord_psbl_cash'] # 주문가능현금잔고
    amt_cash = res.json()['output']['ruse_psbl_amt'] # 재사용가능잔고
    cash = int(cash) + int(amt_cash)
    send_message(f"매수가능금액: {cash}원") # 거래가능잔고

    return int(cash)

def buy(code="005930", qty="1"):
    """주식 시장가 매수"""  
    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"
    data = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "01",
        "ORD_QTY": str(int(qty)),
        "ORD_UNPR": "0",
    }
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC0802U",
        "custtype":"P",
        "hashkey" : hashkey(data)
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    if res.json()['rt_cd'] == '0':
        send_message(f"[매수 성공]{str(res.json())}")
        return True
    else:
        send_message(f"[매수 실패]{str(res.json())}")
        return False

def sell(code="005930", qty="1"):
    """주식 시장가 매도"""
    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"
    data = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "01",
        "ORD_QTY": qty,
        "ORD_UNPR": "0",
    }
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC0801U",
        "custtype":"P",
        "hashkey" : hashkey(data)
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    if res.json()['rt_cd'] == '0':
        send_message(f"[매도 성공]{str(res.json())}")
        return True
    else:
        send_message(f"[매도 실패]{str(res.json())}")
        return False

def get_access_token_if_needed():
    """토큰을 가져오거나 업데이트합니다."""
    now = datetime.datetime.now().date()
    if common.istoken():
        token = common.read('token')[-1]
        if token[0] == str(now):
            ACCESS_TOKEN = token[1]
            print('로드')
        else:
            ACCESS_TOKEN = get_access_token()
            common.write('token', str(now), ACCESS_TOKEN)
            print('파일 존재하고, 발급')
    else:
        ACCESS_TOKEN = get_access_token()
        common.write('token', str(now), ACCESS_TOKEN)
        print('파일 생성하고, 발급')

    return ACCESS_TOKEN
def get_trade_info(sym):
    query_data = database.queryByField('trades', 'code', sym)
    if len(query_data) > 0:
        for index, row in query_data.iterrows():
            qty = row['qty']
            buy_price = row['buy_price']
            sell_price = row['sell_price']
            high_price = row['high_price']
            start_price = row['start_price']
        return qty, buy_price, sell_price, start_price, high_price
    return None, None, None,None,None


async def decide_transaction(sym, start_price, current_price, buy_price, high_price):
    if buy_price != 0:
        percent = ((current_price - buy_price) / buy_price) * 100
        
        # 손실률에 따른 매도 조건
        if percent <= -5:
            return 'buy', 0.3
        elif percent <= -2.8:
            return 'sell', 1.0
        elif percent <= -1.8:
            return 'sell', 0.5
        elif percent <= -1.5:
            return 'sell', 0.3
        
        # 수익률에 따른 매도 조건
        elif percent >= 3:
            return 'sell', 0.3 
        elif percent >= 2:
            return 'sell', 0.15
        elif percent >= 1:
            return 'sell', 0.1
         
        # 최고가의 범위에 따른 매도 조건
        if current_price >= high_price - (high_price * .01) or current_price >= high_price + (high_price * .031):
            return 'sell', 1.0
        
    else:
        # 초기 매수
        return 'buy', 0.2

    return 'hold', 0.0  # 해당 조건 없을 때 홀드



# 주식 거래 처리 함수
async def handle_stock_transaction(sym, have_qty, start_price, current_price, buy_price, high_price):
    decision,percent = await decide_transaction(sym, start_price,current_price, buy_price, high_price)
    if decision == "sell":
                # util.clear()
        r =current_price - buy_price
        if r > 0:
            rstring = '수익'
        else:
            rstring = '손실'
        if percent == 1.0:  # 전량매도
            result = await asyncio.to_thread(sell,sym, have_qty)
            if result:
                sell_amount = r * have_qty
                print(f'*** 전량매도 *** {rstring} 이며, {sell_amount} 원 입니다. 매도수량은 {have_qty} 입니다.')
                database.deleteData('trades', "code", sym)
            else:  # 분할매도
                if have_qty > 1:
                    sell_qty = have_qty * percent  # 분할 매도할 수량 계산
                    if sell_qty == 0:
                        sell_qty =1
                    result = await asyncio.to_thread(sell,sym, sell_qty)
                    if result:
                        sell_amount = r * sell_qty
                        print(f'*** 분할매도 *** {rstring} 이며, {sell_amount} 원 입니다. 매도수량은{sell_qty} 입니다.')
                        if current_price > high_price:
                            high_price = current_price
                        await asyncio.to_thread(database.updateData,'trades', {'qty':have_qty - sell_qty})
    elif decision == "buy":
        # global buy_amount
        buy_amount =start_price # 매수인경우만 중요~~
        buy_qty = int(buy_amount * percent //current_price)  # 분할 매수수량 계산
        if buy_qty > 0:
            result = await asyncio.to_thread(buy,sym, buy_qty)
            if result:
                stock_dict = get_stock_balance()
                stock_dict = await asyncio.to_thread(get_stock_balance)
                syms = stock_dict.keys()
                for sym in syms:
                    have_qty = stock_dict[sym]['qty']
                    buy_price = stock_dict[sym]['price']

                if current_price > high_price:
                    high_price = current_price
                    qty, _,_,_,_ = get_trade_info(sym)
                    if qty is None:
                       await asyncio.to_thread(database.insertData,'trades',
                        {
                        'code': sym,
                        'trade_date': str(datetime.datetime.now().date()),
                        'buy_price': buy_price,
                        'sell_price': 0,
                        'start_price': start_price,
                        'high_price': current_price,
                        'qty': buy_qty
                        })   
                    else:
                        await asyncio.to_thread(database.updateData,'trades', {'qty':have_qty,'buy_price':buy_price,'sell_price':current_price,'high_price':high_price}, "code", sym)
    else:
        print(f"{sym} 주식 거래 보류: 현재 가격 {current_price}.")

async def main():
    global ACCESS_TOKEN
    # 자동매매 시작
    try:
        isAi = False
        ACCESS_TOKEN = await asyncio.to_thread(get_access_token_if_needed)
        total_cash = await asyncio.to_thread(get_balance)
        stock_dict = await asyncio.to_thread(get_stock_balance)
        target_buy_count = 3 
        if isAi:
            symbol_list = await asyncio.to_thread(model.buy_companies) #인공지능
            buy_percent = 1.0 / target_buy_count
            buy_amount = total_cash * buy_percent
        else:
            symbol_list = await asyncio.to_thread(database.codes) 
            buy_percent = 1.0 / target_buy_count
            buy_amount = total_cash * buy_percent

        await asyncio.to_thread(send_message,"===국내 주식 자동매매 프로그램을 시작합니다===") 
        while True:
            t_now = datetime.datetime.now()
            t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
            t_start = t_now.replace(hour=9, minute=1, second=0, microsecond=0)
            t_sell = t_now.replace(hour=15, minute=15, second=0, microsecond=0)
            t_exit = t_now.replace(hour=15, minute=20, second=0,microsecond=0)
            today = datetime.datetime.today().weekday()
            if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
                await asyncio.to_thread(send_message,"주말이므로 프로그램을 종료합니다.") 
                break
            if t_9 < t_now < t_start: # 잔여 수량 매도
                stock_dict = await asyncio.to_thread(get_stock_balance)
                for sym, qty in stock_dict.items():
                    await asyncio.to_thread(sell,sym,qty)
            if t_start < t_now < t_sell :  # AM 09:05 ~ PM 03:15 : 매수
                stocks_to_trade = []
                if len(stock_dict) < target_buy_count:
                    for sym in symbol_list:
                        print('추천주식수:',len(symbol_list))
                        if len(stock_dict) == target_buy_count:
                            break
                        if sym in stock_dict.keys():
                            continue
                        else:
                            print('매수체결 시도 ... !!!')
                            target_price = get_target_price(sym)
                            start_price,current_price,high_price,low_price = await asyncio.to_thread(get_price,sym)
                            if target_price < current_price:
                                # 매수인경우만 buy_amount를 보냄 중요~
                                stocks_to_trade.append((sym,0,buy_amount,current_price,0,high_price))
                else:
                    syms = stock_dict.keys()
                    for sym in syms:
                        have_qty = stock_dict[sym]['qty']
                        buy_price = stock_dict[sym]['price']
                        start_price,current_price,high_price,low_price = await asyncio.to_thread(get_price)
                        stocks_to_trade.append((sym,have_qty,start_price,current_price,buy_price,high_price))
            
                # 각 주식 거래를 비동기적으로 처리
                if len(stocks_to_trade) > 0:
                    await asyncio.gather(*(handle_stock_transaction(sym, have_qty,start_price, current_price, buy_price, high_price) 
                                    for sym, have_qty,start_price, current_price, buy_price, high_price in stocks_to_trade))                
                
                await asyncio.sleep(1)

                if t_now.minute == 1 and t_now.second <= 5: 
                    stock_dict = await asyncio.to_thread(get_stock_balance)
                    await asyncio.sleep(5)

            if t_sell < t_now < t_exit:  # PM 03:15 ~ PM 03:20 : 일괄 매도

                stock_dict = await asyncio.to_thread(get_stock_balance)
                for sym, qty in stock_dict.items():
                    await asyncio.to_thread(sell,sym,qty)
                    await asyncio.to_thread(database.deleteData,'trades','code',sym)
                await asyncio.sleep(1)
                
            if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
                await asyncio.to_thread(send_message,"프로그램을 종료합니다.") 
                break
    except Exception as e:
        await asyncio.to_thread(send_message,f"[오류 발생]{e}") 
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
