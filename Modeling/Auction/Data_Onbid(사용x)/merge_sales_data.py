
import pandas as pd
import glob
import os

# 데이터가 있는 폴더 경로
data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sales_data")

# 해당 폴더의 모든 .xlsx 파일 경로를 가져옵니다.
all_files = glob.glob(os.path.join(data_path, "*.xlsx"))

# 각 파일을 읽어 데이터프레임 리스트를 만듭니다.
li = []
for filename in all_files:
    df = pd.read_excel(filename, engine='openpyxl')
    li.append(df)

# 모든 데이터프레임을 하나로 합칩니다.
if li:
    combined_df = pd.concat(li, axis=0, ignore_index=True)

    # 합쳐진 파일을 저장할 경로
    output_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sales_data", "sales_data_combined.csv")

    # CSV 파일로 저장합니다. (한글 깨짐 방지)
    combined_df.to_csv(output_filename, index=False, encoding='utf-8-sig')

    print(f"{len(all_files)}개의 파일을 합쳐 '{output_filename}' 파일로 저장했습니다.")
    print(f"총 {len(combined_df)}개의 행이 저장되었습니다.")
else:
    print("합칠 파일이 없습니다.")
