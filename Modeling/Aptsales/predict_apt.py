
import joblib
import pandas as pd

# 1. 학습된 모델과 인코더, 컬럼 정보 불러오기
model = joblib.load('rf_model.joblib')
te = joblib.load('target_encoder.joblib')
ohe = joblib.load('onehot_encoder.joblib')
model_columns = joblib.load('model_columns.joblib')

def predict_price(input_data):
    """
    아파트 정보를 입력받아 예상 매매가를 예측하는 함수
    :param input_data: dict 형태의 아파트 정보
    :return: float 형태의 예측 가격 (만원 단위)
    """
    # 1. 입력 데이터를 DataFrame으로 변환
    df = pd.DataFrame([input_data])

    # 2. 인코딩 적용 (학습 때 사용했던 인코더 사용)
    # Target Encoding
    df_encoded = te.transform(df)
    # One-Hot Encoding
    df_encoded = ohe.transform(df_encoded)

    # 3. 컬럼 정렬 (학습 때 사용된 컬럼 순서와 동일하게 맞추기)
    # 모델이 학습하지 않은 새로운 지역(시군구)이 들어올 경우, 해당 컬럼이 없으므로 에러가 발생.
    # reindex를 통해 없는 컬럼은 0으로 채워준다.
    df_aligned = df_encoded.reindex(columns=model_columns, fill_value=0)

    # 4. 가격 예측
    prediction = model.predict(df_aligned)

    return prediction[0]

if __name__ == '__main__':
    # 예측해보고 싶은 아파트의 정보를 dict 형태로 입력
    # 예시: 서울특별시 강남구 개포동의 한 아파트 정보
    sample_data = {
        '시군구': '서울특별시 강남구 개포동',
        '법정동코드': 1168010300,
        '본번': 658,
        '부번': 0,
        '단지명': '개포6차우성아파트1동~8동',
        '전용면적(㎡)': 167.1,
        '계약년월': 202501, # 예측하고 싶은 시점
        '층': 3,
        '건축년도': 1987,
        '가계대출_금리': 3.5 # 예측 시점의 금리 (가정)
    }

    # 함수 호출
    predicted_price = predict_price(sample_data)

    # 결과 출력
    print(f"입력된 아파트 정보: \n{sample_data}")
    print("---" * 10)
    # 억 단위로 변환하여 보기 쉽게 출력
    predicted_price_eok = int(predicted_price / 10000)
    predicted_price_man = int(predicted_price % 10000)
    print(f"==> 예상 매매가: 약 {predicted_price_eok}억 {predicted_price_man}만 원")
