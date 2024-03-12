import streamlit as st
import openapi 
import time
import streamlit.components.v1 as components
import random
import audio
import util
import asyncio
from concurrent.futures import ThreadPoolExecutor

    # result_thread.join() 를 제거하여 메인 스레드가 바로 이어서 실행되도록 함


if 'id' not in st.session_state:
    st.session_state.id=''
if 'ps' not in st.session_state:
    st.session_state.ps=''
if 'check' not in st.session_state:
    st.session_state.check = False
if 'mode' not in st.session_state:
    st.session_state.mode = '채팅모드' 
if 'sound' not in st.session_state:
    st.session_state.sound = False

st.session_state.counter = 0

st.session_state.counter=random.randint(1,46)
# Streamlit 페이지에 JavaScript를 포함시키기 위해 components.html() 사용

st.session_state.counter=random.randint(1,46)
components.html(
    f"""
        <div style="display:none;">숨겨진 컨테이너</div>
        <p>{st.session_state.counter}</p>
        <script>
            var inputs = window.parent.document.querySelectorAll('input,textarea');
            document.addEventListener('DOMContentLoaded', (event) => {{
            for (var i = 0; i < inputs.length; i++) {{
                if (inputs[i].placeholder == 'Your message') {{
                        inputs[i].focus();
                        break;
                }}
                else
                    {{
                        if (inputs[i].value == '' || inputs[i].value == '채팅모드') {{
                                inputs[i].focus();
                                break;
                        }}
                    }}
            }}
        }});

        </script>
    """,
    height=0,
    width=0,
)

def login():
    if not st.session_state.id:
        form.write("아이디를 입력하세요....")
        st.session_state.check = False
    elif not st.session_state.ps:
        form.write("페스워드를 입력하세요....")
        st.session_state.check = False
    else:
        st.session_state.check = True
         
        if openapi.login(st.session_state.id,st.session_state.ps):
            key = openapi.load_api_key()
            if key is not None:
                st.session_state.api_key = key
def run_async(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)             
with st.sidebar:
    form = st.form("my_form")
    form.text_input("아이디", key="id")
    form.text_input("페스워드", key="ps",type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    c = st.button('정리')
    if c:
        run_async(audio.stop_to_speech())

    mode = st.radio(
    '모드선택[채팅모드, 음성모드]',
    ('채팅모드', '음성모드'))
    # mode = st.selectbox("모드선택[채팅, 음성]", ["채팅모드", "음성모드"])
    if mode == '채팅모드':
        st.write('채팅모드를 :blue[채팅모드] 선택하셨네요')
        st.session_state.mode = '채팅모드'  
    else:
        st.write('음성모드를 :blue[음성] 선택하셨네요')
        st.session_state.mode = '음성모드'

    form.form_submit_button("Submit",use_container_width=True,on_click=login)

if st.session_state.check and st.session_state.mode == '채팅모드':
    st.title("💬 채팅모드 입니다.")
    st.caption("🚀 Selected chatting mode by OpenAI LLM")
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "무엇을 도와 드릴까요?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    with st.spinner('채팅모드...'):
        if prompt := st.chat_input():
            client = openapi.client_connect(st.session_state.api_key)
            if client is None:
                st.info("API 키가 무효합니다. 올바른 API 키를 확인하십시오.")
                st.stop()
            if "assistant_id" not in st.session_state:
                st.session_state.assistant_id,st.session_state.thread_id = openapi.isrelations(client,st.session_state.api_key,st.session_state.id)
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            try:
                run = openapi.ask(client, st.session_state.assistant_id, st.session_state.thread_id, prompt)
                time.sleep(1)
                if run is not None:
                    msg = openapi.result(client, run, st.session_state.thread_id)  
                    if msg:
                        print(msg)
                        # # response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
                        # response = client.chat.completions.create(model="gpt-4-turbo-preview", messages=st.session_state.messages)
                        # msg = response.choices[0].message.content
                        # st.write(response,'xxxx')
                        st.session_state.messages.append({"role": "assistant", "content": msg})
                        # audio.text_to_speech(msg)
            except Exception as e:
                st.info("채팅서버 이상유무 확인이 필요합니다.")
                # st.stop()
            # st.rerun()     
elif st.session_state.check and st.session_state.mode == '음성모드':
    if not st.session_state.sound:
        st.title("💬 음성모드 입니다.")
        st.caption("🚀 Selected sound mode by OpenAI LLM")
        if 'ment' not in st.session_state:
            st.session_state.ment = "음성모드 입니다. 무엇을 도와 드릴까요?"
            run_async(audio.text_to_speech(st.session_state.ment))
    with st.spinner('음성모드...'):
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": st.session_state.ment}]

        for msg in reversed(st.session_state.messages):
            st.chat_message(msg["role"]).write(msg["content"])
        exited, prompt = run_async(audio.handle_voice_command())
        if exited:
            if prompt == '종료':
                run_async(audio.text_to_speech('프로그램을 종료합니다.'))
                run_async(audio.stop_to_speech())
                util.kill_exe()
                util.kill_exe('streamlit.exe')
                util.kill_exe('python.exe')
        
            client = openapi.client_connect(st.session_state.api_key)
            if client is None:
                st.info("API 키가 무효합니다. 올바른 API 키를 확인하십시오.")
                st.stop()

            if "assistant_id" not in st.session_state:
                st.session_state.assistant_id,st.session_state.thread_id = openapi.isrelations(client,st.session_state.api_key,st.session_state.id)
            run_async(audio.text_to_speech(prompt))
            try:
                print(st.session_state.assistant_id,st.session_state.thread_id)
                run = openapi.ask(client, st.session_state.assistant_id, st.session_state.thread_id, prompt)
                if run.status == 'failed':
                    run_async(audio.text_to_speech('실패'))
                else:
                    msg = openapi.result(client, run, st.session_state.thread_id)  
                    if msg:
                        st.session_state.messages.append({"role": "assistant", "content": msg})
                        run_async(audio.text_to_speech(msg))
                        st.session_state.sound=True
            except Exception as e:
                st.info("채팅서버 이상유무 확인이 필요합니다.")
        # st.rerun()             



