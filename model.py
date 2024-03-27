import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader as pdr
import streamlit as st

import datetime 
from tensorflow import keras 
from keras.models import Model, Sequential, load_model
from keras.layers import Dense, LSTM, Input, Concatenate,GRU, Dropout
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
import FinanceDataReader as fdr
import pickle
import database
import keyboard
import threading
import util
import asyncio
import aioconsole  # 추가
import os
import sys
import time
from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint
def create_company_directory(company_code):
    directory = f"./models/{company_code}"
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_model(model, company_code):
    directory = f"./models/{company_code}"
    model.save(os.path.join(directory, "model.h5"))

def load_model(company_code):
    directory = f"./models/{company_code}"
    model_path = os.path.join(directory, "model.h5")
    if os.path.exists(model_path):
        return keras.models.load_model(model_path)
    else:
        return None
def files():
    return {
        'model': 'integrated_stock_model1.h5',
        'scaler': 'stock_scaler1.pkl',
        'encoder': 'stock_encoder1.pkl'
    }

def initialize():
    for _, file in files().items():
        if os.path.exists(file):
            os.remove(file)

def get_company_codes():
    companies = []
    query = """
    SELECT id, code, name
    FROM krxs
    WHERE DATE(SUBSTR(ipo, 1, 10)) <= DATE('now', '-100 days') AND sector != '금융 지원 서비스업'
    """
    df = database.queryToDataframe(query)
    for _, row in df.iterrows():
        companies.append({
            'id': row['id'],
            'code': row['code'],
            'name': row['name']
        })
    return companies

# 역정규화 함수 정의
def denormalize(normalized_price, window):
    return normalized_price * window[0] + window[0]

# LSTM 모델 구성 및 컴파일
def build_lstm_model(input_shape):
    model = Sequential()
    model.add(Input(shape=input_shape))  # Use an Input layer to specify the input shape
    model.add(LSTM(50, return_sequences=True))
    model.add(LSTM(64, return_sequences=False))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mse', optimizer='rmsprop')
    return model

def load_data(code):
    start_date = (datetime.datetime.now() - datetime.timedelta(days=1000)).strftime('%Y-%m-%d')
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    data = fdr.DataReader(st.session_state.code, start=start_date, end=today)
    return data

def train_test_data(data):
    # 종가 사용
    close_prices = data['Close'].values

    # 시퀀스 길이 설정
    seq_len = 60

    # 시퀀스 데이터 생성
    result = []
    for index in range(len(close_prices) - seq_len):
        result.append(close_prices[index: index + seq_len + 1])

    # 정규화
    normalized_data = []
    for window in result:
        normalized_window = [((float(p) / float(window[0])) - 1) for p in window]
        normalized_data.append(normalized_window)

    result = np.array(normalized_data)

    # 트레인 테스트 분리
    row = int(round(result.shape[0] * 0.9))
    train = result[:row, :]
    np.random.shuffle(train)

    x_train = train[:, :-1]
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    y_train = train[:, -1]

    x_test = result[row:, :-1]
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
    y_test = result[row:, -1]
    return x_train, y_train, x_test, y_test, close_prices, seq_len

def fit_model(x_train, y_train, count=1):
    lstm_models = [build_lstm_model((60, 1)) for _ in range(count)]

    # 각 모델에 대해 학습
    for model in lstm_models:
        model.fit(x_train, y_train, epochs=10, batch_size=64, verbose=1)
    return lstm_models

def predict_model(x_test, lstm_models, close_prices,seq_len):
    # 각 모델로부터 예측 수행
    predictions = np.array([model.predict(x_test) for model in lstm_models])
    # 예측값의 평균 계산
    mean_predictions = np.mean(predictions, axis=0)
    # 마지막 예측값을 역정규화하여 실제 가격으로 변환
    last_window = close_prices[-seq_len-1:-1]  # Adjust for the correct window
    predicted_price = denormalize(mean_predictions[-1], last_window)
    return predicted_price, mean_predictions

def decisions(predicted_price, close_prices):
    # 예측된 가격 역변환 (첫 번째 특성만 사용)
    price_change = (predicted_price - close_prices[-1]) / close_prices[-1]

    decision_threshold = 0.01
    decision = "보류(Hold)"
    if price_change > decision_threshold:
        decision = "매수(Buy)"
    elif price_change < -decision_threshold:
        decision = "매도(Sell)"
    return decision

def result(predicted_price, close_prices):
    return decisions(predicted_price, close_prices)

def show_decision(predicted_price, close_prices):
    decision = result(predicted_price, close_prices)
    st.write(f'현재가: {close_prices[-1]} , 예측가격: {int(predicted_price)} , 결정: {decision}')

def show_chart(y_test, mean_predictions):
    # 차트 그리기
    fig = plt.figure(facecolor='white', figsize=(20, 10))
    ax = fig.add_subplot(111)
    ax.plot(y_test, label='True')
    ax.plot(mean_predictions, label='Prediction')
    ax.legend()
    plt.show()
    
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
        create_company_directory(st.session_state.code)  # 각 업체별 디렉토리 생성
        data = load_data(st.session_state.code )
        x_train, y_train, x_test, y_test, close_prices, seq_len = train_test_data(data)
        
        # 학습된 모델 불러오기 또는 새로운 모델 학습
        model = load_model(st.session_state.code)
        if model is None:
            lstm_models = fit_model(x_train, y_train, count=1)
            model = lstm_models[0]
            save_model(model, st.session_state.code)
        else:
            lstm_models = [model]

        predicted_price, mean_predictions = predict_model(x_test, lstm_models, close_prices, seq_len)
        show_decision(predicted_price, close_prices)
        show_chart(y_test, mean_predictions)
if __name__ == '__main__':
    main()