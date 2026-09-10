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

# --------------------------------------------------
# [그래프 1] 해당일관객수 추이 (단일 선 그래프)
# --------------------------------------------------
st.header(f"📊 '{selected_movie}' 일일 관객수 추이")

fig1 = px.line(
    filtered_df,
    x="기준일자",
    y="해당일관객수",
    title=f"'{selected_movie}'의 일별 관객수 변화",
    labels={"기준일자": "날짜", "해당일관객수": "일일 관객수(명)"},
    markers=True,  # 데이터 지점에 점 표시
)

st.plotly_chart(fig1, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 개봉 후 일자별 관객수 증감 추이와 흥행 피크 시점(주말 폭증 등)을 확인할 수 있습니다."
)

st.divider()  # 구역 구분을 위한 구분선

# --------------------------------------------------
# [그래프 2] 누적관객수 변화 (영역 차트)
# --------------------------------------------------
st.header(f"📈 '{selected_movie}' 누적 관객수 성장 추이")

fig2 = px.area(
    filtered_df,
    x="기준일자",
    y="누적관객수",
    title=f"'{selected_movie}'의 누적 관객수 변화",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)"},
)

st.plotly_chart(fig2, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 시간이 지남에 따라 관객수가 총 얼마나 누적되었는지 곡선의 기울기를 통해 흥행 지속력을 한눈에 파악할 수 있습니다."
)

st.divider()  # 구역 구분을 위한 구분선

# --------------------------------------------------
# [그래프 3] Top 5 영화 누적관객수 비교 (다중 선그래프)
# --------------------------------------------------
st.header("🏆 누적관객수 Top 5 영화 성과 비교")

# 1. 누적관객수가 가장 높은 상위 5개 영화명 추출
top5_movies = movie_list[:5]

# 2. 전체 데이터에서 Top 5 영화의 데이터만 추출
top5_df = df[df["영화명"].isin(top5_movies)]

# 3. Plotly 다중 선그래프 생성 (color="영화명" 속성으로 영화별 다른 색상 및 범례 자동 적용)
fig3 = px.line(
    top5_df,
    x="기준일자",
    y="누적관객수",
    color="영화명",  # 영화명에 따라 선 색상을 다르게 설정하고 범례 표시
    title="상위 5개 영화의 기준일자별 누적관객수 추이 비교",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)", "영화명": "영화 제목"},
)

st.plotly_chart(fig3, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 가장 흥행한 상위 5개 영화의 관객수 증가 속도와 최종 누적관객수 규모를 한눈에 비교할 수 있습니다."
)
