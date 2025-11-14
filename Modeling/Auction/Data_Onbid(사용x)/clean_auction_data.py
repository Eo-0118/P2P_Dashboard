
import pandas as pd
import os

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auction_entire.csv")

print(f"'{file_path}' 파일 정리를 시작합니다.")

try:
    df = pd.read_csv(file_path)
    original_rows = len(df)
    print(f"원본 데이터: 총 {original_rows}개 행")

    # 제거할 'result' 값 목록
    results_to_remove = ['인터넷입찰마감', '입회검사대기', '입회검사완료']
    
    # 제거할 행의 조건을 정의
    condition_to_remove = df['result'].isin(results_to_remove)
    
    rows_to_remove_count = condition_to_remove.sum()

    if rows_to_remove_count > 0:
        # 조건에 해당하지 않는 행들만 남기기
        df_cleaned = df[~condition_to_remove]
        
        # 기존 파일을 덮어쓰기
        df_cleaned.to_csv(file_path, index=False, encoding='utf-8-sig')
        
        print(f"\n총 {rows_to_remove_count}개의 불필요한 행을 제거했습니다.")
        print(f"파일이 {len(df_cleaned)}개의 행으로 업데이트되었습니다.")
    else:
        print("\n제거할 행이 없습니다. 파일은 변경되지 않았습니다.")

except FileNotFoundError:
    print(f"오류: '{file_path}'을 찾을 수 없습니다.")
except Exception as e:
    print(f"오류가 발생했습니다: {e}")
