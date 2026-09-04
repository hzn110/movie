import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown(
    "1년간 박스오피스 10위권에 든 영화 가운데 해당 기간에 개봉한 "
    "**216편**의 데이터를 이용해 영화의 분포와 관계를 살펴봅니다."
)

# ---------------------------------------------------------
# 데이터 불러오기 / 전처리
# ---------------------------------------------------------
@st.cache_data
def get_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    required = [
        "movieCd", "movieNm", "openDt", "genre", "nation",
        "first_scrn", "first_show", "first_week_audi",
        "total_audi", "days_in_top10"
    ]
    df = df[required].copy()

    # 장르: | 로 여러 장르가 적힌 경우 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 국가: 여러 국가가 있으면 첫 번째 국가를 사용
    df["nation"] = (
        df["nation"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    numeric = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10",
    ]

    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["movieNm"] = df["movieNm"].fillna("영화명 미상")
    df["genre"] = df["genre"].replace("", "미상")
    df["nation"] = df["nation"].replace("", "미상")

    return df


try:
    df = get_data()
except Exception as e:
    st.error("데이터를 불러오지 못했습니다.")
    st.code(str(e))
    st.stop()


def separator():
    st.markdown("---")


def explanation(text):
    st.markdown(
        f"""
        <div style="
            background-color:#f7f7f7;
            border-left:5px solid #666;
            padding:14px 18px;
            margin:10px 0 20px 0;
            border-radius:5px;">
            <b>💡 이 그래프로 알 수 있는 것</b><br>
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# ① 장르별 영화 편수 - 도넛
# =========================================================
st.header("① 장르별 영화 편수")
st.caption("216편의 영화가 어떤 장르로 구성되어 있는지 확인합니다.")

genre_count = (
    df["genre"]
    .value_counts()
    .rename_axis("장르")
    .reset_index(name="영화 편수")
)

fig1 = px.pie(
    genre_count,
    names="장르",
    values="영화 편수",
    hole=0.52,
    title="장르별 영화 편수",
)

fig1.update_traces(
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    ),
)

fig1.update_layout(
    height=600,
    margin=dict(l=20, r=20, t=70, b=20),
    legend_title="장르",
)

st.plotly_chart(fig1, use_container_width=True)
explanation(
    "전체 영화에서 각 장르가 차지하는 영화 편수와 비율을 비교할 수 있습니다."
)


# =========================================================
# ② 장르 → 영화 트리맵
# =========================================================
separator()
st.header("② 장르 안에 들어 있는 영화")
st.caption("장르를 크게 보고, 그 안에서 총 관객이 많은 영화가 얼마나 큰 영역을 차지하는지 봅니다.")

tree_df = df.dropna(subset=["total_audi"]).copy()
tree_df = tree_df[tree_df["total_audi"] >= 0]

fig2 = px.treemap(
    tree_df,
    path=["genre", "movieNm"],
    values="total_audi",
    title="장르별 영화 총 관객 트리맵",
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명<extra></extra>"
    ),
    root_color="lightgrey",
)

fig2.update_layout(
    height=700,
    margin=dict(l=10, r=10, t=70, b=10),
)

st.plotly_chart(fig2, use_container_width=True)
explanation(
    "각 칸의 크기가 총 관객 수를 나타내므로, 같은 장르 안에서도 어떤 영화가 관객을 많이 모았는지 비교할 수 있습니다."
)


# =========================================================
# ③ 총 관객 히스토그램
# =========================================================
separator()
st.header("③ 총 관객 수의 분포")
st.caption("영화별 total_audi가 어느 구간에 가장 많이 모여 있는지 확인합니다.")

hist_df = df.dropna(subset=["total_audi"]).copy()

fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=20,
    title="총 관객 수 히스토그램",
    labels={
        "total_audi": "총 관객 수",
        "count": "영화 편수",
    },
)

fig3.update_traces(
    hovertemplate=(
        "총 관객 구간: %{x}<br>"
        "영화 편수: %{y}편<extra></extra>"
    )
)

fig3.update_layout(
    height=600,
    bargap=0.08,
    margin=dict(l=20, r=20, t=70, b=20),
)

st.plotly_chart(fig3, use_container_width=True)

# 가장 많이 몰린 구간
try:
    bins = pd.cut(hist_df["total_audi"], bins=20, include_lowest=True)
    peak_bin = bins.value_counts().idxmax()
    low = int(peak_bin.left)
    high = int(peak_bin.right)
except Exception:
    low = int(hist_df["total_audi"].min())
    high = int(hist_df["total_audi"].max())

max_idx = hist_df["total_audi"].idxmax()
max_movie = hist_df.loc[max_idx, "movieNm"]
max_audience = int(hist_df.loc[max_idx, "total_audi"])

explanation(
    f"대부분의 영화는 총 관객 약 **{low:,}~{high:,}명** 구간에 몰려 있으며, "
    f"가장 관객이 많은 영화는 **{max_movie}**로 총 **{max_audience:,}명**을 기록했습니다."
)


# =========================================================
# ④ first_scrn × total_audi 산점도
# =========================================================
separator()
st.header("④ 개봉일 스크린 수와 총 관객의 관계")
st.caption("개봉일에 확보한 스크린 수와 최종 총 관객 사이의 관계를 장르별로 비교합니다.")

scatter_df = df.dropna(
    subset=["first_scrn", "total_audi"]
).copy()

fig4 = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    hover_data={
        "first_scrn": ":,",
        "total_audi": ":,",
        "genre": True,
    },
    title="개봉일 스크린 수 × 총 관객",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객",
        "genre": "장르",
    },
)

fig4.update_traces(
    marker=dict(size=10, opacity=0.75),
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린 수: %{x:,}개<br>"
        "총 관객: %{y:,}명<extra></extra>"
    ),
)

fig4.update_layout(
    height=650,
    margin=dict(l=20, r=20, t=70, b=20),
)

st.plotly_chart(fig4, use_container_width=True)
explanation(
    "개봉일 스크린 수가 많은 영화가 총 관객에서도 높은 값을 보이는지, "
    "그리고 장르별로 분포가 어떻게 다른지 확인할 수 있습니다."
)


# =========================================================
# ⑤ 10편 이상 장르 - 박스플롯
# =========================================================
separator()
st.header("⑤ 영화가 10편 이상인 장르의 총 관객 분포")
st.caption("표본이 너무 적은 장르는 제외하고 장르별 total_audi를 비교합니다.")

genre_sizes = df["genre"].value_counts()
selected_genres = genre_sizes[genre_sizes >= 10].index.tolist()

box_df = df[
    df["genre"].isin(selected_genres)
].dropna(subset=["total_audi"]).copy()

fig5 = px.box(
    box_df,
    x="genre",
    y="total_audi",
    color="genre",
    points="outliers",
    hover_name="movieNm",
    hover_data={
        "total_audi": ":,",
        "genre": False,
    },
    title="영화 10편 이상 장르의 총 관객 상자 그림",
    labels={
        "genre": "장르",
        "total_audi": "총 관객",
    },
)

fig5.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "총 관객: %{y:,}명<extra></extra>"
    )
)

fig5.update_layout(
    height=650,
    showlegend=False,
    margin=dict(l=20, r=20, t=70, b=20),
)

st.plotly_chart(fig5, use_container_width=True)
explanation(
    "영화가 10편 이상인 장르만 비교하여 각 장르의 중앙값, 일반적인 관객 범위와 "
    "상자 밖으로 크게 벗어난 영화(이상치)를 확인할 수 있습니다."
)


# =========================================================
# ⑥ 버블 산점도
# =========================================================
separator()
st.header("⑥ 첫 주 관객을 크기로 넣은 버블 그래프")
st.caption("④번 산점도에 first_week_audi를 점 크기로 추가한 그래프입니다.")

bubble_df = df.dropna(
    subset=["first_scrn", "total_audi", "first_week_audi"]
).copy()

# first_week_audi가 0인 경우에도 버블이 사라지지 않게 최소값 처리
bubble_df["bubble_audience"] = bubble_df["first_week_audi"].clip(lower=1)

fig6 = px.scatter(
    bubble_df,
    x="first_scrn",
    y="total_audi",
    size="bubble_audience",
    color="genre",
    hover_name="movieNm",
    hover_data={
        "first_scrn": ":,",
        "total_audi": ":,",
        "first_week_audi": ":,",
        "genre": True,
        "bubble_audience": False,
    },
    size_max=48,
    opacity=0.68,
    title="개봉일 스크린 수 × 총 관객 × 첫 주 관객",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객",
        "first_week_audi": "첫 주 관객",
        "genre": "장르",
    },
)

fig6.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린 수: %{x:,}개<br>"
        "총 관객: %{y:,}명<br>"
        "첫 주 관객: %{customdata[2]:,}명<extra></extra>"
    )
)

# customdata의 열 순서를 명확하게 지정
fig6.update_traces(
    customdata=bubble_df[
        ["first_scrn", "total_audi", "first_week_audi", "genre"]
    ].values
)

fig6.update_layout(
    height=700,
    margin=dict(l=20, r=20, t=70, b=20),
)

st.plotly_chart(fig6, use_container_width=True)
explanation(
    "점의 위치는 개봉일 스크린 수와 총 관객을 나타내고, "
    "점의 크기는 첫 주 관객을 나타내므로 개봉 초반 흥행 규모까지 함께 비교할 수 있습니다."
)


# =========================================================
# ⑦ 제작 국가 → 장르 선버스트
# =========================================================
separator()
st.header("⑦ 제작 국가에서 장르로 내려가는 영화 구성")
st.caption("제작 국가별 영화 편수를 장르까지 내려가며 살펴봅니다.")

sun_df = (
    df.groupby(["nation", "genre"])
    .size()
    .reset_index(name="영화 편수")
)

fig7 = px.sunburst(
    sun_df,
    path=["nation", "genre"],
    values="영화 편수",
    title="제작 국가 → 장르별 영화 구성",
)

fig7.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<extra></extra>"
    )
)

fig7.update_layout(
    height=700,
    margin=dict(l=10, r=10, t=70, b=10),
)

st.plotly_chart(fig7, use_container_width=True)
explanation(
    "바깥쪽으로 갈수록 장르가 세분화되며, 각 영역의 크기는 영화 편수를 나타내므로 "
    "제작 국가별로 어떤 장르의 영화가 많이 포함되어 있는지 비교할 수 있습니다."
)


# ---------------------------------------------------------
# 마지막 정보
# ---------------------------------------------------------
separator()
st.success(f"총 {len(df):,}편의 영화 데이터를 분석했습니다.")
