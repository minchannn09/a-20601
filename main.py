import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 그래프 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

# 앱 제목 설정
st.title("🎬 영화 데이터 그래프 - 분포와 관계")
st.markdown("---")

# 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # genre: 세로막대 기호(|)로 여러 개 적힌 영화는 첫 번째 장르만 추출
    df['genre_first'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0].strip())
    
    # openDt 날짜 형식 변환
    df['openDt'] = pd.to_datetime(df['openDt'].astype(str), format='%Y%m%d', errors='coerce')
    
    return df

try:
    df = load_data()
    
    # 데이터 미리보기 토글 섹션
    with st.expander("📊 데이터셋 살펴보기 (216편 영화 데이터)"):
        st.dataframe(df.head(), use_container_width=True)
        st.caption(f"총 {len(df)}개 데이터가 성공적으로 로드되었습니다.")

    # -------------------------------------------------------------
    # 1. 장르별 영화 편수 분포 (도넛 그래프)
    # -------------------------------------------------------------
    st.markdown("## 1. 장르별 영화 편수 분포")
    
    # 장르별 편수 집계
    genre_counts = df['genre_first'].value_counts().reset_index()
    genre_counts.columns = ['장르', '편수']
    
    # Plotly 도넛 그래프 생성
    fig1 = px.pie(
        genre_counts,
        values='편수',
        names='장르',
        hole=0.4,
        title="장르별 영화 편수 비율",
        hover_data=['편수']
    )
    
    # 호버(마우스 올림) 시 편수와 비율 표기
    fig1.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate="<b>장르: %{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>"
    )
    
    fig1.update_layout(
        margin=dict(t=50, b=20, l=20, r=20),
        legend_title_text="장르"
    )
    
    # 그래프 출력
    st.plotly_chart(fig1, use_container_width=True)
    
    # 하단 구역: 이 그래프로 알 수 있는 것
    st.info("💡 **이 그래프로 알 수 있는 것:** 최근 1년간 박스오피스 Top 10에 오른 영화 중 어떤 장르가 가장 큰 비중을 차지하는지, 시장을 주도하는 주요 장르 분포와 다양성을 한눈에 파악할 수 있습니다.")

    st.markdown("---")

    # -------------------------------------------------------------
    # 2. 장르 및 영화별 총 관객수 (트리맵 그래프)
    # -------------------------------------------------------------
    st.markdown("## 2. 장르별 영화 및 총 관객수 분포 (트리맵)")
    
    # Plotly 트리맵 그래프 생성
    fig2 = px.treemap(
        df,
        path=[px.Constant("전체 영화"), 'genre_first', 'movieNm'],
        values='total_audi',
        title="장르 및 영화별 총 관객수 트리맵 (칸 크기 = 총 관객수)",
        hover_data={'total_audi': ':,d'}
    )
    
    # 호버(마우스 올림) 시 영화명과 총 관객수가 보이도록 설정
    fig2.update_traces(
        hovertemplate="<b>%{label}</b><br>총 관객수: %{value:,}명<extra></extra>"
    )
    
    fig2.update_layout(
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    # 그래프 출력
    st.plotly_chart(fig2, use_container_width=True)
    
    # 하단 구역: 이 그래프로 알 수 있는 것
    st.info("💡 **이 그래프로 알 수 있는 것:** 각 장르 내에서 어떤 영화가 흥행을 주도(관객수 차지)했는지와 장르 전체의 관객 동원력을 시각적으로 비교해 파악할 수 있습니다.")

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
