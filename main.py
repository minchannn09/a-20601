import streamlit as st
st.title("나의 데이터 과학 포트폴리오")
st.write("반갑습니다! 이제부터 여기에 제 작업을 기록합니다.")
st.write("강민찬")
import datetime
import requests
import pandas as pd
import pytz
import streamlit as st

# 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(
    page_title="어제 박스오피스 순위",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 어제 일별 박스오피스")


# ----------------------------------------------------
# 1. API 데이터 불러오기 함수 (캐시 적용)
# ----------------------------------------------------
# ttl=3600: 같은 날짜 데이터는 1시간(3600초) 동안 API를 다시 부르지 않고 저장된 값을 사용합니다.
@st.cache_data(ttl=3600)
def fetch_box_office_data(target_date: str, api_key: str):
    """KOBIS API를 호출하여 해당 날짜의 박스오피스 데이터를 가져오는 함수"""
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {
        "key": api_key,
        "targetDt": target_date
    }
    
    # API 요청 실행
    response = requests.get(url, timeout=10)
    
    # HTTP 상태 코드가 200(성공)이 아닌 경우 예외 발생
    response.raise_for_status()
    
    return response.json()


# ----------------------------------------------------
# 2. 날짜 및 인증키 준비
# ----------------------------------------------------
# 한국 표준시(KST) 기준 어제 날짜 구하기
kst = pytz.timezone("Asia/Seoul")
now_kst = datetime.datetime.now(kst)
yesterday = now_kst - datetime.timedelta(days=1)
target_dt_str = yesterday.strftime("%Y%m%d")
display_date_str = yesterday.strftime("%Y년 %m월 %d일")

st.caption(f"기준 날짜: **{display_date_str}** (한국 시간 기준)")

# Streamlit Secrets에서 API 키 불러오기
try:
    api_key = st.secrets["KOBIS_KEY"]
except Exception:
    st.error("🔑 API 키를 찾을 수 없습니다.")
    st.info(
        "**확인 조치 방법:**\n"
        "1. Streamlit Cloud의 앱 설정에서 **Secrets** 메뉴로 이동하세요.\n"
        "2. `KOBIS_KEY = \"발급받은_인증키\"` 형태로 비밀키를 입력했는지 확인해 주세요."
    )
    st.stop()


# ----------------------------------------------------
# 3. 데이터 수집 및 예외 처리
# ----------------------------------------------------
try:
    data = fetch_box_office_data(target_dt_str, api_key)
except Exception as e:
    st.error(f"🌐 API 요청 중 네트워크 오류가 발생했습니다: {e}")
    st.info("**확인 조치 방법:**\n- 인터넷 연결 상태를 확인해 주세요.\n- KOBIS 서버가 일시적인 점검 중일 수 있으니 잠시 후 다시 시도해 주세요.")
    st.stop()

# KOBIS API 특이사항: 인증키 오류 시 status_code는 200이지만 'faultInfo' 응답이 옴
if "faultInfo" in data:
    fault_msg = data["faultInfo"].get("message", "알 수 없는 오류")
    st.error(f"⚠️ KOBIS API 오류 발생: {fault_msg}")
    st.info(
        "**확인 조치 방법:**\n"
        "1. 등록된 `KOBIS_KEY`가 올바른지 확인해 주세요.\n"
        "2. 영화진흥위원회 오픈API 웹사이트에서 키가 유효한 상태인지 확인해 주세요."
    )
    st.stop()

# 응답 데이터 검증
box_office_result = data.get("boxOfficeResult", {})
movie_list = box_office_result.get("dailyBoxOfficeList", [])

if not movie_list:
    st.warning("⚠️ 조회된 박스오피스 영화 목록이 비어 있습니다.")
    st.info(
        "**확인 조치 방법:**\n"
        "- 해당 날짜의 집계 데이터가 아직 업데이트되지 않았을 수 있습니다.\n"
        "- KOBIS 홈페이지에서 해당 날짜 데이터가 존재하는지 확인해 주세요."
    )
    st.stop()


# ----------------------------------------------------
# 4. 데이터 전처리 (문자열 -> 숫자 변환)
# ----------------------------------------------------
df = pd.DataFrame(movie_list)

# 숫자로 변환할 컬럼 지정
numeric_columns = ["rank", "audiCnt", "audiAcc", "scrnCnt"]
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 순위(rank) 기준 오름차순 정렬
df = df.sort_values("rank").reset_index(drop=True)


# ----------------------------------------------------
# 5. 화면 출력: 1위 영화 지표 카드 (Metrics)
# ----------------------------------------------------
top_movie = df.iloc[0]

st.subheader(f"🥇 1위 영화: {top_movie['movieNm']}")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="일별 관객수",
        value=f"{top_movie['audiCnt']:,} 명"
    )
with col2:
    st.metric(
        label="누적 관객수",
        value=f"{top_movie['audiAcc']:,} 명"
    )
with col3:
    st.metric(
        label="스크린수",
        value=f"{top_movie['scrnCnt']:,} 개"
    )

st.divider()


# ----------------------------------------------------
# 6. 화면 출력: 상위 5개 영화 관객수 막대그래프
# ----------------------------------------------------
st.subheader("📊 관객수 TOP 5")

top5_df = df.head(5)

# Streamlit 기본 막대그래프 생성
st.bar_chart(
    data=top5_df,
    x="movieNm",
    y="audiCnt",
    x_label="영화명",
    y_label="일별 관객수(명)"
)

st.divider()


# ----------------------------------------------------
# 7. 화면 출력: 전체 순위 표 (Table)
# ----------------------------------------------------
st.subheader("📋 전체 박스오피스 순위")

# 표에 보여줄 컬럼 선택 및 이름을 한글로 변경
table_df = df[["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]].copy()
table_df.columns = ["순위", "영화명", "개봉일", "관객수", "누적관객", "스크린수"]

# 천 단위 쉼표(,) 포맷팅 적용하여 출력
st.dataframe(
    table_df.style.format({
        "관객수": "{:,}",
        "누적관객": "{:,}",
        "스크린수": "{:,}"
    }),
    use_container_width=True,
    hide_index=True
)
