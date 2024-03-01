import streamlit as st
from collections import deque

def main():

    st.title("실시간 채팅 애플리케이션")

    # 세션 상태에서 대화 내용을 저장할 deque 초기화
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = deque(maxlen=7)

    # 중간 영역: 동적 콘텐츠 표시
    chat_placeholder = st.empty()

    # 하단 영역: 사용자 입력
    with st.container():
        user_input = st.text_input("메시지를 입력하세요:", key="input",value='')
        send_button = st.button("전송")

    if send_button:
        st.session_state.chat_history.appendleft(user_input)
        user_input = ''

    # 중간 영역 콘텐츠 업데이트
    with chat_placeholder.container(height=600,border=0):
        for message in st.session_state.chat_history:
            st.chat_message('assistant').write(message)

if __name__ == "__main__":
    main()
