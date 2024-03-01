import webrtcvad
from collections import deque
import pyaudio
import numpy as np
from openai import OpenAI
import speech_recognition as sr
from bs4 import BeautifulSoup
import time
from gtts import gTTS
from pygame import mixer
import os
import subprocess
import requests
import json
import streamlit as st
client = OpenAI(api_key="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")
def kill_python():
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], check=True)
        print("Python has been successfully terminated.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
def kill_chrome():
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], check=True)
        print("Chrome has been successfully terminated.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

 
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            audio = r.listen(source, timeout=5,phrase_time_limit=5)               
            if audio:
                    text = r.recognize_google(audio, language='ko-KR')
                    if text:
                            return True, text
        except sr.WaitTimeoutError:
                return False, 'timeout'
        except sr.UnknownValueError:
                return False, 'unknown'
        except sr.RequestError as e:
                return False, 'error'        
def text_to_speech(text, lang='ko'):
    try:
        # 현재 디렉토리에 오디오 파일 이름 설정
        temp_file_name = "temp_audio.mp3"
        
        # gTTS를 사용하여 텍스트를 오디오로 변환하고 파일 저장
        tts = gTTS(text=text, lang=lang)
        tts.save(temp_file_name)
        
        # pygame 믹서 초기화
        mixer.init()
        
        # 오디오 파일 불러오기 및 재생
        mixer.music.load(temp_file_name)
        mixer.music.play()

        # 오디오 재생이 끝날 때까지 대기
        while mixer.music.get_busy():
            pass

        # 오디오 재생이 끝나면 파일 삭제
        mixer.quit()
        os.remove(temp_file_name)
        
    except:
        print('end...')
        

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

client = OpenAI(api_key="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")

def assistant():
    assistant = client.beta.assistants.create(
        instructions = "너는 기름 전문가야",
        
        model="gpt-3.5-turbo-1106",
        tools = tools
    )
    return assistant.id

def thread():    
    thread = client.beta.threads.create()
    return thread.id
def run(client, assistant_id, thread_id):
    run = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assistant_id
    )   
    return run.id
def message(m, assistant_id, thread_id):
    client.beta.threads.messages.create(
    thread_id,
    role="user",
    content=m
    )
    run_id=run(client,assistant_id,thread_id)
    run_check = wait_run(client, run_id, thread_id)
    return run_check, run_id,m

def wait_run(client, run_id, thread_id):
  while True:
    run_check = client.beta.threads.runs.retrieve(
      thread_id=thread_id,
      run_id=run_id
    )
    print(run_check.status)
    if run_check.status in ['queued','in_progress']:
      time.sleep(2)
    else:
      break
  return run_check

def result(client, run_check,thread_id,run_id):
    while True:
            if run_check.status == 'completed':
                messages = client.beta.threads.messages.list(thread_id)
                msg = messages.data[0].content[0].text.value
                return msg
                    # for msg in reversed(thread_messages.data):
                    #     print(type(msg.content[0].text.value))   
                    #     # print(f"{msg.role}: {msg.content[0].text.value}") 
                    #     # print(msg.content[0].text.value)
                    # break
            
            tool_calls = run_check.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            for tool in tool_calls:
                func_name = tool.function.name
                kwargs = json.loads(tool.function.arguments)
                output = globals()[func_name](**kwargs)
                # output = locals()[func_name](**kwargs)
                tool_outputs.append(
                    {
                        "tool_call_id":tool.id,
                        "output":str(output)
                    }
                )
            run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs
            )
            run_check = wait_run(client,run.id,thread_id)
print(assistant())
assistant_id = 'asst_gcyRKHs1s2pJB5gWNRS1IENL'
thread_id='thread_poMHPM3C3cuO4jsEdUF9cGdX'

if "messages" not in st.session_state:
    st.session_state['messages'] = deque(maxlen=20)
    st.session_state['pgm_end'] = False
    st.session_state['help_msg'] = '무엇을 도와드릴까요?'
    st.chat_message('assistant').write(st.session_state['help_msg'])
    text_to_speech(st.session_state['help_msg'])          
while True:
            status, msg = speech_to_text()

            if status:
                        st.chat_message("user").write(msg)
                        run_check, run_id, m = message(msg, assistant_id,thread_id)
                        msg = result(client,run_check,thread_id,run_id) 
                        if msg:
                                if '종료' in m:
                                    st.session_state['pgm_end'] = True
                                else:
                                    st.session_state.messages.appendleft({'role':'assistant','content':msg})
                                    st.chat_message('assistant').write(msg)
                                    text_to_speech(msg)   
                                    for msg in st.session_state.messages:
                                        st.chat_message(msg["role"]).write(msg["content"])
                                        st.rerun()  # 페이지 리로드
            if st.session_state['pgm_end']:
                text_to_speech('프로그램을 종료합니다.') 
                kill_chrome()
                kill_python()    
                break         

       
    
    



