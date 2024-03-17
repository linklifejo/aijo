import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader as pdr
import datetime 
from tensorflow import keras
from keras.models import Model, Sequential, load_model
from keras.layers import Dense, LSTM, Input, Concatenate
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
import FinanceDataReader as fdr
import pickle
import database
import keyboard
import os
from keras.callbacks import EarlyStopping

def initialize():
    # 파일 삭제 또는 기타 초기화 작업 수행
    if os.path.exists('integrated_stock_model.h5'):
        os.remove('integrated_stock_model.h5')
    if os.path.exists('stock_scaler.pkl'):
        os.remove('stock_scaler.pkl')
    if os.path.exists('stock_encoder.pkl'):
        os.remove('stock_encoder.pkl')
def get_company_codes(start_id, end_id):
    codes = []
    names = []
    query = f"""
    SELECT * 
    FROM krxs 
    WHERE DATE(SUBSTR(ipo, 1, 10)) <= DATE('now', '-60 days')
    """
    df = database.queryIdRange('krxs', start_id, end_id)
    for _, row in df.iterrows():
        codes.append(row['code'])
        names.append(row['name'])
    return codes, names

def load_and_preprocess_data(codes, start_date):
    scaler = MinMaxScaler(feature_range=(0, 1))
    encoder = OneHotEncoder(handle_unknown='ignore')

    encoded_codes = encoder.fit_transform(np.array(codes).reshape(-1, 1)).toarray()

    x_prices, x_companies, y_prices = [], [], []
    for code in codes:
        df = fdr.DataReader(code, start=start_date)
        if len(df) >= 60:
            prices = df['Close'].values.reshape(-1, 1)
            scaled_prices = scaler.fit_transform(prices)
            for i in range(60, len(scaled_prices)):
                x_prices.append(scaled_prices[i-60:i, 0])
                x_companies.append(encoded_codes[codes.index(code)])
                y_prices.append(scaled_prices[i, 0])

    return np.array(x_prices), np.array(x_companies), np.array(y_prices), scaler, encoder

def build_or_load_model(model_path, input_shape, num_companies):
    if os.path.exists(model_path):
        print("Loading existing model...")
        model = load_model(model_path)
    else:
        print("Building a new model...")
        price_input = Input(shape=input_shape, name='price_input')
        company_input = Input(shape=(num_companies,), name='company_input')
        lstm_layer = LSTM(50, return_sequences=False)(price_input)
        concat_layer = Concatenate()([lstm_layer, company_input])
        dense_layer = Dense(25, activation='relu')(concat_layer)
        output_layer = Dense(1, activation='linear')(dense_layer)
        model = Model(inputs=[price_input, company_input], outputs=output_layer)
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def train_and_predict(start_id, end_id):
    model_path = 'integrated_stock_model.h5'
    x_prices, x_companies, y_prices, scaler, encoder = load_and_preprocess_data(CODES[start_id:end_id], START_DATE)
    
    if len(x_prices) > 0:
        model = build_or_load_model(model_path, (60, 1), len(CODES[start_id:end_id]))
        early_stopping = EarlyStopping(monitor='val_loss', patience=5, verbose=1, mode='min', restore_best_weights=True)
        model.fit([x_prices, x_companies], y_prices, epochs=10, batch_size=32, validation_split=0.2, callbacks=[early_stopping])
        
        model.save(model_path)
        with open('stock_scaler.pkl', 'wb') as f:
            pickle.dump(scaler, f)
        # encoder 저장
        with open('stock_encoder.pkl', 'wb') as f:
            pickle.dump(encoder, f)

        print_predictions(model, scaler, encoder, start_id, end_id)
    else:
        print("Insufficient data. Cannot train the model.")

def print_predictions(model, scaler, encoder, start_id, end_id):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    decision_threshold = 0.05  # 5% 변동을 기준으로 결정

    for index, code in enumerate(CODES[start_id:end_id]):
        try:
            df = fdr.DataReader(code, start=START_DATE, end=today)
            
            if len(df) >= 60:
                last_60_days = df['Close'].values[-60:].reshape(-1, 1)
                current_price = df['Close'].values[-1]  # 가장 최근 가격

                scaled_last_60_days = scaler.transform(last_60_days)
                company_encoded = encoder.transform([[code]]).toarray().reshape(1, -1)

                predicted_price_scaled = model.predict([scaled_last_60_days.reshape(1, 60, 1), company_encoded])
                predicted_price = scaler.inverse_transform(predicted_price_scaled)[0][0]

                print(f"업체 '{code} ({NAMES[start_id + index]})'의 현재 가격: {current_price:.2f}, 예측된 내일 'Close' 가격: {predicted_price:.2f}")

                price_change = (predicted_price - current_price) / current_price

                if price_change > decision_threshold:
                    decision = "매수(Buy)"
                elif price_change < -decision_threshold:
                    decision = "매도(Sell)"
                else:
                    decision = "보류(Hold)"

                print(f"결정: {decision}")

            else:
                print(f"업체 '{code} ({NAMES[start_id + index]})'에 대한 충분한 데이터가 없습니다.")
        except ValueError:
            print(f"업체 '{code}'에 대해 알 수 없는 카테고리입니다. 예측을 건너뜁니다.")

def predict_next_day_prices():
    model_path = 'integrated_stock_model.h5'
    scaler_path = 'stock_scaler.pkl'
    encoder_path = 'stock_encoder.pkl'
    
    if os.path.exists(model_path) and os.path.exists(scaler_path) and os.path.exists(encoder_path):
        model = load_model(model_path)
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        with open(encoder_path, 'rb') as f:
            encoder = pickle.load(f)

        print_predictions(model, scaler, encoder, 1, 2554)
    else:
        print("필요한 모델 또는 전처리 파일이 없습니다. 먼저 학습 모드(F1)를 실행해 주세요.")
def on_press(event):
    if event.name == 'f9':
        print('학습 모드...')
        for i in range(1, num_companies + 1, 200):
            end = min(i + 126, num_companies)  # 마지막 그룹에서는 127을 초과하지 않도록
            train_and_predict(i, end)
        print(datetime.datetime.now())
    elif event.name == 'f10':
        print('예측 모드...')
        predict_next_day_prices()
        print(datetime.datetime.now())
    elif event.name == 'f11':
        print('초기화 모드...')
        initialize()

def main():
    print(datetime.datetime.now())
    print("프로그램 실행 중... (F9: 학습/재학습, F10: 예측), F11: 초기화, Esc: 종료")
    keyboard.on_press(on_press)
    keyboard.wait('esc')  # 프로그램 종료를 위해 'esc' 키를 누를 때까지 대기 

# 전역 상수로 코드와 이름 리스트 정의
CODES, NAMES = get_company_codes(1, 2554)
num_companies = len(CODES)
START_DATE = '2020-01-01'

if __name__ == '__main__':
    main()
