from openai import OpenAI
from bs4 import BeautifulSoup
import requests
import time
import json
import os
from openapi import show_json, login,load_api_key,client_connect,assistants_delete,assistant_create,assistant_list,assistant_delete,thread_create,ask,result

def oil_price():
  url = "https://www.knoc.co.kr/"
  r = requests.get(url)
  soup = BeautifulSoup(r.text, 'html.parser')
  price=[]
  for tag in soup.find_all("dl",class_="money_list")[3:]:
    price.append(tag.find('li').text)
  return {"Dubai":2000, "WTI":2000, "Brent":2000}

def usd_krw():
  url = "https://finance.naver.com/marketindex/"
  r = requests.get(url)
  soup = BeautifulSoup(r.text, 'html.parser')
  usdkrw = soup.find("span",class_='value').text
  return usdkrw
# Assistant에게 함수 사용법을 알려주기 위해 함수 설명도 준비했습니다.

tools = [
    {
        "type":"function",
        "function": {
            "name":"oil_price",
            "description":"Get current oil prices - Dubai, WTI, and Brent",
            "parameters": {
                "type":"object",
                "properties": {}
            },
            "required": []
        }
    },
    {
        "type":"function",
        "function": {
            "name":"usd_krw",
            "description":"Get current exchange rate from USD to KRW",
            "parameters": {
                "type":"object",
                "properties": {}
            },
            "required": []
        }
    }
]

client=None
assistant_id = None
thread_id = None
if login('1','1'):
   api_key = load_api_key()
   if api_key:
      client = client_connect(api_key)
      assistant_id = assistant_create(client)
      thread_id = thread_create(client)

# print(assistants_delete(client))
# 3+3
# 미국의수도는?
# 현재 WTI 석유 가격을 원화로 알려줄래?



while True:
    user_message = input('질문하세요:')
    if user_message: 
        run = ask(client, assistant_id, thread_id, user_message)
        time.sleep(1)
        print(result(client, run, thread_id))       
