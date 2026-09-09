import datetime
import pandas as pd
import requests
import streamlit as st
import pytz

# -----------------------------------------------------------------------------
# 1. Page Configuration & Layout Settings
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="어제 박스오피스 Top 10",
    page_icon="🎬",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. Date Calculation (KST Standard)
# Streamlit Cloud servers may not use KST, so explicit timezone handling is used.
# -----------------------------------------------------------------------------
tz_kst = pytz.timezone("Asia/Seoul")
now_kst = datetime.datetime.now(tz_kst)
yesterday_kst = now_kst - datetime.timedelta(days=1)
target_date_str = yesterday_kst.strftime("%Y%m%d")
display_date_str = yesterday_kst.strftime("%Y년 %m월 %d일")

# -----------------------------------------------------------------------------
# 3. Data Fetching Function (Cached for 1 Hour)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_daily_boxoffice(api_key: str, target_dt: str):
    """
    Fetches daily box office data from the KOBIS API and performs validation.
    """
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {
        "key": api_key,
        "targetDt": target_dt
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Validate faultInfo structure in response
        if "faultInfo" in data:
            message = data["faultInfo"].get("message", "알 수 없는 API 오류가 발생했습니다.")
            return None, f"KOBIS API 오류: {message}"
            
        # Extract movie list
        boxoffice_result = data.get("boxOfficeResult", {})
        daily_list = boxoffice_result.get("dailyBoxOfficeList", [])
        
        if not daily_list:
            return None, "해당 날짜의 데이터가 비어 있습니다."
            
        return daily_list, None
        
    except requests.exceptions.RequestException as e:
        return None, f"네트워크 통신 오류가 발생했습니다: {e}"
    except Exception as e:
        return None, f"데이터 처리 중 오류가 발생했습니다: {e}"

# -----------------------------------------------------------------------------
# 4. Main Application Interface
# -----------------------------------------------------------------------------
st.title("🎬 어제의 박스오피스 순위")
st.caption(f"기준일자: {display_date_str} (한국 표준시 기준)")

# Retrieve API Key from Streamlit Secrets
api_key = st.secrets.get("KOBIS_KEY")

# Secret key presence validation
if not api_key:
    st.error("🔑 API 인증키(KOBIS_KEY)를 찾을 수 없습니다.")
    st.info(
        "**확인 사항:**\n"
        "1. Streamlit Cloud 설정의 `Secrets` 항목에 `KOBIS_KEY = '발급받은_키'` 형태로 등록되어 있는지 확인하세요.\n"
        "2. 로컬 실행 시 `.streamlit/secrets.toml` 파일에 키가 설정되어 있는지 확인하세요."
    )
    st.stop()

# Fetch data using cached function
with st.spinner("박스오피스 데이터를 불러오는 중입니다..."):
    raw_data, error_msg = fetch_daily_boxoffice(api_key, target_date_str)

# Error handling display
if error_msg:
    st.error(f"🚨 데이터를 불러오지 못했습니다: {error_msg}")
    st.info(
        "**확인 사항:**\n"
        "1. KOBIS_KEY가 올바르게 입력되었는지 확인해 주세요.\n"
        "2. KOBIS API 서버 상태 및 일일 요청 한도를 초과하지 않았는지 확인해 주세요.\n"
        "3. 조회 대상 날짜의 데이터 집계가 완료되었는지 확인해 주세요."
    )
    st.stop()

# -----------------------------------------------------------------------------
# 5. Data Processing & Parsing
# -----------------------------------------------------------------------------
df = pd.DataFrame(raw_data)

# Extract and convert fields to correct data types
df["rank"] = df["rank"].astype(int)
df["movieNm"] = df["movieNm"].astype(str)
df["openDt"] = df["openDt"].astype(str)
df["audiCnt"] = df["audiCnt"].astype(int)
df["audiAcc"] = df["audiAcc"].astype(int)
df["scrnCnt"] = df["scrnCnt"].astype(int)

# Sort by rank
df = df.sort_values(by="rank", ascending=True).reset_index(drop=True)

# -----------------------------------------------------------------------------
# 6. Display Top 1 Movie Highlights (Metrics)
# -----------------------------------------------------------------------------
top_movie = df.iloc[0]

st.markdown(f"### 🏆 1위: {top_movie['movieNm']}")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="어제 관객수",
        value=f"{top_movie['audiCnt']:,} 명"
    )
with col2:
    st.metric(
        label="누적 관객수",
        value=f"{top_movie['audiAcc']:,} 명"
    )
with col3:
    st.metric(
        label="상영 스크린수",
        value=f"{top_movie['scrnCnt']:,} 개"
    )

st.divider()

# -----------------------------------------------------------------------------
# 7. Display Chart (Top 5 Movies Audience)
# -----------------------------------------------------------------------------
st.subheader("📊 관객수 상위 5개 영화")

top_5_df = df.head(5).copy()
st.bar_chart(
    data=top_5_df,
    x="movieNm",
    y="audiCnt",
    x_label="영화명",
    y_label="어제 관객수 (명)"
)

st.divider()

# -----------------------------------------------------------------------------
# 8. Display Data Table
# -----------------------------------------------------------------------------
st.subheader("📋 전체 순위 (Top 10)")

# Format display dataframe with clear column names
display_df = df[["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]].copy()
display_df.columns = ["순위", "영화명", "개봉일", "어제 관객수", "누적 관객수", "스크린수"]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "순위": st.column_config.NumberColumn(format="%d"),
        "어제 관객수": st.column_config.NumberColumn(format="%d 명"),
        "누적 관객수": st.column_config.NumberColumn(format="%d 명"),
        "스크린수": st.column_config.NumberColumn(format="%d 개")
    }
)
