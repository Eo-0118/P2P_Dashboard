
import pandas as pd
import os

# 변환할 Excel 파일과 저장할 CSV 파일 경로 설정
excel_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auction_entire.xlsx")
csv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auction_entire.csv")

try:
    # Excel 파일을 읽어옵니다.
    df = pd.read_excel(excel_file, engine='openpyxl')

    # CSV 파일로 저장합니다. (한글 깨짐 방지)
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')

    print(f"'{excel_file}' 파일을 성공적으로 '{csv_file}'로 변환했습니다.")

except FileNotFoundError:
    print(f"오류: '{excel_file}'을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
except Exception as e:
    print(f"파일 변환 중 오류가 발생했습니다: {e}")
