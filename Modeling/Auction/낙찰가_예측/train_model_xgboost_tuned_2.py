import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
import os

def mspe_objective(y_true, y_pred):
    """
    Mean Squared Percentage Error (MSPE) objective function for XGBoost.
    """
    # To avoid division by zero, add a small epsilon where y_true is zero
    y_true = np.where(y_true == 0, 1e-8, y_true)
    
    # Gradient (first derivative)
    grad = -2 * (y_true - y_pred) / (y_true ** 2)
    
    # Hessian (second derivative)
    hess = 2 / (y_true ** 2)
    
    return grad, hess

# --- 1. 데이터 준비 ---
# 파일 경로 설정
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Data')
input_file = os.path.join(data_dir, 'auction_preprocessed.csv')

# 데이터 불러오기
try:
    df = pd.read_csv(input_file)
    print(f"'{input_file}' 파일을 성공적으로 불러왔습니다. (총 {len(df)}개 데이터)")
except FileNotFoundError:
    print(f"오류: '{input_file}'을 찾을 수 없습니다.")
    exit()

# 타겟 변수(낙찰가) 및 숫자형 특성 전처리
cols_to_clean = ['winprice', 'minprice', 'landarea', 'aptarea', '본번', '부번', '건축년도', 'floor']
for col in cols_to_clean:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df.dropna(subset=['winprice'], inplace=True)
df = df[df['winprice'] > 0]
print(f"유효한 낙찰가 데이터: {len(df)}개")

# --- 이상치 제거  ---
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

# XGBoost Regressor 사용 (사용자 정의 목적 함수 적용)
xgb_reg = xgb.XGBRegressor(obj=mspe_objective, random_state=42)

# 하이퍼파라미터 그리드 설정
param_grid = {
    'n_estimators': [100, 200, 300, 400, 500],
    'max_depth': [3, 5, 7, 9],
    'learning_rate': [0.01, 0.05, 0.1, 0.15, 0.2],
    'subsample': [0.7, 0.8, 0.9, 1.0],
    'colsample_bytree': [0.7, 0.8, 0.9, 1.0],
    'gamma': [0, 0.1, 0.2]
}

# GridSearchCV 설정
grid_search = GridSearchCV(estimator=xgb_reg, param_grid=param_grid, cv=3, n_jobs=-1, verbose=2, scoring='r2')

print("XGBoost 하이퍼파라미터 튜닝 중 (사용자 정의 목적 함수: MSPE)...")
grid_search.fit(X_train, y_train)
print("하이퍼파라미터 튜닝 완료.")

print(f"\n최적 하이퍼파라미터: {grid_search.best_params_}")

# 최적의 모델로 예측
best_model = grid_search.best_estimator_

# --- 3. 모델 평가 ---
print("\n--- 3. 모델 성능 평가 ---")

y_pred = best_model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
mape = mean_absolute_percentage_error(y_test, y_pred)

print(f"  - R² (결정계수): {r2:.4f}")
print(f"  - MAE (평균 절대 오차): {mae:,.0f} 원")
print(f"  - MSE (평균 제곱 오차): {mse:,.0f}")
print(f"  - MAPE (평균 절대 백분율 오차): {mape:.2%}")
