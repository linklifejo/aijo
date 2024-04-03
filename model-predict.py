import streamlit as st
import model
import database
def main():
    if 'code' not in st.session_state:
        st.session_state.code = ''
    # 함수 사용 예시
    query = """
        SELECT id, code, name
        FROM krxs
        WHERE DATE(SUBSTR(ipo, 1, 10)) <= DATE('now', '-100 days') AND sector != '금융 지원 서비스업'
        """
    # queryToDataframe 함수를 사용하여 데이터를 가져옵니다.
    query_data = database.queryToDataframe(query)
    # 데이터가 없는 경우를 확인합니다.
    if len(query_data) > 0:
        options = ["Select..."] + [f"{row['code']} - {row['name']}" for index, row in query_data.iterrows()]
        selected = st.selectbox("선택", options=options)
        if selected != "Select...":
            st.session_state.code = selected.split(" - ")[0]
            decision,predicted_price,close_price = model.buy_and_sell(st.session_state.code)
            percent = model.calculate_percentage(predicted_price, close_price)
            if decision is not None:
                st.write(f'{decision},{predicted_price},{close_price},{percent}%')
            else:
                st.write('No Model....')
if __name__ == '__main__':
    main()
