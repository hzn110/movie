
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption("1년간 박스오피스 10위권에 든 영화 중 해당 기간에 개봉한 216편의 데이터를 이용합니다.")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    # 사용자가 지정한 분석용 열만 사용
    columns = [
        "movieCd", "movieNm", "openDt", "genre", "nation",
        "first_scrn", "first_show", "first_week_audi",
        "total_audi", "days_in_top10"
    ]
    df = df[columns].copy()

    # 장르가 여러 개면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    return df

try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.exception(e)
    st.stop()

# ---------------------------------------------------------
# 그래프 1. 장르별 영화 편수
# ---------------------------------------------------------
st.divider()
st.subheader("① 장르별 영화 편수")

genre_counts = (
    df["genre"]
    .value_counts()
    .rename_axis("장르")
    .reset_index(name="영화 편수")
)

fig = px.pie(
    genre_counts,
    names="장르",
    values="영화 편수",
    hole=0.55,
    title="장르별 영화 편수 분포",
)

fig.update_traces(
    textinfo="percent",
    hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<br>비율: %{percent}<extra></extra>",
)

fig.update_layout(
    height=550,
    margin=dict(t=70, b=30, l=20, r=20),
    legend_title_text="장르",
)

st.plotly_chart(fig, use_container_width=True)

st.info(
    "💡 이 그래프로 알 수 있는 것: "
    "장르별 영화 편수의 차이와 전체 영화에서 각 장르가 차지하는 비율을 비교할 수 있습니다."
)

st.divider()
st.caption(f"총 {len(df):,}편의 영화 데이터를 사용했습니다.")
