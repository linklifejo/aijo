import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import qrcode
import time
import FinanceDataReader as fdr
import random
from datetime import datetime as dt
import datetime
import sqlite3
import asyncio
import audio
# 비동기 함수를 정의합니다. 이 함수는 임의의 숫자 목록을 생성합니다.
async def generate_numbers():
    numbers = [random.randint(0, 100) for _ in range(10)]
    await asyncio.sleep(1)  # 비동기 작업을 시뮬레이션하기 위한 대기 시간
    return numbers

# Streamlit 애플리케이션의 메인 함수입니다.
# DataFrame 생성
dataframe = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40],
})

# DataFrame
# use_container_width 기능은 데이터프레임을 컨테이너 크기에 확장할 때 사용합니다. (True/False)
st.dataframe(dataframe, use_container_width=False)


# 테이블(static)
# DataFrame과는 다르게 interactive 한 UI 를 제공하지 않습니다.
st.table(dataframe)


# # 메트릭
st.metric(label="온도", value="10°C", delta="1.2°C")
st.metric(label="삼성전자", value="61,000 원", delta="-1,200 원")

# 컬럼으로 영역을 나누어 표기한 경우
col1, col2, col3 = st.columns(3)
col1.metric(label="달러USD", value="1,228 원", delta="-12.00 원")
col2.metric(label="일본JPY(100엔)", value="958.63 원", delta="-7.44 원")
# 버튼 클릭
button = st.button('버튼을 눌러보세요')

if button:
    st.write(':blue[버튼]이 눌렸습니다 :sparkles:')


# 파일 다운로드 버튼
# 샘플 데이터 생성
dataframe = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40],
})

# 다운로드 버튼 연결
st.download_button(
    label='CSV로 다운로드',
    data=dataframe.to_csv(), 
    file_name='sample.csv', 
    mime='text/csv'
)

# 체크 박스
agree = st.checkbox('동의 하십니까?')

if agree:
    st.write('동의 해주셔서 감사합니다 :100:')

# 라디오 선택 버튼
mbti = st.radio(
    '당신의 MBTI는 무엇입니까?',
    ('ISTJ', 'ENFP', '선택지 없음'))

if mbti == 'ISTJ':
    st.write('당신은 :blue[현실주의자] 이시네요')
elif mbti == 'ENFP':
    st.write('당신은 :green[활동가] 이시네요')
else:
    st.write("당신에 대해 :red[알고 싶어요]:grey_exclamation:")

# 선택 박스
mbti = st.selectbox(
    '당신의 MBTI는 무엇입니까?',
    ('ISTJ', 'ENFP', '선택지 없음'), 
    index=2
)

if mbti == 'ISTJ':
    st.write('당신은 :blue[현실주의자] 이시네요')
elif mbti == 'ENFP':
    st.write('당신은 :green[활동가] 이시네요')
else:
    st.write("당신에 대해 :red[알고 싶어요]:grey_exclamation:")

# 다중 선택 박스
options = st.multiselect(
    '당신이 좋아하는 과일은 뭔가요?',
    ['망고', '오렌지', '사과', '바나나'],
    ['망고', '오렌지'])

st.write(f'당신의 선택은: :red[{options}] 입니다.')


# 슬라이더
values = st.slider(
    '범위의 값을 다음과 같이 지정할 수 있어요:sparkles:',
    0.0, 100.0, (25.0, 75.0))
st.write('선택 범위:', values)

start_time = st.slider(
    "언제 약속을 잡는 것이 좋을까요?",
    min_value=dt(2020, 1, 1, 0, 0), 
    max_value=dt(2020, 1, 7, 23, 0),
    value=dt(2020, 1, 3, 12, 0),
    step=datetime.timedelta(hours=1),
    format="MM/DD/YY - HH:mm")
st.write("선택한 약속 시간:", start_time)


# 텍스트 입력
title = st.text_input(
    label='가고 싶은 여행지가 있나요?', 
    placeholder='여행지를 입력해 주세요'
)
st.write(f'당신이 선택한 여행지: :violet[{title}]')

# 숫자 입력
number = st.number_input(
    label='나이를 입력해 주세요.', 
    min_value=10, 
    max_value=100, 
    value=30,
    step=5
)
st.write('당신이 입력하신 나이는:  ', number)
st.title(':sparkles:로또 생성기:sparkles:')


def generate_lotto():
    lotto = set()

    while len(lotto) < 6:
        number = random.randint(1, 46)
        lotto.add(number)

    lotto = list(lotto)
    lotto.sort()
    return lotto

# st.subheader(f'행운의 번호: :green[{generate_lotto()}]')
# st.write(f"생성된 시각: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

button = st.button('로또를 생성해 주세요!')

if button:
    for i in range(1, 6):
        st.subheader(f'{i}. 행운의 번호: :green[{generate_lotto()}]')
    st.write(f"생성된 시각: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
# Finance Data Reader
# https://github.com/financedata-org/FinanceDataReader

st.title('종목 차트 검색')

with st.sidebar:
    date = st.date_input(
        "조회 시작일을 선택해 주세요",
        datetime.datetime(2022, 1, 1)
    )

    code = st.text_input(
        '종목코드', 
        value='',
        placeholder='종목코드를 입력해 주세요'
    )

if code and date:
    df = fdr.DataReader(code, date)
    if not df.empty:
        data = df.sort_index(ascending=True).loc[:, 'Close']

        tab1, tab2 = st.tabs(['차트', '데이터'])

        with tab1:    
            st.line_chart(data)

        with tab2:
            st.dataframe(df.sort_index(ascending=False))

        with st.expander('컬럼 설명'):
            st.markdown('''
            - Open: 시가
            - High: 고가
            - Low: 저가
            - Close: 종가
            - Adj Close: 수정 종가
            - Volumn: 거래량
            ''')
# 파일 업로드 버튼 (업로드 기능)
file = st.file_uploader("파일 선택(csv or excel)", type=['csv', 'xls', 'xlsx'],key="xx")

# 파일이 정상 업로드 된 경우
# if file is not None:
#     # 파일 읽기
#     df = pd.read_csv(file)
#     # 출력
#     st.dataframe(df)

time.sleep(3)

# Excel or CSV 확장자를 구분하여 출력하는 경우
if file is not None:
    ext = file.name.split('.')[-1]
    if ext == 'csv':
        # 파일 읽기
        df = pd.read_csv(file)
        # 출력
        st.dataframe(df)
    elif 'xls' in ext:
        # 엑셀 로드
        df = pd.read_excel(file, engine='openpyxl')
        # 출력

# 한글 폰트 설정
plt.rcParams['font.family'] = "AppleGothic"
# Windows, 리눅스 사용자
# plt.rcParams['font.family'] = "NanumGothic"
plt.rcParams['axes.unicode_minus'] = False


# DataFrame 생성
data = pd.DataFrame({
    '이름': ['영식', '철수', '영희'],
    '나이': [22, 31, 25],
    '몸무게': [75.5, 80.2, 55.1]
})

st.dataframe(data, use_container_width=True)

fig, ax = plt.subplots()
ax.bar(data['이름'], data['나이'])
st.pyplot(fig)

barplot = sns.barplot(x='이름', y='나이', data=data, ax=ax, palette='Set2')
fig = barplot.get_figure()

st.pyplot(fig)

#############

labels = ['G1', 'G2', 'G3', 'G4', 'G5']
men_means = [20, 35, 30, 35, 27]
women_means = [25, 32, 34, 20, 25]
men_std = [2, 3, 4, 1, 2]
women_std = [3, 5, 2, 3, 3]
width = 0.35       # the width of the bars: can also be len(x) sequence

fig, ax = plt.subplots()

ax.bar(labels, men_means, width, yerr=men_std, label='Men')
ax.bar(labels, women_means, width, yerr=women_std, bottom=men_means,
       label='Women')

ax.set_ylabel('Scores')
ax.set_title('Scores by group and gender')
ax.legend()

st.pyplot(fig)

# Create a QR code instance
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

# Data to be encoded in the QR code
data = "https://www.example.com"

qr = qrcode.QRCode(
    version=1,  # Version 1: 21x21 matrix
    error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
    box_size=10,  # Size of each box in pixels
    border=4,  # Border size in boxes
)

# Add data to the QR code and make it fit within the specified version
qr.add_data(data)
qr.make(fit=True)

# Create an Image object from the QR Code instance
img_single = qr.make_image(fill_color="black", back_color="white")

# Display the QR Code
# img_single.show()
img_single.save("single_qr_code.png")
def connect_db():
    conn = sqlite3.connect('app.db')
    # 외래 키 제약 조건 활성화
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
def init_db():
    conn = connect_db()
    c = conn.cursor()
    # 외래 키 제약 조건 활성화
    c.execute('''CREATE TABLE IF NOT EXISTS Customers
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS Transactions
                 (id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL,
                  FOREIGN KEY(customer_id) REFERENCES Customers(id)
                  ON DELETE CASCADE)''')
    conn.commit()
    conn.close()



def add_customer(name, email):
    conn = connect_db()
    c = conn.cursor()
    c.execute("INSERT INTO Customers (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
    conn.close()

# 거래 내역 추가 함수
def add_transaction(customer_id, amount):
    conn = connect_db()
    c = conn.cursor()
    c.execute("INSERT INTO Transactions (customer_id, amount) VALUES (?, ?)", (customer_id, amount))
    conn.commit()
    conn.close()

# 고객 정보 수정 함수
def update_customer(id, name, email):
    conn = connect_db()
    c = conn.cursor()
    c.execute("UPDATE Customers SET name = ?, email = ? WHERE id = ?", (name, email, id))
    conn.commit()
    conn.close()

# 고객 삭제 함수
def delete_customer(id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("DELETE FROM Customers WHERE id = ?", (id,))
    # c.execute("DELETE FROM Transactions WHERE customer_id = ?", (id,))  # 해당 고객의 모든 거래 내역도 삭제
    conn.commit()
    conn.close()

# 고객 조회 함수
def view_customers():
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM Customers", conn)
    conn.close()
    return df

# 거래 내역 조회 함수
def view_transactions():
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM Transactions", conn)
    conn.close()
    return df

# Streamlit 앱
def main():
    st.title("Customer and Transaction Management")
    st.title("Asyncio and Streamlit Example")

    # 비동기 작업을 동기적으로 실행하고 결과를 가져오기 위한 함수
    def get_numbers():
        return asyncio.run(generate_numbers())

    if st.button("Generate Numbers"):
        with st.spinner('Generating numbers...'):
            numbers = get_numbers()  # 비동기 함수를 호출합니다.
            st.success("Numbers generated!")
            st.write(numbers)
            s,t =audio.speech_to_text()
            if s:
                st.write(t)
            audio.text_to_speech('안녕하세요')
    # 데이터베이스 초기화
    init_db()

    # 사이드바 메뉴
    menu = ["Add Customer", "View Customers", "Add Transaction", "View Transactions", "Update Customer", "Delete Customer"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Add Customer":
        st.subheader("Add New Customer")
        with st.form(key='CustomerForm'):
            name = st.text_input("Name")
            email = st.text_input("Email")
            submit_button = st.form_submit_button(label='Add Customer')
            if submit_button:
                add_customer(name, email)
                st.success(f"Added {name} to the database")

    elif choice == "View Customers":
        st.subheader("View Customers")
        customer_data = view_customers()
        st.dataframe(customer_data)

    elif choice == "Add Transaction":
        st.subheader("Add New Transaction")
        customer_list = view_customers()['id'].tolist()
        with st.form(key='TransactionForm'):
            customer_id = st.selectbox("Customer ID", customer_list)
            amount = st.number_input("Amount", min_value=0.01)
            submit_button = st.form_submit_button(label='Add Transaction')
            if submit_button:
                add_transaction(customer_id, amount)
                st.success(f"Added transaction for customer ID {customer_id}")

    elif choice == "View Transactions":
        st.subheader("View Transactions")
        transaction_data = view_transactions()
        st.dataframe(transaction_data)

    elif choice == "Update Customer":
        st.subheader("Update Customer Information")
        with st.form(key='UpdateCustomer'):
            id = st.number_input("Customer ID", min_value=1, step=1)
            name = st.text_input("Name")
            email = st.text_input("Email")
            submit_button = st.form_submit_button(label='Update Customer')
            if submit_button:
                update_customer(id, name, email)
                st.success(f"Updated customer ID {id}")

    elif choice == "Delete Customer":
        st.subheader("Delete Customer")
        with st.form(key='DeleteCustomer'):
            id = st.number_input("Customer ID", min_value=1, step=1)
            submit_button = st.form_submit_button(label='Delete Customer')
            if submit_button:
                delete_customer(id)
                st.success(f"Deleted customer ID {id}")

if __name__ == "__main__":
    main()
