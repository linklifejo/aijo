import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader as pdr
import datetime 
import tensorflow as tf
from tensorflow import keras 
from keras.callbacks import ModelCheckpoint
from keras.models import Model, Sequential, load_model
from keras.layers import Dense, LSTM, Input, Concatenate,GRU, Dropout
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
import FinanceDataReader as fdr
import shutil  # shutil 모듈 임포트
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
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='training_log.log', filemode='a')
logging.info("프로그램 시작")
def create_company_directory(company_code):
    directory = f"./models/{company_code}"
    if not os.path.exists(directory):
        os.makedirs(directory)


# 기존 함수 및 모델 정의는 여기에 포함 (create_company_directory, get_company_codes 등)

def custom_load_model(company_code):
    directory = f"./models/{company_code}/"
    checkpoint_dir = os.path.join(directory, "checkpoints")
    latest_checkpoint = tf.train.latest_checkpoint(checkpoint_dir)

    if latest_checkpoint:
        print(f"최신 체크포인트에서 모델 로드: {latest_checkpoint}")
        model = build_lstm_model((60, 1))  # 모델 구성 함수 호출
        model.load_weights(latest_checkpoint)
        return model
    else:
        model_path = os.path.join(directory, "model.keras")
        if os.path.exists(model_path):
            print(f"모델 파일에서 모델 로드: {model_path}")
            return load_model(model_path)
        else:
            return None

def save_model(model, company_code):
    try:
        directory = f"./models/{company_code}/"
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # 모델 전체를 저장
        model_path = os.path.join(directory, "model.keras")
        model.save(model_path)
        print(f"모델 저장됨: {model_path}")
    except Exception as e:
        logging.exception("save_model 함수에서 예외 발생")




def files():
    return {
        'model': 'integrated_stock_model1.h5',
        'scaler': 'stock_scaler1.pkl',
        'encoder': 'stock_encoder1.pkl'
    }


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

def build_lstm_model(input_shape):
    model = Sequential()
    model.add(Input(shape=input_shape))
    model.add(LSTM(50, return_sequences=True))
    model.add(Dropout(0.5))  # 드롭아웃 추가, 20% 비율
    model.add(LSTM(64, return_sequences=False))
    model.add(Dropout(0.5))  # 드롭아웃 추가, 20% 비율
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mse', optimizer='rmsprop')
    return model

def load_data(code):
    try:
        start_date = (datetime.datetime.now() - datetime.timedelta(days=1000)).strftime('%Y-%m-%d')
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        data = fdr.DataReader(code, start=start_date, end=today)
    except Exception as e:
        logging.exception("load_data 함수에서 예외 발생")
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

def predict_model(x_test, lstm_models, close_prices, seq_len):
    # 각 모델로부터 예측 수행
    predictions = np.array([model.predict(x_test) for model in lstm_models])
    # 예측값의 평균 계산
    mean_predictions = np.mean(predictions, axis=0)
    # 마지막 예측값을 역정규화하여 실제 가격으로 변환
    last_window = close_prices[-seq_len-1:-1]  # Adjust for the correct window
    predicted_price = denormalize(mean_predictions[-1][0], last_window)  # 배열에서 첫 번째 원소 추출
    # 예측값을 반올림하여 정수로 변환
    predicted_price = round(predicted_price)
    return predicted_price, mean_predictions


def decisions(predicted_price, close_prices):
    # 예측된 가격 역변환 (첫 번째 특성만 사용)
    price_change = (predicted_price - close_prices[-1]) / close_prices[-1]

    decision_threshold = 0.01
    decision = "hold"
    if price_change > decision_threshold:
        decision = "buy"
    elif price_change < -decision_threshold:
        decision = "sell"
    return decision

def result(predicted_price, close_prices):
    return decisions(predicted_price, close_prices)

def show_decision(predicted_price, close_prices):
    decision = result(predicted_price, close_prices)
    print(f'현재가: {close_prices[-1]} , 예측가격: {int(predicted_price)} , 결정: {decision}')
    return  decision, predicted_price, close_prices[-1]

def show_chart(y_test, mean_predictions):
    # 차트 그리기
    fig = plt.figure(facecolor='white', figsize=(20, 10))
    ax = fig.add_subplot(111)
    ax.plot(y_test, label='True')
    ax.plot(mean_predictions, label='Prediction')
    ax.legend()
    plt.show()



def initialize():
    try:
        model_directory = "./models/"
        if os.path.exists(model_directory):
            for company_code in os.listdir(model_directory):
                company_path = os.path.join(model_directory, company_code)
                # 디렉터리 내의 파일 및 하위 디렉터리 삭제
                shutil.rmtree(company_path)  # shutil.rmtree() 사용
            print("모든 모델과 회사 디렉터리가 초기화되었습니다.")
            logging.info("모든 모델과 회사 디렉터리가 초기화되었습니다.")
        else:
            print("초기화할 모델 디렉터리가 존재하지 않습니다.")
    except Exception as e:
        logging.exception("initialize 함수에서 예외 발생")
# 전역 변수로 프로그램 및 학습 실행 상태를 관리합니다.
running = True
is_working = False
stop_training = False

def on_q_press(e):
    global stop_training
    stop_training = True
    print("'q' 키가 눌려 학습 중단 요청이 처리됩니다.")

def on_esc_press():
    global running
    running = False
    print("프로그램 종료 요청됨")

# 모델을 관리하는 딕셔너리 생성
company_models = {}

def train_and_company():
    global is_working, stop_training, running
    if is_working:
        logging.info("작업이 이미 진행 중입니다.")
        print("작업이 이미 진행 중입니다.")
        return
    is_working = True
    stop_training = False

    def on_q_press(event=None):  # 'q' 키 이벤트 핸들러 함수
        global stop_training
        stop_training = True
        print("'q' 키가 눌려 학습 중단 요청이 처리됩니다.")

    keyboard.on_press_key("q", on_q_press)  # 'q' 키에 이벤트 핸들러 등록
    try:
        companies = get_company_codes()
        for company in companies:
            if stop_training or not running:
                print(f"{company['code']} 학습 중단, f9: 학습, Esc: 종료, q: 잠시중단")
                break

            print(f"{company['code']} 학습 시작")
            create_company_directory(company['code'])
            data = load_data(company['code'])
            if data is not None:
                x_train, y_train, x_test, y_test, close_prices, seq_len = train_test_data(data)

                model = build_lstm_model((seq_len, 1))
                
                cp_callback = ModelCheckpoint(filepath=f"./models/{company['code']}/checkpoints/cp-{{epoch:04d}}.weights.h5",
                                            save_weights_only=True, verbose=1, save_freq='epoch')
                
                es_callback = EarlyStopping(monitor='val_loss', patience=5, verbose=1, mode='min', restore_best_weights=True)

                # 모델 학습
                model.fit(x_train, y_train, validation_split=0.1, epochs=10, batch_size=64, callbacks=[cp_callback, es_callback], verbose=1)
                
                # 학습 중단 검사
                if stop_training:
                    print(f"학습이 사용자 요청에 의해 중단되었습니다: {company['code']}")
                    break

                save_model(model, company['code'])  # 마지막 에포크 번호 전달

                predicted_price, mean_predictions = predict_model(x_test, [model], close_prices, seq_len)
                show_decision(predicted_price, close_prices)

    except Exception as e:
        logging.exception("train_and_company 함수에서 예외 발생")
    finally:
        keyboard.unhook_key("q")  # 'q' 키 감지 해제
        is_working = False
        stop_training = False
def start_training_thread():
    training_thread = threading.Thread(target=train_and_company)
    training_thread.start()
    
def buy_and_sell(code):
    model = custom_load_model(code)
    if model is not None:
        lstm_models = [model]
        data = load_data(code )
        if data is not None:
            _, _, x_test, y_test, close_prices, seq_len = train_test_data(data)
            predicted_price, mean_predictions = predict_model(x_test, lstm_models, close_prices, seq_len)
            return show_decision(predicted_price, close_prices)
    return None,None,None
def calculate_percentage(predicted_value, actual_value):
    if predicted_value is None or actual_value is None:
        # 오류 메시지를 출력하거나, 기본값을 반환하거나, 예외를 발생시킵니다.
        print("예측값 또는 실제값이 None입니다.")
        return 0  # 또는 적절한 기본값 또는 예외 처리
    else:
        difference_percentage = ((predicted_value - actual_value) / actual_value) * 100
        return round(difference_percentage)

def buy_companies(chk='buy'):
    # 'decision' 필드가 제공된 'chk' 값과 일치하는 행을 데이터베이스에서 조회합니다.
    query_data = database.queryByField('predicts', 'decision', chk)
    
    # 'percent' 열을 기준으로 데이터프레임을 내림차순으로 정렬합니다.
    query_data_sorted = query_data.sort_values(by='percent', ascending=False)
    
    # 'code' 열을 리스트로 추출합니다.
    data = query_data_sorted['code'].tolist()
    
    return data


def main():
    keyboard.add_hotkey('f9', start_training_thread)  # 'f9'로 학습 시작 스레드를 호출
    keyboard.add_hotkey('f10', initialize)  # 'f10'으로 초기화
    keyboard.add_hotkey('esc', on_esc_press)  # 'esc'로 프로그램 종료
    util.clear()
    print("실행중....!: f9: 학습, f10: 초기화, Esc: 종료")

    while running:
        time.sleep(0.1)

    # 스레드 및 핫키 해제
    if is_working:
        print("학습 스레드 종료를 기다립니다...")
        while is_working:
            time.sleep(0.1)

    keyboard.clear_all_hotkeys()
    print("프로그램이 종료되었습니다.")

if __name__ == '__main__':
    main()