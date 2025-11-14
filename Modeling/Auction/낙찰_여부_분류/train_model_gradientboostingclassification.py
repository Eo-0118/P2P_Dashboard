import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score
import os
import joblib

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
    print(f"오류: '{input_file}'을 찾을 수 없습니다.")
    exit()

# 타겟 변수(낙찰가) 및 숫자형 특성 전처리
cols_to_clean = ['minprice', 'landarea', 'aptarea', '본번', '부번', '건축년도', 'floor']
for col in cols_to_clean:
    df[col] = pd.to_numeric(df[col], errors='coerce')

#낙찰 결과 원-핫 인코딩
status_map = {'낙찰': 1,
              '낙찰\n (낙찰후취소)': 1,
              '유찰\n (수의계약완료)' : 1,
              '유찰\n (수의계약가능)' : 0,
              '유찰': 0}
df['result'] = df['result'].map(status_map)
# df.dropna(subset=['winprice'], inplace=True)
# df = df[df['winprice'] > 0]
# print(f"유효한 낙찰가 데이터: {len(df)}개")

# # --- 이상치 제거 ---
# if not df.empty:
#     print(f"\n이상치 제거 전 데이터 개수: {len(df)}")
#     index_to_drop = df['winprice'].idxmax()
#     df.drop(index_to_drop, inplace=True)
#     print(f"이상치 제거 후 데이터 개수: {len(df)}")
# else:
#     print("처리할 데이터가 없습니다.")
#     exit()

# --- 특성 선택 (모든 특성 사용) ---
features = ['minprice', 'landarea', 'aptarea', '법정동코드', 'year', 'month', '본번', '부번', '건축년도', 'floor']
target = 'result'
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

gbc = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
print("Gradient Boosting Classifier 모델 학습 중...")
gbc.fit(X_train, y_train)
print("모델 학습 완료.")

# --- 모델 저장 ---
model_filename = 'gradient_boosting_classifier_model.joblib'
model_path = os.path.join(os.path.dirname(__file__), model_filename)
joblib.dump(gbc, model_path)
print(f"학습된 모델이 '{model_path}' 파일로 저장되었습니다.")

# --- 3. 모델 평가 ---
print("\n--- 3. 모델 성능 평가 ---")

y_pred = gbc.predict(X_test)
y_pred_proba = gbc.predict_proba(X_test)[:, 1]

# 혼동 행렬
conf_matrix = confusion_matrix(y_test, y_pred)
# 정확도, 정밀도, 재현율, F1 스코어
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_pred_proba)

print("  [ 모델 평가 결과 ]")
print(f"  - 혼동 행렬 (Confusion Matrix): \n{conf_matrix}")
print(f"  - 정확도 (Accuracy): {accuracy:.4f}")
print(f"  - 정밀도 (Precision): {precision:.4f}")
print(f"  - 재현율 (Recall): {recall:.4f}")
print(f"  - F1 스코어 (F1 Score): {f1:.4f}")
print(f"  - ROC AUC: {roc_auc:.4f}")

# --- 4. 새로운 데이터에 대한 낙찰 확률 예측 ---
print("\n--- 4. 새로운 데이터 예측 ---")

# 예측할 새로운 데이터를 준비합니다.
# 특성(features)은 모델 학습에 사용된 것과 동일한 순서와 개수여야 합니다.
# features = ['minprice', 'landarea', 'aptarea', '법정동코드', 'year', 'month', '본번', '부번', '건축년도', 'floor']
# new_data_point = [[286700000, 39.86, 75.89, 1111018600, 2020, 12, 105, 22, 2002, 2]] # 이전 데이터
# new_data_point = [[350000000, 20.151, 55.7, 1138010400, 2020, 11, 468, 4, 2019, 14]] # 새로운 데이터
new_data_point = [[1437750000, 122.62, 213.07, 1111018300, 2020, 12, 66, 1, 2009, 3]] # 유찰 데이터
# 데이터를 DataFrame으로 변환 (학습 데이터와 동일한 컬럼 사용)
new_df = pd.DataFrame(new_data_point, columns=X_train.columns)

# 낙찰 확률 예측
# predict_proba()는 [유찰 확률, 낙찰 확률]을 반환합니다.
# 우리는 두 번째 값인 낙찰 확률을 선택합니다 ([:, 1]).
success_probability = gbc.predict_proba(new_df)[:, 1]

# 결과 출력
print(f"입력된 데이터의 낙찰 확률: {success_probability[0] * 100:.2f}%")