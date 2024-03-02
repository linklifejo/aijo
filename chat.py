import streamlit as st
import openapi 
import time
import streamlit.components.v1 as components
import random


if 'id' not in st.session_state:
    st.session_state.id=''
if 'ps' not in st.session_state:
    st.session_state.ps=''
if 'counter' in st.session_state:
    st.session_state.counter = 0

with st.sidebar:
    id = st.text_input("회원아이디", key="id")
    ps = st.text_input("패스워드", key="ps",type="password")
    "[![Get an OpenAI API key](https://github.com/codespaces/badge.svg)](https://platform.openai.com/account/api-keys)"
    submit_button = st.button(label='Submit',use_container_width=True)
    if submit_button:
        if not id:
 
            st.write("아이디를 입력하세요....")

            # st.stop()

        elif not ps:
            st.write("페스워드를 입력하세요....")
            # st.stop()
        st.session_state.counter = number = random.randint(1, 46)
        components.html(
            
                f"""
                    <div>some hidden container</div>
                    <p>{st.session_state.counter}</p>
                    <script>
                        var inputs = window.parent.document.querySelectorAll("input[type=text]");
                        for (var i = 0; i < inputs.length; ++i) {{
                            if (inputs[i].value == '') {{
                                inputs[i].focus();
                                break; // Exit the loop after focusing the first empty input  
                            }}
                        }}
 
                    </script>
                """,
            height=0,
            width=0,
            ) 

    if openapi.login(id,ps):
        key = openapi.load_api_key()
        if key is not None:
            st.session_state.api_key = key

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
                    st.session_state.assistant_id = openapi.assistant_create(client)
                if "thread_id" not in st.session_state:
                    st.session_state.thread_id = openapi.thread_create(client)
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
                except Exception as e:
                    st.info("채팅서버 이상유무 확인이 필요합니다.")
                    # st.stop()
                st.rerun()        
