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

    st.markdown("---")

    # -------------------------------------------------------------
    # 3. 총 관객수 분포 (히스토그램)
    # -------------------------------------------------------------
    st.markdown("## 3. 총 관객수(total_audi) 분포")
    
    # 관객수가 가장 많은 영화 계산
    max_movie = df.loc[df['total_audi'].idxmax()]
    max_title = max_movie['movieNm']
    max_audi = max_movie['total_audi']
    
    # Plotly 히스토그램 그래프 생성
    fig3 = px.histogram(
        df,
        x='total_audi',
        nbins=30,
        title="영화별 총 관객수 분포 히스토그램",
        labels={'total_audi': '총 관객수(명)', 'count': '영화 수'},
        hover_data=['movieNm']
    )
    
    fig3.update_layout(
        xaxis_title="총 관객수 (명)",
        yaxis_title="영화 수 (편)",
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    # 그래프 출력
    st.plotly_chart(fig3, use_container_width=True)
    
    # 하단 구역: 이 그래프로 알 수 있는 것
    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** 대부분의 영화는 관객수 하위 구간(약 100만 명 미만 구간)에 집중되어 분포하고 있으며, "
        f"가장 관객이 많은 영화는 **'{max_title}'** (총 {max_audi:,}명)으로 극소수의 흥행 대작이 전체 관객수 분포의 오른쪽 긴 꼬리를 형성함을 보여줍니다."
    )

    st.markdown("---")

    # -------------------------------------------------------------
    # 4. 개봉일 스크린수와 총 관객수의 관계 (산점도)
    # -------------------------------------------------------------
    st.markdown("## 4. 개봉일 스크린수와 총 관객수의 관계 (산점도)")
    
    # Plotly 산점도 그래프 생성
    fig4 = px.scatter(
        df,
        x='first_scrn',
        y='total_audi',
        color='genre_first',
        hover_name='movieNm',
        title="개봉일 스크린수(first_scrn) vs 총 관객수(total_audi)",
        labels={
            'first_scrn': '개봉일 스크린수 (개)',
            'total_audi': '총 관객수 (명)',
            'genre_first': '장르'
        },
        hover_data={
            'first_scrn': ':,d',
            'total_audi': ':,d',
            'genre_first': False
        }
    )
    
    # 호버(마우스 올림) 시 영화명, 스크린수, 총 관객수 표기
    fig4.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,}개<br>총 관객수: %{y:,}명<extra></extra>"
    )
    
    fig4.update_layout(
        xaxis_title="개봉일 스크린수 (개)",
        yaxis_title="총 관객수 (명)",
        margin=dict(t=50, b=20, l=20, r=20),
        legend_title_text="장르"
    )
    
    # 그래프 출력
    st.plotly_chart(fig4, use_container_width=True)
    
    # 하단 구역: 이 그래프로 알 수 있는 것
    st.info("💡 **이 그래프로 알 수 있는 것:** 개봉일 스크린수가 많을수록 총 관객수도 증가하는 비례 경향(양의 상관관계)을 보이며, 장르별 선호 스크린 확보 규모와 관객 수 선점 차이를 확인할 수 있습니다.")

    st.markdown("---")

    # -------------------------------------------------------------
    # 5. 주요 장르별 총 관객수 박스플롯 (상자 그림)
    # -------------------------------------------------------------
    st.markdown("## 5. 영화 10편 이상 주요 장르별 총 관객수 분포 (박스플롯)")
    
    # 영화 편수가 10편 이상인 장르 필터링
    genre_counts_series = df['genre_first'].value_counts()
    major_genres = genre_counts_series[genre_counts_series >= 10].index.tolist()
    df_major = df[df['genre_first'].isin(major_genres)]
    
    # Plotly 박스플롯 그래프 생성
    fig5 = px.box(
        df_major,
        x='genre_first',
        y='total_audi',
        color='genre_first',
        hover_name='movieNm',
        points='outliers',  # 상자 밖의 아웃라이어 점 표시
        title="주요 장르별(10편 이상) 총 관객수 분포 (이상치 관측)",
        labels={
            'genre_first': '장르',
            'total_audi': '총 관객수 (명)'
        },
        hover_data={
            'total_audi': ':,d',
            'genre_first': False
        }
    )
    
    fig5.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>총 관객수: %{y:,}명<extra></extra>"
    )
    
    fig5.update_layout(
        xaxis_title="장르",
        yaxis_title="총 관객수 (명)",
        margin=dict(t=50, b=20, l=20, r=20),
        legend_title_text="장르"
    )
    
    # 그래프 출력
    st.plotly_chart(fig5, use_container_width=True)
    
    # 하단 구역: 이 그래프로 알 수 있는 것
    st.info(f"💡 **이 그래프로 알 수 있는 것:** 영화 편수가 10편 이상인 주요 장르({', '.join(major_genres)})의 관객수 중간값과 편차를 비교할 수 있으며, 상자 밖으로 튀어나온 이상치(outlier) 점들을 통해 해당 장르에서 압도적인 흥행 성과를 거둔 대표 대작들을 쉽게 식별할 수 있습니다.")

    st.markdown("---")

    # -------------------------------------------------------------
    # 6. 개봉일 스크린수, 총 관객수 및 첫 주 관객수의 관계 (버블 차트)
    # -------------------------------------------------------------
    st.markdown("## 6. 스크린수 · 총 관객수 · 첫 주 관객수 버블 차트")
    
    # Plotly 버블 차트 생성
    fig6 = px.scatter(
        df,
        x='first_scrn',
        y='total_audi',
        size='first_week_audi',
        color='genre_first',
        hover_name='movieNm',
        size_max=45,
        title="스크린수(x) vs 총 관객수(y) vs 첫 주 관객수(버블 크기)",
        labels={
            'first_scrn': '개봉일 스크린수 (개)',
            'total_audi': '총 관객수 (명)',
            'first_week_audi': '첫 주 관객수 (명)',
            'genre_first': '장르'
        },
        hover_data={
            'first_scrn': ':,d',
            'total_audi': ':,d',
            'first_week_audi': ':,d',
            'genre_first': False
        }
    )
    
    fig6.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,}개<br>총 관객수: %{y:,}명<br>첫 주 관객수: %{marker.size:,}명<extra></extra>"
    )
    
    fig6.update_layout(
        xaxis_title="개봉일 스크린수 (개)",
        yaxis_title="총 관객수 (명)",
        margin=dict(t=50, b=20, l=20, r=20),
        legend_title_text="장르"
    )
    
    # 그래프 출력
    st.plotly_chart(fig6, use_container_width=True)
    
    # 하단 구역: 이 그래프로 알 수 있는 것
    st.info("💡 **이 그래프로 알 수 있는 것:** 개봉일 스크린수와 총 관객수의 상관관계에 더해 버블 크기(첫 주 관객수)를 통해 초반 흥행 집객력이 최종 총 관객수 동원에 결정적인 영향을 미치는지 3차원적인 상관성을 시각적으로 파악할 수 있습니다.")

    st.markdown("---")

    # -------------------------------------------------------------
    # 7. 제작 국가 및 장르별 영화 편수 선버스트 차트
    # -------------------------------------------------------------
    st.markdown("## 7. 제작 국가 및 장르별 영화 편수 선버스트")
    
    # Plotly 선버스트 그래프 생성 (path: nation -> genre_first)
    fig7 = px.sunburst(
        df,
        path=['nation', 'genre_first'],
        title="제작 국가 및 장르별 영화 편수 분포 (칸 크기 = 영화 편수)"
    )
    
    # 마우스 올림(호버) 시 정보 표기
    fig7.update_traces(
        hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<extra></extra>"
    )
    
    fig7.update_layout(
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    # 그래프 출력
    st.plotly_chart(fig7, use_container_width=True)
    
    # 하단 구역: 이 그래프로 알 수 있는 것
    st.info("💡 **이 그래프로 알 수 있는 것:** 영화를 제작한 각 국가(내부 링)에서 주력으로 제작하거나 개봉한 핵심 장르(외부 링)의 편수 비율과 계층 구조를 동심원 형태로 한눈에 파악할 수 있습니다.")

    st.markdown("---")

    # -------------------------------------------------------------
    # 8. 첫 주 관객수와 총 관객수의 상관관계 (산점도)
    # -------------------------------------------------------------
    st.markdown("## 8. 첫 주 관객수와 총 관객수의 관계 (산점도)")
    
    # Plotly 산점도 그래프 생성
    fig8 = px.scatter(
        df,
        x='first_week_audi',
        y='total_audi',
        hover_name='movieNm',
        title="첫 주 관객수(first_week_audi) vs 총 관객수(total_audi)",
        labels={
            'first_week_audi': '첫 주 관객수 (명)',
            'total_audi': '총 관객수 (명)'
        },
        hover_data={
            'first_week_audi': ':,d',
            'total_audi': ':,d'
        }
    )
    
    fig8.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>첫 주 관객수: %{x:,}명<br>총 관객수: %{y:,}명<extra></extra>"
    )
    
    fig8.update_layout(
        xaxis_title="첫 주 관객수 (명)",
        yaxis_title="총 관객수 (명)",
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    # 그래프 출력
    st.plotly_chart(fig8, use_container_width=True)
    
    # 하단 구역: 이 그래프로 알 수 있는 것
    st.info("💡 **이 그래프로 알 수 있는 것:** 개봉 첫 주 관객수가 많을수록 최종 총 관객수도 함께 증가하는 비례 경향(양의 상관관계)을 한눈에 확인할 수 있습니다.")

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
