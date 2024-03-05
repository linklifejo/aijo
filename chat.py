import streamlit as st
import openapi 
import time
import streamlit.components.v1 as components
import random
import audio


if 'id' not in st.session_state:
    st.session_state.id=''
if 'ps' not in st.session_state:
    st.session_state.ps=''
if 'check' not in st.session_state:
    st.session_state.check = False
   
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
                        if (inputs[i].value == '') {{
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
with st.sidebar:
    form = st.form("my_form")
    form.text_input("아이디", key="id")
    form.text_input("페스워드", key="ps",type="password")
    "[![Get an OpenAI API key](https://github.com/codespaces/badge.svg)](https://platform.openai.com/account/api-keys)"
    form.form_submit_button("Submit",use_container_width=True,on_click=login)
    

if st.session_state.check:
    st.title("💬 Chatbot")
    st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]


    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

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
            msg = openapi.result(client, run, st.session_state.thread_id)  
            # # response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
            # response = client.chat.completions.create(model="gpt-4-turbo-preview", messages=st.session_state.messages)
            # msg = response.choices[0].message.content
            # st.write(response,'xxxx')
            st.session_state.messages.append({"role": "assistant", "content": msg})
            # audio.text_to_speech(msg)
        except Exception as e:
            st.info("채팅서버 이상유무 확인이 필요합니다.")
            # st.stop()
        st.rerun()     



