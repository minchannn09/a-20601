import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="박스오피스 데이터 분석", layout="wide")

st.title("🎬 영화 박스오피스 데이터 분석 웹앱")


# [1. 데이터 불러오기] - 캐싱 적용
# @st.cache_data를 사용해 데이터를 한 번만 불러오고 매번 다시 로드하지 않도록 설정합니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    data = pd.read_csv(url)

    # [2. 날짜 및 데이터 전처리]
    # 결측치가 포함된 행 삭제
    data = data.dropna()

    # '기준일자' 컬럼을 datetime 형식으로 변환 (yyyy-mm-dd)
    data["기준일자"] = pd.to_datetime(data["기준일자"])

    # 전체 데이터를 기준일자 순서대로 정렬
    data = data.sort_values(by="기준일자")

    return data


# 데이터 로드
df = load_data()

# [3. 영화 선택 기능]
# 사이드바에 영화 선택 옵션 배치
st.sidebar.header("🔍 영화 선택")

# 중복 없는 영화 목록 생성 및 누적관객수 내림차순 정렬
# 각 영화별 최대 누적관객수를 구해 내림차순으로 정렬합니다.
movie_list = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

# 사용자로부터 영화 선택받기 (기본값: 관객수가 가장 높은 첫 번째 영화)
selected_movie = st.sidebar.selectbox("영화 이름을 선택하세요:", movie_list)

# 선택된 영화의 데이터만 필터링
filtered_df = df[df["영화명"] == selected_movie]

# [5. 기타] 구역 나누기 (메인 섹션 1)
st.header(f"📊 '{selected_movie}' 관객수 추이")

# [4. 선그래프 그리기]
# Plotly를 이용한 기준일자별 해당일관객수 선 그래프 작성
fig = px.line(
    filtered_df,
    x="기준일자",
    y="해당일관객수",
    title=f"'{selected_movie}'의 일별 관객수 변화",
    labels={"기준일자": "날짜", "해당일관객수": "일일 관객수(명)"},
    markers=True,  # 데이터 지점에 점 표시
)

# 그래프 화면에 출력
st.plotly_chart(fig, use_container_width=True)

# 그래프 아래 설명 문구 자리
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 개봉 후 일자별 관객수 증감 추이와 흥행 피크 시점을 확인할 수 있습니다."
)

st.divider()  # 구역 구분을 위한 구분선

# [5. 기타] 추후 그래프를 추가할 수 있는 구역 예시 (메인 섹션 2)
st.header("📈 추가 분석 구역 (예정)")
st.caption("이곳에 추후 다른 시각화 그래프나 분석 결과를 추가할 수 있습니다.")

# 설명 문구 자리 예시
st.info("💡 **이 그래프로 알 수 있는 것:** (추후 추가될 분석에 대한 설명 입력)")
