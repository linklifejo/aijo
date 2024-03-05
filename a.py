import streamlit as st
import asyncio
import ad

# 비동기 작업을 Streamlit에서 실행하기 위한 래퍼 함수
def run_async(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coroutine)

st.title('비동기 TTS 앱')
mbti = st.radio(
    '선택하세요',
    ('음성변환', '문자변환'))

if mbti == '음성변환':
    text = st.text_input('텍스트를 입력하세요:',value='our secret API keys are listed below. Please note that we do not display your secret API keys again after you generate them.')
    c =st.button("음성변환")
    s =st.button("음성중지")
    if c:
        ad.text_to_speech(text)
    if s:
        st.write('The End...')
        ad.stop_to_speech()
else:
    cc=st.button("문자변환")
    if cc:
        st.write(ad.speech_to_text())





