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
    for file in ['integrated_stock_model.h5', 'stock_scaler.pkl', 'stock_encoder.pkl']:
        if os.path.exists(file):
            os.remove(file)

def get_company_codes():
    companies = []
    query = """
    SELECT id, code, name
    FROM krxs 
    WHERE DATE(SUBSTR(ipo, 1, 10)) <= DATE('now', '-60 days')
    """
    df = database.queryToDataframe(query)
    for _, row in df.iterrows():
        companies.append({
            'id': row['id'],
            'code': row['code'],
            'name': row['name']
        })
    return companies

def load_and_preprocess_data(params):
    start_date = params['start_date']
    scaler = MinMaxScaler(feature_range=(0, 1))
    encoder = OneHotEncoder()

    x_prices, x_companies, y_prices = [], [], []
    for info in params['infos']:
        encoded_code = encoder.fit_transform(np.array(info['code']).reshape(-1, 1)).toarray()
        df = fdr.DataReader(info['code'], start=start_date)
        if len(df) >= 60:
            prices = df['Close'].values.reshape(-1, 1)
            scaled_prices = scaler.fit_transform(prices)
            for i in range(60, len(scaled_prices)):
                x_prices.append(scaled_prices[i-60:i, 0])
                x_companies.append(encoded_code)
                y_prices.append(scaled_prices[i, 0])

    return np.array(x_prices), np.array(x_companies), np.array(y_prices), scaler, encoder

def build_or_load_model(params):
    model_path = params['model_path']
    input_shape = params['input_shape']
    num_companies = params['num_companies']

    if os.path.exists(model_path):
        print("Loading existing model...")
        model = load_model(model_path)
    else:
        print("Building a new model...")
        price_input = Input(shape=input_shape, name='price_input')
        company_input = Input(shape=(1,), name='company_input')
        lstm_layer = LSTM(50, return_sequences=False)(price_input)
        concat_layer = Concatenate()([lstm_layer, company_input])
        dense_layer = Dense(25, activation='relu')(concat_layer)
        output_layer = Dense(1, activation='linear')(dense_layer)
        model = Model(inputs=[price_input, company_input], outputs=output_layer)
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def train_and_predict(params):
    model_path = params['model_path']
    x_prices, x_companies, y_prices, scaler, encoder = load_and_preprocess_data(params)
    
    if len(x_prices) > 0:
        model = build_or_load_model(params)
        
        # 조기 종료 콜백 설정
        early_stopping = EarlyStopping(monitor='val_loss', patience=5, verbose=1, mode='min', restore_best_weights=True)
        
        model.fit([x_prices, x_companies], y_prices, epochs=10, batch_size=32, validation_split=0.2, callbacks=[early_stopping])
        
        model.save(model_path)
        with open('stock_scaler.pkl', 'wb') as f:
            pickle.dump(scaler, f)
        with open('stock_encoder.pkl', 'wb') as f:
            pickle.dump(encoder, f)

        print_predictions(model, scaler, encoder, params)
    else:
        print("Insufficient data. Cannot train the model.")

def print_predictions(model, scaler, encoder, params):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = params['start_date']
    for info in params['infos']:
        df = fdr.DataReader(info['code'], start=start_date, end=today)
        
        # 데이터가 충분한 경우에만 예측을 진행
        if len(df) >= 60:
            last_60_days = df['Close'].values[-60:].reshape(-1, 1)
            scaled_last_60_days = scaler.transform(last_60_days)  # 정규화된 데이터 사용
            company_encoded = encoder.transform([[info['code']]]).toarray().reshape(1, -1)

            predicted_price_scaled = model.predict([scaled_last_60_days.reshape(1, 60, 1), company_encoded])
            predicted_price = scaler.inverse_transform(predicted_price_scaled)
            print(f"id: {info['id']} / {params['num_companies']}, code: {info['code']}, name: {info['name']}, 예측된 내일 'Close' 가격: {predicted_price[0][0]:.2f}")
        else:
            # 데이터가 충분하지 않은 업체에 대해서는 메시지 출력 후 다음 업체로 넘어감
            print(f"id: {info['id']} / {params['num_companies']}, code: {info['code']}, name: {info['name']}, 충분한 데이터가 없습니다.")

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

        infos = get_company_codes()
        start_date = '2020-01-01'  # 임의로 선택한 시작 날짜
        params = {'model_path': model_path, 'infos': infos, 'start_date': start_date}
        print_predictions(model, scaler, encoder, params)
    else:
        print("필요한 모델 또는 전처리 파일이 없습니다. 먼저 학습 모드(F1)를 실행해 주세요.")

def on_press(event):
    if event.name == 'f9':
        print('학습 모드...')
        infos = get_company_codes()
        start_date = '2020-01-01'  # 임의로 선택한 시작 날짜
        params = {'model_path': 'integrated_stock_model.h5', 'infos': infos, 'start_date': start_date, 'input_shape': (60, 1), 'num_companies': len(infos)}
        train_and_predict(params)
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

if __name__ == '__main__':
    main()
