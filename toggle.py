import streamlit as st
from st_click_detector import click_detector
from streamlit.components.v1 import html
import base64

# 자동 포커스를 주기 위한 JavaScript 코드 생성
def set_autofocus_js():
    return """
        <script>
            var input = window.parent.document.querySelectorAll("input[type=text]");
            for (var i = 0; i < input.length; ++i) {{
                input[i].focus();
            }}
        </script>
    """

# 이미지 파일을 Base64로 인코딩하는 함수
def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# 이미지 Base64 문자열을 HTML 이미지 태그로 변환하는 함수
def get_img_tag_with_base64(img_base64, img_id):
    return f'<a href="#" id="{img_id}"><img src="data:image/png;base64,{img_base64}" style="width:50px;height:50px; cursor: pointer;"></a>'

def on_enter():
    st.session_state.img = 'voice'
    st.session_state.input = ''  # 입력 필드를 비움

# 세션 상태에 'mode', 'image_clicked', 'input' 초기화
if 'mode' not in st.session_state:
    st.session_state.mode = 'chat'
if 'img' not in st.session_state:
    st.session_state.img = 'voice'
if 'image_clicked' not in st.session_state:
    st.session_state.image_clicked = False
if 'input' not in st.session_state:  # 입력 필드를 위한 세션 상태 추가
    st.session_state.input = ''

# 현재 모드에 따라 이미지 파일 이름 설정
image_file = 'voice_mode.png' if st.session_state.img == 'voice' else 'chat_mode.png'

# 이미지 Base64 인코딩 및 HTML 컨텐츠 생성
img_base64 = get_image_base64(image_file)
image_id = "toggle_image"
content = get_img_tag_with_base64(img_base64, image_id)
with st.container():
    col1, col2 = st.columns([3, 1])
    if st.session_state.img == 'voice':
        with col1:
            user_input = st.text_input("메시지를 입력하세요...", value=st.session_state.input, on_change=on_enter, key="input")
            html(set_autofocus_js())
    else:
        with col1:
            st.write("말씀하세요")

    # 이미지가 클릭되었다는 것을 감지하기 위한 컨테이너
    with col2:
        clicked = click_detector(content, key="click_detector")
        # if clicked:
        st.session_state.image_clicked = not st.session_state.image_clicked
        st.session_state.img = 'voice' if st.session_state.img == 'chat' else 'chat'
        st.session_state.mode = 'chat' if st.session_state.mode == 'voice' else 'voice'
