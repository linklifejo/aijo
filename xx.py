import pickle
import datetime
from keras.models import load_model
import FinanceDataReader as fdr
from sklearn.preprocessing import OneHotEncoder
import numpy as np

# 모델, 스케일러, 인코더 로드
MODEL_PATH = 'integrated_stock_model.h5'
SCALER_PATH = 'stock_scaler.pkl'
ENCODER_PATH = 'stock_encoder.pkl'

model = load_model(MODEL_PATH)
with open(SCALER_PATH, 'rb') as f:
    scaler = pickle.load(f)
with open(ENCODER_PATH, 'rb') as f:
    encoder = pickle.load(f)

def predict_price_for_code(code):
    # 데이터 요청 기간을 확장합니다 (예: 최근 100일)
    start_date = (datetime.datetime.now() - datetime.timedelta(days=100)).strftime('%Y-%m-%d')
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    try:
        # 주어진 업체 코드가 인코더에 존재하는지 확인합니다.
        if code not in encoder.categories_[0]:
            print(f"알 수 없는 업체 코드 {code}")
            return None

        # 최근 데이터 로드
        df = fdr.DataReader(code, start=start_date, end=today)

        # 데이터가 충분하지 않은 경우, None을 반환합니다.
        if len(df) < 60:
            print(f"업체 '{code}'에 대한 데이터가 충분하지 않습니다.")
            return None

        # 스케일링 및 모델 입력 형태로 변환
        last_60_days_scaled = scaler.transform(df['Close'][-60:].values.reshape(-1, 1))
        model_input = last_60_days_scaled.reshape(1, -1, 1)

        # 업체 코드 인코딩
        company_encoded = encoder.transform([[code]]).toarray()

        # 예측 실행
        predicted_price_scaled = model.predict([model_input, company_encoded])
        predicted_price = scaler.inverse_transform(predicted_price_scaled)[0][0]

        # 예측된 가격에 따라 매수, 매도, 보류 결정
        current_price = df['Close'].values[-1]
        price_change = (predicted_price - current_price) / current_price

        decision_threshold = 0.05  # 5% 변동을 기준으로 결정
        if price_change > decision_threshold:
            decision = "매수(Buy)"
        elif price_change < -decision_threshold:
            decision = "매도(Sell)"
        else:
            decision = "보류(Hold)"

        return predicted_price, decision

    except Exception as e:
        print(f"예측 중 오류 발생: {e}")
        return None, None

# 함수 사용 예시
code = '210120'  # 예시 업체 코드
predicted_price, decision = predict_price_for_code(code)
if predicted_price is not None:
    print(f"업체 '{code}'의 예측된 내일 가격: {predicted_price:.2f}, 결정: {decision}")
