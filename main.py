import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
# [그래프 3] 조건 만족 영화 누적관객수 비교 (다중 선그래프)
# --------------------------------------------------
st.header("🏆 장기 흥행 Top 5 영화 누적관객수 비교")

# 1. 영화별 차트(TOP10) 등장 일수 카운트
movie_counts = df["영화명"].value_counts()

# 2. 등장 일수가 20일 이상인 영화 목록 필터링
movies_over_20days = movie_counts[movie_counts >= 20].index

# 3. 조건(20일 이상)을 만족하는 데이터만 1차 필터링
df_over_20days = df[df["영화명"].isin(movies_over_20days)]

# 4. 필터링된 영화들 중 최고 누적관객수 기준으로 상위 5개 영화명 추출
top5_long_run_movies = (
    df_over_20days.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .head(5)
    .index.tolist()
)

# 5. 상위 5개 영화의 전체 데이터 추출
top5_long_run_df = df[df["영화명"].isin(top5_long_run_movies)]

# 6. Plotly 다중 선그래프 생성
fig3 = px.line(
    top5_long_run_df,
    x="기준일자",
    y="누적관객수",
    color="영화명",  # 영화별로 색상 구분 및 범례 생성
    title="TOP10 20일 이상 진입 영화 중 누적관객수 상위 5개 영화 추이 비교",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)", "영화명": "영화 제목"},
)

st.plotly_chart(fig3, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 박스오피스 상위권에 20일 이상 장기 집권한 흥행작들의 누적관객수 증가 추이와 장기 흥행 동력을 한눈에 비교할 수 있습니다."
)

st.divider()  # 구역 구분을 위한 구분선

# --------------------------------------------------
# [그래프 4] 전체 TOP10 일별 관객수 합계 및 7일 이동평균 (이동평균선 차트)
# --------------------------------------------------
st.header("📉 전체 박스오피스 일일 관객수 합계 및 7일 이동평균")

# 1. 기준일자별 TOP10 전체 영화의 해당일관객수 합계 계산
daily_total_df = (
    df.groupby("기준일자")["해당일관객수"].sum().reset_index()
)

# 2. 7일 이동평균 계산
daily_total_df["7일이동평균"] = (
    daily_total_df["해당일관객수"].rolling(window=7).mean()
)

# 3. Plotly Graph Objects를 이용한 차트 생성
fig4 = go.Figure()

fig4.add_trace(
    go.Scatter(
        x=daily_total_df["기준일자"],
        y=daily_total_df["해당일관객수"],
        mode="lines",
        name="일일 관객수 합계",
        line=dict(color="rgba(150, 150, 150, 0.4)", width=1.5),
    )
)

fig4.add_trace(
    go.Scatter(
        x=daily_total_df["기준일자"],
        y=daily_total_df["7일이동평균"],
        mode="lines",
        name="7일 이동평균",
        line=dict(color="#FF4B4B", width=3),
    )
)

fig4.update_layout(
    title="전체 박스오피스 관객수 추이 및 7일 이동평균선",
    xaxis_title="날짜",
    yaxis_title="관객수(명)",
    legend_title="구분",
    hovermode="x unified",
)

st.plotly_chart(fig4, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 주말과 평일의 심한 일별 관객수 변동성(노이즈)을 제거하여, 전체 극장가 관객 시장의 전반적인 흐름과 계절적 성수기/비성수기 추세를 명확하게 파악할 수 있습니다."
)

st.divider()  # 구역 구분을 위한 구분선

# --------------------------------------------------
# [그래프 5] 월별 전체 관객수 합계 (막대그래프)
# --------------------------------------------------
st.header("🗓️ 월별 전체 관객수 합계")

# 1. 기준일자에서 연-월(YYYY-MM) 문자열 추출
daily_total_df["연월"] = daily_total_df["기준일자"].dt.strftime("%Y-%m")

# 2. 월 단위로 묶어서 해당일관객수 합산
monthly_total_df = (
    daily_total_df.groupby("연월")["해당일관객수"].sum().reset_index()
)

# 3. Plotly 막대그래프 생성
fig5 = px.bar(
    monthly_total_df,
    x="연월",
    y="해당일관객수",
    title="월별 극장가 총 관객수 비교",
    labels={"연월": "연-월", "해당일관객수": "총 관객수(명)"},
    text_auto=".2s",  # 막대 위에 축약된 숫자로 관객수 표시 (예: 1.2M)
)

fig5.update_traces(textposition="outside")

st.plotly_chart(fig5, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 월별 총 관객 수 규모를 비교하여 영화 시장의 월별 성수기(여름 방학, 명절 등)와 비성수기를 한눈에 직관적으로 파악할 수 있습니다."
)

st.divider()  # 구역 구분을 위한 구분선

# --------------------------------------------------
# [그래프 6] 요일별 x 연월 관객수 캘린더 히트맵
# --------------------------------------------------
st.header("🗓️ 요일 및 월별 관객 분포 (캘린더 히트맵)")

# 1. 날짜 데이터에서 요일명, 요일 번호, 연월, 날짜 문자열(YYYY-MM-DD) 추출
heatmap_df = daily_total_df.copy()
heatmap_df["요일명"] = heatmap_df["기준일자"].dt.day_name()
heatmap_df["요일번호"] = heatmap_df["기준일자"].dt.dayofweek  # 월:0 ~ 일:6
heatmap_df["날짜문자열"] = heatmap_df["기준일자"].dt.strftime("%Y-%m-%d")

# 2. 요일 순서를 월요일부터 일요일로 지정하기 위한 설정
days_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
days_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

# 3. pivot_table을 활용해 히트맵 행(요일), 열(연월) 형태로 데이터 구조 변환
# z축(값): 해당일관객수, customdata: 마우스 호버용 yyyy-mm-dd 날짜
z_matrix = heatmap_df.pivot_table(
    index="요일명", columns="연월", values="해당일관객수", aggfunc="sum"
).reindex(days_order)

date_matrix = heatmap_df.pivot_table(
    index="요일명", columns="연월", values="날짜문자열", aggfunc="first"
).reindex(days_order)

# 4. Plotly Heatmap 생성
fig6 = go.Figure(
    data=go.Heatmap(
        z=z_matrix.values,
        x=z_matrix.columns,
        y=days_kr,  # Y축 레이블을 한글 요일로 표시
        customdata=date_matrix.values,  # 마우스 올렸을 때 보여줄 데이터 설정
        hovertemplate="<b>날짜: %{customdata}</b><br>요일: %{y}<br>관객수: %{z:,.0f}명<extra></extra>",
        colorscale="Reds",  # 관객수가 많을수록 진한 빨간색
    )
)

fig6.update_layout(
    title="월별/요일별 박스오피스 관객수 히트맵",
    xaxis_title="연-월",
    yaxis_title="요일",
)

st.plotly_chart(fig6, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 각 월별로 어떤 요일에 관객 집중도가 높았는지 파악할 수 있으며, 주말 및 공휴일 영향에 따른 관객 몰림 현상을 한눈에 비교할 수 있습니다."
)
