import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader as pdr
import datetime 
from tensorflow import keras
from keras.models import Model,Sequential
from keras.layers import Dense,LSTM,Input
from sklearn.preprocessing import MinMaxScaler
import FinanceDataReader as fdr
date = datetime.datetime(2022, 1, 1)
code = '000150'
if code and date:
    df = fdr.DataReader(code, date)
    # if not df.empty:
    #     data = df.sort_index(ascending=True).loc[:, 'Close']

# 필요한 컬럼 선택, 여기서는 'Close' 가격을 사용
data = df.filter(['Close'])
dataset = data.values

scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(dataset)

# 훈련 데이터 세트 생성
train_data_len = int(len(dataset) * 0.8)
train_data = scaled_data[0:train_data_len, :]

# x_train과 y_train 데이터 세트 생성
x_train, y_train = [], []

for i in range(60, len(train_data)):
    x_train.append(train_data[i-60:i, 0])
    y_train.append(train_data[i, 0])


# 데이터를 numpy 배열로 변환
x_train, y_train = np.array(x_train), np.array(y_train)

# LSTM에 맞는 데이터 형태로 변환
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

# LSTM 모델 구축
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
model.add(LSTM(50, return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))

# 모델 컴파일
model.compile(optimizer='adam', loss='mean_squared_error')

model.fit(x_train, y_train, batch_size=1, epochs=1)
# 테스트 데이터 세트 생성
test_data = scaled_data[train_data_len - 60: , :]
x_test, y_test = [], dataset[train_data_len:, :]

for i in range(60, len(test_data)):
    x_test.append(test_data[i-60:i, 0])

x_test = np.array(x_test)
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

# 모델을 사용하여 값 예측
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

# RMSE 값 계산
rmse = np.sqrt(np.mean(predictions - y_test)**2)
train = data[:train_data_len]
valid = data[train_data_len:]
valid['Predictions'] = predictions
plt.rcParams['font.family'] = 'Malgun Gothic'  # 맑은 고딕으로 설정
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호가 정상적으로 표시되도록 설정
plt.figure(figsize=(16,8))
plt.title('한국거래소 업체별 예측')
plt.xlabel('거래일자', fontsize=18)
plt.ylabel('대한민국 화폐 원', fontsize=18)
plt.plot(train['Close'])
plt.plot(valid[['Close', 'Predictions']])
plt.legend(['Train', 'Val', 'Predictions'], loc='lower right')
plt.show()

model.save('my_model.h5')  # HDF5 파일 형식으로 저장


# # 모델 불러오기
# loaded_model = load_model('my_model.h5')

# # 모델 재교육
# model.fit(x_additional, y_additional, batch_size=32, epochs=20, initial_epoch=10)
# # 예측을 위한 새로운 데이터 준비
# x_new = ...  # 새로운 입력 데이터

# # 모델을 사용하여 예측 수행
# predictions = model.predict(x_new)

# # 예측 결과 사용
# ...