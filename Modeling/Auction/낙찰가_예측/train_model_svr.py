
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR # SVR 모델 import
from sklearn.preprocessing import StandardScaler # 특성 스케일링을 위한 import
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
import os

# --- 1. 데이터 준비 ---
print("--- 1. 데이터 준비 시작 ---")

# 파일 경로 설정
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Data')
input_file = os.path.join(data_dir, 'auction_preprocessed.csv')

# 데이터 불러오기
try:
    df = pd.read_csv(input_file)
    print(f"'{input_file}' 파일을 성공적으로 불러왔습니다. (총 {len(df)}개 데이터)")
except FileNotFoundError:
    print(f"오류: '{input_file}'을(를) 찾을 수 없습니다.")
    exit()

# 타겟 변수(낙찰가) 및 숫자형 특성 전처리
cols_to_clean = ['winprice', 'minprice', 'landarea', 'aptarea', '본번', '부번', '건축년도', 'floor']
for col in cols_to_clean:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df.dropna(subset=['winprice'], inplace=True)
df = df[df['winprice'] > 0]
print(f"유효한 낙찰가 데이터: {len(df)}개")

# --- 이상치 제거 ---
if not df.empty:
    index_to_drop = df['winprice'].nlargest(4).index
    df.drop(index_to_drop, inplace=True)

# --- 특성 선택 (모든 특성 사용) ---
features = ['minprice', 'landarea', 'aptarea', '법정동코드', 'year', 'month', '본번', '부번', '건축년도', 'floor']
target = 'winprice'
df_model = df[features + [target]].copy()

# 숫자형으로 변환 및 NaN 처리
for col in features:
    df_model[col] = pd.to_numeric(df_model[col], errors='coerce').fillna(0)

print(f"\n전처리 완료. 총 {len(df_model.columns)}개의 특성으로 모델링을 시작합니다.")

# --- 2. 모델 학습 ---
print("\n--- 2. 모델 학습 시작 ---")

X = df_model.drop(target, axis=1)
y = df_model[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 특성 스케일링
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# SVR 모델 사용
svr = SVR(kernel='rbf') # 가장 일반적인 RBF 커널 사용
print("SVR 모델 학습 중...")
svr.fit(X_train_scaled, y_train)
print("모델 학습 완료.")

# --- 3. 모델 평가 ---
print("\n--- 3. 모델 성능 평가 ---")

y_pred = svr.predict(X_test_scaled)

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
mape = mean_absolute_percentage_error(y_test, y_pred)

print(f"  - R² (결정계수): {r2:.4f}")
print(f"  - MAE (평균 절대 오차): {mae:,.0f} 원")
print(f"  - MSE (평균 제곱 오차): {mse:,.0f}")
print(f"  - MAPE (평균 절대 백분율 오차): {mape:.2%}")
