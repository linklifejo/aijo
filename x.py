from openai import OpenAI
import streamlit as st
import subprocess
import audio
def kill_streamlit():
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'streamlit.exe'], check=True)
        print("Python has been successfully terminated.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
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


with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password",value="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")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Chatbot")
st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")
if "messages" not in st.session_state:
    st.session_state['messages'] = [{"role": "assistant", "content": "말씀하세요"}]

for msg in reversed(st.session_state.messages):
    st.chat_message(msg["role"]).write(msg["content"])

status, msg = audio.speech_to_text()
if status:
    # if prompt := st.chat_input():
        if not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()

        client = OpenAI(api_key=openai_api_key)
        st.session_state.messages.append({"role": "user", "content": msg})
        st.chat_message("user").write(msg)
        if '종료' in msg:
            audio.text_to_speech('프로그램을 종료합니다.') 
            kill_chrome()
            kill_python()   
        response = client.chat.completions.create(model="gpt-3.5-turbo-1106", messages=st.session_state.messages)
        msg = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

        audio.text_to_speech(msg)
st.rerun()