# IFRS-9 기반 P2P 부동산 담보투자 기대손실(ECL) 산출 대시보드

IFRS-9 기대신용손실(Expected Credit Loss) 프레임워크를 적용하여 P2P 부동산 담보투자의 리스크를 정량적으로 분석하고 시각화하는 웹 솔루션입니다.

<<그림1>>
-> 실행화면 그림 추가

## 📖 프로젝트 개요 (Overview)

본 프로젝트는 기존 P2P 금융 시장의 정보 비대칭 문제를 해결하고, 투자자 관점에서 객관적인 리스크 평가를 돕기 위해 개발되었습니다. 국제회계기준(IFRS 9)을 준용하여 차입자의 부도확률(PD)과 담보물의 손실률(LGD)을 머신러닝 및 통계적 기법으로 추정하고, 최종적인 기대손실(ECL)을 산출합니다.

## 🚀 주요 기능 (Key Features)

### 1. 부도확률 (PD: Probability of Default) 예측

차입자의 인적, 재무 정보를 바탕으로 머신러닝 모델을 통해 부도 가능성을 예측합니다.

다양한 신용 평가 지표를 학습하여 개인별 맞춤형 PD를 산출합니다.

### 2. 부도 시 손실률 (LGD: Loss Given Default) 추정

부동산 매매가 예측: 아파트, 지역 정보를 활용하여 매매 시 예상 회수액을 추정합니다.

부동산 경매 낙찰가 예측: 감정가, 지역 정보를 활용하여 경매 시 예상 회수액을 추정합니다.

시나리오 분석: 임의매각 및 경매 등 다양한 회수 시나리오를 가정하여 선순위 채권액을 고려한 최종 손실률을 계산합니다.

### 3. 기대손실 (ECL) 산출 및 대시보드

ECL 공식 적용: ECL = PD × LGD × EAD

웹 대시보드: 사용자가 투자 금액, 차입자 정보, 담보 정보를 입력하면 즉시 리스크 지표를 확인할 수 있는 인터페이스를 제공합니다.

<<그림2>>
-> 산출되는 보고서 그림 추가

## 💻 설치 및 실행 (Installation & Usage)
```
# Repository clone
git clone [https://github.com/username/project-name.git](https://github.com/username/project-name.git)

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

## 📂 프로젝트 구조 (Project Structure)
```
├── data/                  # 데이터셋 폴더
├── models/                # 학습된 모델 파일 (pkl 등)
├── src/                   # 소스 코드
│   ├── data_processing.py # 전처리 로직
│   ├── calc_pd.py         # PD 산출 모듈
│   └── calc_lgd.py        # LGD 산출 모듈
├── app.py                 # 대시보드 실행 파일
├── requirements.txt       # 필요 라이브러리 목록
└── README.md              # 프로젝트 설명
```

## 👥 팀원 (Contributors)

 - 박윤찬(팀장) : 부도확률 예측 모델 개발 및 대시보드 프론트 엔드 개발

 - 어승윤(팀원) : 부동산 경매 시 낙찰가 예측 모델 개발 및 대시보드 백엔드 개발

 - 조현재(팀원) : 부동산 매각 시 매각가 예측 모델 개발 및 대시보드 백엔드 개발

## 🛠️ 사용 기술 (Tech Stack)

Data Analysis: Python, Pandas, NumPy

Machine Learning: Scikit-learn (Regression & Classification models)

Visualization & Web: (예: Streamlit, Flask, Django 등 사용한 프레임워크 기재)
-> 여기도 수정해야함

## 📝 License

This project is licensed under the MIT License.
