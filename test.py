import openapi
import streamlit as st
import pandas as pd

dataframe = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40],
})
st.download_button(
    label='CSV로 다운로드',
    data=dataframe.to_csv(), 
    file_name='sample.csv', 
    mime='text/csv'
)
if "x" not in st.session_state:
    st.session_state.x = set()
        
        
file = st.file_uploader("파일선택(다중가능)(csv or excel)", type=['csv', 'xls', 'xlsx'],accept_multiple_files=True )
x=set()
if file is not None:
    for i in file:
        x.add(i.name)
    
    for j in list(x):
        st.write(j)
    # ext = file.name.split('.')[-1]
    # if ext == 'csv':
    #     # 파일 읽기
    #     df = pd.read_csv(file)
    #     # 출력
    #     st.dataframe(df)
    # elif 'xls' in ext:
    #     # 엑셀 로드
    #     df = pd.read_excel(file, engine='openpyxl')
    #     # 출력
# client = openapi.client(openapi.load_api_key())

# print(openapi.assistant_create(client, "수학 전문가", model="gpt-3.5-turbo", args=None, kwargs=None))
