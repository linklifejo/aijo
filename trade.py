import requests
import json
import datetime
import time
import yaml
import keyboard
import common
from bs4 import BeautifulSoup

with open('config.yaml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)
APP_KEY = _cfg['APP_KEY']
APP_SECRET = _cfg['APP_SECRET']
ACCESS_TOKEN = ""
CANO = _cfg['CANO']
ACNT_PRDT_CD = _cfg['ACNT_PRDT_CD']
DISCORD_WEBHOOK_URL = _cfg['DISCORD_WEBHOOK_URL']
URL_BASE = _cfg['URL_BASE']

def codes():
    COST = 100  #단가
    VOLUME = 2000000 #거래량
    url = 'https://finance.naver.com/sise/sise_rise.naver?sosok=1'

    response = requests.get(url)
    records = []
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html,'html.parser')
        trs = soup.select('table.type_2 tr')
        del trs[0:2]
        
        for tr in trs:
            record = []
            for td in tr.find_all('td'):
                if td.select('a[href]'):
                    code = td.find('a').get('href').split('=')[-1].strip().replace(',','')
                    record.append(code)  
                    name = td.get_text().strip().replace(',','')
                    record.append(name) 
                else:
                    data = td.get_text().strip().replace(',','')
                    if data.isdigit():
                        record.append(int(data))  
                    else:
                        record.append(data) 
            if len(record)>0:
                records.append(record)                 
                

    else : 
        print(response.status_code)
    result =[]
    codes = []

    for record in records:
        if len(record) > 1:
            if record[3] >= COST and record[6] >= VOLUME:
                result.append(record)
                codes.append(record[1])
    return codes

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
    return target_price
def get_starting_price(code="005930"):
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
    return stck_oprc

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

# 종목,시가,시장가,매수가,매수량,매도량,

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
def decision(current_price,buy_price,start_price,high_price):
    if current_price < start_price:
        return 'sell',100
    elif current_price > buy_price:
        up_price = buy_price + (buy_price * .05)
        if current_price >= up_price:
            return 'sell',30
    elif current_price < high_price:
        low_price = high_price - (high_price * .02)
        if current_price == low_price:
            return 'sell',50
        low_price = high_price - (high_price * .03)
        if current_price == low_price:
            return 'sell',100   

# 자동매매 시작
try:
    h = common.Hook()  # 종료 또 데이타 조회 f4,f2: 각각 종료,데이타조회    
    h.start()   # 쓰레드 실행
    now = datetime.datetime.now().date()
    if common.istoken():
        token = common.read('token')[-1]
        if token[0] == str(now):
            ACCESS_TOKEN = token[1]
        else:
            ACCESS_TOKEN = get_access_token()
            common.write('token',str(now) ,ACCESS_TOKEN)
 
    symbol_list = codes() # 매수 희망 종목 리스트
    bought_list = [] # 매수 완료된 종목 리스트   
    bought_price = dict()
    
    total_cash = get_balance() # 보유 현금 조회
    stock_dict = get_stock_balance() # 보유 주식 조회
    for sym in stock_dict.keys():
        bought_list.append(sym)

    target_buy_count = 3 # 매수할 종목 수
    buy_percent = 1.0 / target_buy_count # 종목당 매수 금액 비율
    soldout = False 
    buy_amount = total_cash * buy_percent  # 종목별 주문 금액 계산

    send_message("===국내 주식 자동매매 프로그램을 시작합니다===")
    while True:
        t_now = datetime.datetime.now()
        t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
        t_start = t_now.replace(hour=9, minute=5, second=0, microsecond=0)
        t_sell = t_now.replace(hour=15, minute=15, second=0, microsecond=0)
        t_exit = t_now.replace(hour=15, minute=20, second=0,microsecond=0)
        today = datetime.datetime.today().weekday()
        if h.event == 'f4':  # h.event가 True이면(f4 입력받은 경우) 종료
            break
        if h.event == 'f2':
            stock_list = common.read('trade')
            for l in stock_list:
                print(l)
            h.event=''

        if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
            send_message("주말이므로 프로그램을 종료합니다.")
            break
        if t_9 < t_now < t_start and soldout == False: # 잔여 수량 매도
            for sym, qty in stock_dict.items():
                sell(sym, qty)
                common.write('trade',sym,current_price,-qty,str(now),'sell')
            soldout == True
            bought_list = []
            stock_dict = get_stock_balance()

        if t_start < t_now < t_sell :  # AM 09:05 ~ PM 03:15 : 매수, 매도



            for sym in symbol_list:
                target_price = get_target_price(sym)
                start_price = get_starting_price(sym)
                current_price = get_current_price(sym)                
                if len(bought_list) < target_buy_count:
                    if sym in bought_list:
                        continue

                    if target_price < current_price:
                        buy_qty = 0  # 매수할 수량 초기화
                        buy_qty = int(buy_amount // current_price)
                        buy_qty //= 3
                        
                        if buy_qty > 0:
                            send_message(f"{sym} 목표가 달성({target_price} < {current_price}) 매수를 시도합니다.")
                            result = buy(sym, buy_qty)
                            common.write('trade',sym, current_price, buy_qty, str(now),'buy')
                            if result:
                                soldout = False
                                # bought_list.append(sym)
                                bought = dict()
                                bought['buy_price'] = current_price
                                bought['high_price'] = current_price
                                bought_price[sym] = bought
                                stock_dict = get_stock_balance() # 보유 주식 조회
                                for sym in stock_dict.keys():
                                    bought_list.append(sym)
                                time.sleep(1)
            time.sleep(1)

            for sym in bought_list:
                target_price = get_target_price(sym)
                start_price = get_starting_price(sym)
                current_price = get_current_price(sym)                
                bought = bought_price.get(sym)
                high_price = bought.get('high_price')
                buy_price = bought.get('buy_price')
                sell,per = decision(current_price,buy_price,start_price,high_price)
                if sell:
                   qty = 0  # 보유수량
                   sell_qty = 0
                   qty = stock_dict.get(sym)
                   sell_qty = int(qty * (per / 100))
                #    qty = int(buy_amount // current_price)
                   sell(sym, sell_qty)
                   common.write('trade',sym, current_price, -qty, str(now),'sell')
                   stock_dict = get_stock_balance() # 보유 주식 조회
                   for sym in stock_dict.keys():
                     bought_list.append(sym)                   
                   time.sleep(1)
                else:
                    bought = bought_price.get(sym)
                    if bought:
                        high_price = bought.get('high_price')
                        if current_price > high_price:
                            bought['high_price'] = current_price
                            bought_price[sym] = bought

                    time.sleep(1)
        
            # if t_now.minute == 30 and t_now.second <= 5: 
            #     stock_dict = get_stock_balance() # 보유 주식 조회
            #     for d in common.read('trade'):
            #         print(d)
            #     if not len(bought_list):
            #         symbol_list = codes() # 매수 희망 종목 리스트
            #     time.sleep(5)

        if t_sell < t_now < t_exit:  # PM 03:15 ~ PM 03:20 : 일괄 매도
            if soldout == False:
                stock_dict = get_stock_balance()
                for sym, qty in stock_dict.items():
                    sell(sym, qty)
                    common.write('trade',sym, current_price, -qty, str(now),'sell')

                soldout = True
                bought_list = []
                time.sleep(1)
        if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
            for d in common.read('trade'):
                print(d)
            send_message("프로그램을 종료합니다.")
            break


    h.join()    # 쓰레드 종료까지 대기
    keyboard.unhook_all()  # 후킹 해제    
except Exception as e:
    send_message(f"[오류 발생]{e}")
    time.sleep(1)
  
