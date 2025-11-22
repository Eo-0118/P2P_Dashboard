import pandas as pd
import os

# --- 1. 데이터 준비 ---
data_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(data_dir, 'auction_preprocessed.csv')

try:
    df = pd.read_csv(input_file)
except FileNotFoundError:
    print(f"오류: '{input_file}'을 찾을 수 없습니다.")
    exit()

# --- 2. 매핑 및 NaN 원인 분석 ---
status_map = {
    '낙찰': 1,
    '낙찰\n (낙찰후취소)': 1,
    '유찰\n (수의계약완료)': 1,
    '유찰\n (수의계약가능)': 0,
    '유찰': 0
}

mapped_result = df['result'].map(status_map)
nan_mask = mapped_result.isna()
problematic_rows = df[nan_mask]

# --- 3. 결과 출력 ---
if not problematic_rows.empty:
    print("--- 'result' 열에서 매핑되지 않고 NaN을 유발한 데이터 ---")
    print(f"총 {len(problematic_rows)}개의 행이 발견되었습니다.")
    
    print("\n[NaN을 유발한 'result' 값 종류 및 개수]")
    print(problematic_rows['result'].value_counts())
    
    print("\n--- 'location' 열 분석 ---")
    
    yongin_count = problematic_rows['location'].str.contains("용인체력단련장").sum()
    
    print(f"99개의 이상치 중 '용인체력단련장'을 포함하는 행의 수: {yongin_count}개")
    
    unique_locations = problematic_rows['location'].nunique()
    print(f"이상치에 포함된 고유 'location'의 수: {unique_locations}개")
    
    if unique_locations > 1:
        print("\n'용인체력단련장' 이외의 다른 location도 포함되어 있습니다.")
        print("\n[Location 별 이상치 개수]")
        print(problematic_rows['location'].value_counts())
    else:
        print("\n모든 이상치는 '용인체력단련장' 관련 데이터가 맞습니다.")

else:
    print("매핑되지 않는 'result' 값을 찾을 수 없습니다.")