import requests
import json
import datetime
import time
import yaml
import model
import common
import database
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

def get_current_price(code="005930"):
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
    return int(res.json()['output']['stck_prpr'])

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
    return target_price, stck_oprc

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
            stock_dict[stock['pdno']] = stock['hldg_qty']
            send_message(f"{stock['prdt_name']}({stock['pdno']}): {stock['hldg_qty']}주")
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
    cash = res.json()['output']['ord_psbl_cash']
    send_message(f"주문 가능 현금 잔고: {cash}원")
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
# 판단 : 매도
# 매도 인경우 : 종목코드,시가,매도가,시장가,수량
# 1번매도 : 현재가 시가보다 작으면 전량매도(보유수량)
# 2번매도 : 현재가 매입가 대비 5퍼 오른경우 보유수량의 30퍼 매도
# 3번매도 : 현재가 고가 대비 2퍼 하락한경우 보유수량의 50퍼 매도
# 4번매도 : 현재가 고가 대비 3퍼 하락한경우 보유수량의 전량매도
# 시장가(현재가) : current_price
# 시가   : start_price
# 고가   : high_price
# 매수가 : buy_price
# 매도가 : sell_price
# code,qty,start_price,buy_price,high_price
def decision(current_price, buy_price, start_price, high_price):
    if current_price < start_price:
        return 'sell', 100
    elif current_price > buy_price:
        up_price = buy_price + (buy_price * .05)
        if current_price >= up_price:
            return 'sell', 30
    elif current_price < high_price:
        low_price = high_price - (high_price * .02)
        if current_price == low_price:
            return 'sell', 50
        low_price = high_price - (high_price * .03)
        if current_price == low_price:
            return 'sell', 100
    return None, 0  # 매도하지 않는 경우 None과 0 반환

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

def get_trade_amount(sym):
    qty, buy_price,sell_price, start_price,high_price = get_trade_info(sym)
    if qty is not None:
       query_amount = qty * buy_price
       return query_amount, buy_price
    return None, None
def get_buy_quty(sym):
    global buy_amount
    buy_qty = 0  # 매수할 수량 초기화
    target_price,start_price = get_target_price(sym)
    current_price = get_current_price(sym)
    query_amount, _ = get_trade_amount(sym) 
    if target_price < current_price:
        buy_qty = int(buy_amount * 0.1 // current_price)  # 10%의 비율로 매수
        if buy_qty > 0 and buy_amount > query_amount:
            send_message(f"{sym} 목표가 달성({target_price} < {current_price}) 매수를 시도합니다.")
            return buy_qty, start_price
    return buy_qty, start_price, current_price

# 자동매매 시작
try:
    # symbol_list = ["005930","035720","000660","069500"] # 매수 희망 종목 리스트
    # 변수 초기화
    bought_list = [] # 매수 완료된 종목 리스트
    ACCESS_TOKEN = get_access_token_if_needed()
    symbol_list = model.buy_companies()
    total_cash = get_balance() # 보유 현금 조회
    stock_dict = get_stock_balance() # 보유 주식 조회
    for sym in stock_dict.keys():
        bought_list.append(sym)
    target_buy_count = 3 # 매수할 종목 수
    buy_percent = 0.33 # 종목당 매수 금액 비율
    buy_amount = total_cash * buy_percent  # 종목별 주문 금액 계산
    soldout = False

    send_message("===국내 주식 자동매매 프로그램을 시작합니다===")
    while True:
        t_now = datetime.datetime.now()
        t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
        t_start = t_now.replace(hour=9, minute=5, second=0, microsecond=0)
        t_sell = t_now.replace(hour=15, minute=15, second=0, microsecond=0)
        t_exit = t_now.replace(hour=15, minute=20, second=0,microsecond=0)
        today = datetime.datetime.today().weekday()
        if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
            send_message("주말이므로 프로그램을 종료합니다.")
            break
        if t_9 < t_now < t_start and soldout == False: # 잔여 수량 매도
            for sym, qty in stock_dict.items():
                sell(sym, qty)
            soldout == True
            bought_list = []
            stock_dict = get_stock_balance()
        if t_start < t_now < t_sell:  # AM 09:05 ~ PM 03:15 : 매수 및 매도
            if len(bought_list) < target_buy_count:
                for sym in symbol_list:
                    buy_qty, start_price, current_price = get_buy_quty(sym)
                    if buy_qty > 0:
                        result = buy(sym, buy_qty)
                        if result:
                            database.insertData('trades', {
                            'code': sym,
                            'trade_date': str(datetime.datetime.now().date()),
                            'buy_price': current_price,
                            'sell_price': 0,
                            'start_price': start_price,
                            'high_price': current_price,
                            'qty': buy_qty
                            })
                            # 종목 정보 저장
                            soldout = False
                            bought_list.append(sym)
                            get_stock_balance()
                    time.sleep(1)
                time.sleep(1)
            if t_now.minute == 30 and t_now.second <= 5: 
                get_stock_balance()
                time.sleep(5)

            if soldout == False:
                for sym in bought_list:  # 매수 완료된 종목에 대해서만 매도 진행
                    current_price = get_current_price(sym)
                    qty, buy_price,sell_price, start_price,high_price = get_trade_info(sym)
                    if qty is not None:
                        action, sell_qty = decision(current_price, buy_price, start_price, high_price)
                        if action == 'sell' and sell_qty > 0:
                            if sell_qty == 100:  # 전량매도
                                sell(sym, qty)
                                database.deleteData('trades', "code", sym)
                            else:  # 분할매도
                                if qty > 1:
                                    sell_amount = int(qty * sell_qty / 100)  # 분할 매도할 수량 계산
                                else:
                                    sell_amount = 1
                                sell(sym, sell_amount)
                                database.updateData('trades', {'sell_price': current_price,'high_price': high_price,'qty': qty - sell_amount}, "code", sym)
                        else:
                            if current_price > high_price:
                                database.updateData('trades', {'high_price': high_price}, "code", sym)

                if len(bought_list) == 0:
                    soldout = True
                time.sleep(1)
                
        if t_sell < t_now < t_exit:  # PM 03:15 ~ PM 03:20 : 일괄 매도
            if soldout == False:
                stock_dict = get_stock_balance()
                for sym, qty in stock_dict.items():
                    sell(sym, qty)
                    database.deleteData('trades', "code", sym)
                soldout = True
                bought_list = []
                time.sleep(1)
        if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
            send_message("프로그램을 종료합니다.")
            break
except Exception as e:
    send_message(f"[오류 발생]{e}")
    time.sleep(1)