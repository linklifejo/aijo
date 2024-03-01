import streamlit as st
import audio



# 페이지 컨텐츠 표시 함수
def show_mode():
    # 너비 비율을 조정하여 첫 번째 컬럼을 더 넓게 설정
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"{'채팅' if st.session_state.mode == 'chat' else '음성'}모드입니다")
        with col2:
            next_mode = f"{'음성' if st.session_state.mode == 'chat' else '채팅'}모드로변환"
            if st.button(next_mode):
               st.session_state.mode = 'voice' if st.session_state.mode == 'chat' else 'chat'
               st.rerun()  # 페이지 리로드



# 세션 상태 초기화
if "mode" not in st.session_state:
    st.session_state.mode = 'chat'
show_mode()
if st.session_state.mode == 'chat':
    with st.spinner('Chatting Mode...'):
        if prompt := st.chat_input():
            st.write(prompt)
else:
    with st.spinner('Voice Mode...'):
        audio.text_to_speech('음성모드 입니다. 무엇을 도와드릴까요?')
