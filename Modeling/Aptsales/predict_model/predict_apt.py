
import joblib
import pandas as pd

# City mapping for dynamic model loading
CITY_MAP = {
    '서울': 'seoul',
    '부산': 'busan',
    '대구': 'daegu',
    '인천': 'incheon',
    '광주': 'gwangju',
    '대전': 'daejeon',
    '울산': 'ulsan',
    '경기': 'gyeonggi'
}

# Global variables to store loaded models and encoders to avoid reloading
_loaded_models = {}
_loaded_tes = {}
_loaded_ohes = {}
_loaded_model_columns = {}

def _load_city_models(city_korean):
    """Loads models and encoders for a given city, caching them."""
    city_english = None
    for k, v in CITY_MAP.items():
        if city_korean.startswith(k):
            city_english = v
            break
    
    if not city_english:
        raise ValueError(f"Unsupported city: {city_korean}. Please provide a valid city name.")

    if city_english not in _loaded_models:
        print(f"Loading models for {city_korean} ({city_english})...")
        try:
            _loaded_models[city_english] = joblib.load(f'rf_model_{city_english}.joblib')
            _loaded_tes[city_english] = joblib.load(f'target_encoder_{city_english}.joblib')
            _loaded_model_columns[city_english] = joblib.load(f'model_columns_{city_english}.joblib')
            
            # Load OneHotEncoder for cities that use it
            if city_english in ['incheon', 'seoul']:
                _loaded_ohes[city_english] = joblib.load(f'onehot_encoder_{city_english}.joblib')
            else:
                _loaded_ohes[city_english] = None # Explicitly set to None for other cities
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Model files for {city_korean} not found. Please ensure {e.filename} exists in the current directory.")
    
    return _loaded_models[city_english], _loaded_tes[city_english], _loaded_ohes[city_english], _loaded_model_columns[city_english]

def predict_price(input_data):
    """
    아파트 정보를 입력받아 예상 매매가를 예측하는 함수
    :param input_data: dict 형태의 아파트 정보
    :return: float 형태의 예측 가격 (만원 단위)
    """
    # --- 1. 입력 데이터 변환 ---
    # 모델이 학습한 형태로 입력 데이터를 재구성합니다.
    sigungu_str = f"{input_data.get('시/도', '')} {input_data.get('구', '')} {input_data.get('동', '')}".strip()
    
    model_input = {
        '시군구': sigungu_str,
        '법정동코드': input_data.get('법정동코드'),
        '본번': input_data.get('본번'),
        '부번': input_data.get('부번'),
        '단지명': input_data.get('아파트명'),
        '전용면적(㎡)': input_data.get('전용면적'),
        '계약년월': input_data.get('계약년월'),
        '층': input_data.get('층'),
        '건축년도': input_data.get('건축년도'),
        '가계대출_금리': input_data.get('가계대출_금리')
    }

    # 필수 입력값 확인
    required_fields = ['시군구', '법정동코드', '단지명', '전용면적(㎡)', '계약년월', '층', '건축년도', '가계대출_금리']
    for field in required_fields:
        if model_input[field] is None:
            # '본번', '부번'은 없을 수 있으므로 예외 처리
            if field not in ['본번', '부번']:
                 raise ValueError(f"필수 입력값이 누락되었습니다: {field}")

    # --- 2. 도시별 모델 및 인코더 로드 ---
    city_korean = input_data.get('시/도', '').strip()
    if not city_korean:
        raise ValueError("입력 데이터에 '시/도' 필드가 반드시 포함되어야 합니다.")
        
    model, te, ohe, model_columns = _load_city_models(city_korean)

    # --- 3. 예측을 위한 데이터프레임 생성 ---
    df = pd.DataFrame([model_input])

    # --- 4. 인코딩 적용 ---
    # Target Encoding
    df_encoded = te.transform(df)
    
    # One-Hot Encoding (해당 도시 모델이 OHE를 사용하는 경우)
    if ohe:
        df_encoded = ohe.transform(df_encoded)

    # --- 5. 컬럼 정렬 ---
    # 학습 시점의 컬럼 순서와 동일하게 맞추고, 없는 컬럼은 0으로 채웁니다.
    df_aligned = df_encoded.reindex(columns=model_columns, fill_value=0)

    # --- 6. 가격 예측 ---
    prediction = model.predict(df_aligned)

    return prediction[0]

if __name__ == '__main__':
    # --- 예측할 아파트 정보 입력 ---
    # 사용자가 제공한 형식에 따른 예시 데이터
    sample_data = {
        #--- 사용자 입력 ---
        '시/도': '서울특별시',
        '구': '강남구',
        '동': '개포동',
        '본번': 658,
        '부번': 0,
        '아파트명': '개포6차우성아파트1동~8동',
        '전용면적': 167.1,
        '건축년도': 1987,
        #--- 다른 모델에서 사용될 수 있는 변수 ---
        '동(선택)': '101동',
        '호수(선택)': '101호',
        '감정가격(원)': 2500000000,
        '선순위채권 가격(원)': 500000000,
        #--- 예측을 위해 추가로 필요한 변수 (사용자가 제공해야 함) ---
        '법정동코드': 1168010300,
        '층': 3,
        '계약년월': 202501, # 예측하고 싶은 시점 (YYYYMM 형식)
        '가계대출_금리': 3.5 # 예측 시점의 금리
    }

    try:
        # 함수 호출
        predicted_price = predict_price(sample_data)

        # 결과 출력
        print("--- 입력된 아파트 정보 ---")
        for key, value in sample_data.items():
            print(f"- {key}: {value}")
        print("---" * 10)
        
        # 억 단위로 변환하여 보기 쉽게 출력
        predicted_price_eok = int(predicted_price / 10000)
        predicted_price_man = int(predicted_price % 10000)
        print(f"==> 예상 매매가: 약 {predicted_price_eok}억 {predicted_price_man}만 원")

    except (ValueError, FileNotFoundError) as e:
        print(f"[ERROR] 예측 중 오류가 발생했습니다: {e}")
