import pandas as pd
import re
import os

# --- 파일 경로 설정 ---
data_dir = os.path.dirname(os.path.abspath(__file__))
auction_file = os.path.join(data_dir, 'auction_entire.csv')
code_file = os.path.join(data_dir, 'si_code.csv')
sales_file = os.path.join(data_dir, 'sales.xlsx')
output_processed_file = os.path.join(data_dir, 'auction_processed.csv')
output_final_file = os.path.join(data_dir, 'auction_preprocessed.csv')

# --- 1. 데이터 및 조회용 데이터 불러오기 ---
try:
    auction_df = pd.read_csv(auction_file)
    code_df = pd.read_csv(code_file)
    sales_df = pd.read_excel(sales_file)
    print("모든 소스 파일을 성공적으로 불러왔습니다.")
except FileNotFoundError as e:
    print("파일을 찾을 수 없습니다.")
    exit()

# --- 2. 조회용 데이터 준비 ---
valid_districts = set(code_df[code_df['폐지여부'] == '존재']['법정동명'].unique())
sales_df.dropna(subset=['도로명', '시군구', '번지'], inplace=True)
sales_df['도로명_키'] = sales_df['도로명'].str.strip().str.replace(' ', '')
address_lookup = {k: v for k, v in zip(sales_df['도로명_키'], sales_df[['시군구', '번지']].to_dict('records'))}
print(f"{len(valid_districts)}개의 법정동명, {len(address_lookup)}개의 도로명-지번 조회 데이터를 준비했습니다.")

# --- 3. 날짜 전처리 ---
# time 컬럼을 datetime 형식으로 변환하고, year와 month 컬럼 생성
auction_df['time'] = pd.to_datetime(auction_df['time'])
auction_df['year'] = auction_df['time'].dt.year
auction_df['month'] = auction_df['time'].dt.month
print("\n날짜 전처리 완료: 'year', 'month' 컬럼이 추가되었습니다.")


# --- 4. Helper 함수 정의 ---
def classify_address_type(location_str, districts_set):
    if not isinstance(location_str, str): return '알 수 없음'
    first_three_words = " ".join(location_str.split()[:3])
    return '지번 주소' if first_three_words in districts_set else '도로명 주소'

def parse_lot_based(location_str):
    parts = location_str.split()
    sigungu_parts = []
    for part in parts:
        if part.endswith(('시', '도', '구', '군', '동', '리', '가')):
            sigungu_parts.append(part)
        else:
            break
    sigungu = " ".join(sigungu_parts)
    remaining_parts = parts[len(sigungu_parts):]
    
    bunji, others = None, " ".join(remaining_parts)
    for i, part in enumerate(remaining_parts):
        if re.match(r'^[0-9,-]+', part):
            # 숫자와 하이픈만 남기고 나머지 문자 제거
            bunji = re.sub(r'[^0-9-]', '', part)
            others = " ".join(remaining_parts[i+1:])
            break
    return sigungu, bunji, others

def convert_street_to_lot(location_str, lookup_dict):
    address_core = re.split(r'[,(]', location_str)[0].strip()
    sigungu_match = re.match(r'\S+\s\S+', address_core)
    if not sigungu_match: return None
    road_address_part = address_core[sigungu_match.end():].strip()
    lookup_key = road_address_part.replace(' ', '')
    found_data = lookup_dict.get(lookup_key)
    if found_data:
        sigungu = found_data['시군구']
        bunji = str(found_data['번지'])
        others = location_str.split(address_core)[-1].strip(', ').strip()
        return sigungu, bunji, others
    else:
        return None

def process_row(row):
    location = row['location']
    addr_type = classify_address_type(location, valid_districts)
    if addr_type == '도로명 주소':
        result = convert_street_to_lot(location, address_lookup)
        if result is not None:
            return result
    return parse_lot_based(location)

# --- 4. 주소 전처리 실행 ---
print("\n1단계: 주소 전처리를 시작합니다...")
auction_df[['시군구', '번지', '이외']] = auction_df.apply(process_row, axis=1, result_type='expand')
print("1단계 완료: 주소 분리 작업이 완료되었습니다.")

# --- 5. 번지 데이터 전처리 ---
def split_bunji(bunji_str):
    if not isinstance(bunji_str, str):
        return 0, 0
    
    # 먼저 숫자와 하이픈(-)을 제외한 모든 문자를 제거
    cleaned_str = re.sub(r'[^0-9-]', '', bunji_str)
    
    if '-' in cleaned_str:
        parts = cleaned_str.split('-')
        bonbeon = parts[0]
        bubeon = parts[1] if len(parts) > 1 else 0
        return bonbeon, bubeon
    else:
        return cleaned_str, 0

auction_df[['본번', '부번']] = auction_df['번지'].apply(lambda x: pd.Series(split_bunji(x)))

# 본번, 부번을 숫자형으로 변환 (오류 발생 시 0으로 처리)
auction_df['본번'] = pd.to_numeric(auction_df['본번'], errors='coerce').fillna(0).astype(int)
auction_df['부번'] = pd.to_numeric(auction_df['부번'], errors='coerce').fillna(0).astype(int)
print("2단계 완료: '번지'를 '본번'과 '부번'으로 분리했습니다.")


# --- 6. 법정동 코드 매핑 ---
print("\n3단계: 법정동 코드 매핑을 시작합니다...")
code_df_active = code_df[code_df['폐지여부'] == '존재'][['법정동명', '법정동코드']]
processed_df = pd.merge(auction_df, code_df_active, left_on='시군구', right_on='법정동명', how='left')
if '법정동명' in processed_df.columns:
    processed_df.drop(columns=['법정동명'], inplace=True)
print("법정동 코드 매핑 완료.")

# --- 7. 건축년도 매핑 ---
print("\n4단계: 건축년도 매핑을 시작합니다...")
# sales.xlsx에서 조회용 데이터 준비 (중복 제거)
sales_lookup = sales_df[['시군구', '번지', '건축년도']].copy()
sales_lookup.dropna(inplace=True)
sales_lookup['번지'] = sales_lookup['번지'].astype(str) # merge를 위해 타입을 문자열로 통일
sales_lookup.drop_duplicates(subset=['시군구', '번지'], inplace=True)

# processed_df의 번지 타입도 문자열로 통일
processed_df['번지'] = processed_df['번지'].astype(str)

# 데이터 합치기
final_df = pd.merge(processed_df, sales_lookup, on=['시군구', '번지'], how='left')

failed_count = final_df['건축년도'].isnull().sum()
print(f"건축년도 매핑에 실패한 데이터 수: {failed_count}")

if '법정동명' in final_df.columns:
    final_df.drop(columns=['법정동명'], inplace=True)
print("법정동 코드 매핑 완료.")

# --- 추가 단계: 층 정보 추출 ---
def extract_floor(location_str):
    if not isinstance(location_str, str):
        return 0
    # '숫자+호' 패턴을 모두 찾음
    found_numbers = re.findall(r'(\d+)호', location_str)
    
    if not found_numbers:
        return 0 # 층 정보가 없으면 0으로 처리
    
    # 가장 마지막에 나온 번호를 실제 호수로 간주
    last_number_str = found_numbers[-1]
    
    try:
        number = int(last_number_str)
        # 3자리 이상일 경우 (층+호수 형태일 가능성 높음)
        if number >= 100:
            return number // 100
        else: # 1~2자리 숫자는 층 정보로 보기 어려움
            return 0
    except ValueError:
        return 0

print("\n층 정보 추출을 시작합니다...")
final_df['floor'] = final_df['location'].apply(extract_floor)
print("층 정보 추출 완료: 'floor' 컬럼이 추가되었습니다.")

# --- 8. 최종 결과 저장 및 출력 ---
final_df.to_csv(output_final_file, index=False, encoding='utf-8-sig')
print(f"\n모든 작업 완료: 최종 파일을 '{output_final_file}'로 저장했습니다.")

print("\n--- 최종 데이터 샘플 ---")
print(final_df[['시군구', '번지', '본번', '부번', '법정동코드', '건축년도']].head().to_string())