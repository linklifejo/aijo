import keyboard
import threading
import pyautogui
import subprocess  # 외부 프로그램을 실행하기 위한 모듈
from time import sleep
from openai import OpenAI
import streamlit as st

chrome_process = None
class Hook(threading.Thread):
    def __init__(self):
        super(Hook, self).__init__()  # 부모 클래스 __init__ 실행
        self.daemon = True  # 데몬 쓰레드로 설정
        self.event = False  # f4가 눌리면 event 발생
        self.my_xy = []     # 좌표 저장 리스트
        
        keyboard.unhook_all()  # 후킹 초기화
        keyboard.add_hotkey('f4', print, args=['\n종료합니다'])  # f4가 눌리면 print 실행
        keyboard.add_hotkey('f2', print, args=['\n좌표값이 추가되었습니다'])  # f2가 눌리면 print 실행
        keyboard.add_hotkey('f8', print, args=['\n크롬을 실행합니다.'])  # f7가 눌리면 print 실행
        keyboard.add_hotkey('f9', print, args=['\n크롬을 종료합니다.'])  # f8가 눌리면 print 실행

    def run(self):  # run 메소드 재정의
        while True:
            key = keyboard.read_hotkey(suppress=False)  # hotkey를 계속 읽음
            if key == 'f4':  # f4 받은 경우
                self.event = True  # event 클래스 변수를 True로 설정
                # print("\n", self.my_xy)

                with open(r"config.txt", "w") as f:
                    for i in self.my_xy:
                        f.write("{},{}\n".format(i[0], i[1]))
                # sleep(1)
                subprocess.run(['taskkill', '/F', '/IM', 'streamlit.exe'], check=True)
                break  # 반복문 탈출
               
            
            elif key == 'f2':
                position = pyautogui.position()
                self.my_xy.append((position.x, position.y))
            elif key == 'f8':
                 self.open_chrome()
            elif key == 'f9':
                 self.close_chrome()
                 sleep(1)
                 subprocess.run(['taskkill', '/F', '/IM', 'streamlit.exe'], check=True)

    def open_chrome(self):
        global chrome_process
        if chrome_process is None:  # 크롬이 실행되지 않았다면
            # 크롬 실행 (경로는 시스템에 따라 다를 수 있음)
            chrome_process = subprocess.Popen('start chrome', shell=True)
            print("Chrome opened")

    def close_chrome(self):
        global chrome_process
        if chrome_process is not None:  # 크롬이 실행 중이라면
            # 크롬 프로세스 종료
            chrome_process.terminate()
            chrome_process = None
            print("Chrome closed")
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], check=True)
                print("Chrome has been successfully terminated.")
            except subprocess.CalledProcessError as e:
                print(f"An error occurred: {e}")      


h = Hook()  # 훅 쓰레드 생성
h.start()   # 쓰레드 실행
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Chatbot")
st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(model="gpt-3.5-turbo-1106", messages=st.session_state.messages)
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)

if h.event == True:  # h.event가 True이면(f4 입력받은 경우) 종료
    h.close_chrome()
    keyboard.unhook_all()  # 후킹 해제 
    exit()
    
else:
    h.join()    # 쓰레드 종료까지 대기
          
