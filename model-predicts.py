import streamlit as st
import model
import database
import datetime
import database

def main():
    query = """
        SELECT code, name
        FROM krxs
        WHERE DATE(SUBSTR(ipo, 1, 10)) <= DATE('now', '-100 days')
        """
    # queryToDataframe 함수를 사용하여 데이터를 가져옵니다.
    query_data = database.queryToDataframe(query)
    if len(query_data) > 0:
        database.deleteAllData('predicts')
        for index, row in query_data.iterrows():
            code = row['code']
            name = row['name']
            predicted_date = datetime.datetime.now().strftime('%Y-%m-%d')
            decision, predicted_price, close_price = model.buy_and_sell(code)
            percent = model.calculate_percentage(predicted_price, close_price)
            if decision is not None:
                database.insertData('predicts', {
                'code': code,
                'name': name,
                'predicted_date': predicted_date,
                'decision': decision,
                'predicted_price': int(predicted_price),
                'close_price': int(close_price),
                'percent': percent
                })
if __name__ == '__main__':
    main()
