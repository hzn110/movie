import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# 기본 설정
# =========================================================
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


# =========================================================
# 데이터 불러오기
# =========================================================
@st.cache_data
def load_data():
    usecols = [
        "movieCd",
        "movieNm",
        "openDt",
        "genre",
        "nation",
        "first_scrn",
        "first_show",
        "first_date",
        "first_week_audi",
        "total_audi",
        "days_in_top10",
    ]

    df = pd.read_csv(DATA_URL, encoding="utf-8-sig", usecols=usecols)

    df["movieNm"] = df["movieNm"].fillna("영화명 미상")

    # 여러 장르/국가가 들어 있는 경우 첫 번째 값만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
        .replace("", "미상")
    )

    df["nation"] = (
        df["nation"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
        .replace("", "미상")
    )

    numeric_cols = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["openDt"] = pd.to_datetime(df["openDt"].astype("string"), format="%Y%m%d", errors="coerce")

    return df


df = load_data()


# =========================================================
# CSS
# =========================================================
st.markdown(
    """
<style>
/* 전체 */
.stApp {
    background: #f4f6fa;
}

.block-container {
    max-width: 1280px;
    padding: 35px 32px 70px;
}

/* Streamlit 기본 여백 */
[data-testid="stHeader"] {
    background: transparent;
}

/* 히어로 */
.hero {
    background: linear-gradient(135deg, #111827 0%, #243b68 100%);
    border-radius: 28px;
    padding: 42px 46px;
    margin-bottom: 24px;
    box-shadow: 0 18px 45px rgba(17, 24, 39, 0.16);
}

.hero-kicker {
    color: #a9c2ff !important;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2.5px;
    margin-bottom: 8px;
}

.hero-title {
    color: #ffffff !important;
    font-size: 43px;
    font-weight: 900;
    letter-spacing: -2.5px;
    line-height: 1.15;
    margin: 0;
}

.hero-description {
    color: #d8e0ec !important;
    font-size: 15px;
    line-height: 1.75;
    margin-top: 14px;
    max-width: 900px;
}

/* KPI */
.kpi-card {
    background: #ffffff;
    border: 1px solid #e3e7ee;
    border-radius: 20px;
    padding: 21px 22px;
    min-height: 120px;
    box-shadow: 0 8px 25px rgba(17, 24, 39, 0.055);
}

.kpi-label {
    color: #8a94a5 !important;
    font-size: 12px;
    font-weight: 800;
}

.kpi-value {
    color: #172033 !important;
    font-size: 25px;
    font-weight: 900;
    letter-spacing: -0.7px;
    margin-top: 5px;
}

.kpi-sub {
    color: #a0a8b5 !important;
    font-size: 11px;
    margin-top: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* 구분선 */
.divider {
    height: 1px;
    background: #dfe4ec;
    margin: 40px 0 29px;
}

/* 섹션 제목 */
.section-number {
    display: inline-block;
    background: #e9efff;
    color: #3657a7 !important;
    border-radius: 9px;
    padding: 6px 9px;
    margin-right: 10px;
    font-size: 11px;
    font-weight: 900;
    vertical-align: 3px;
}

.section-title {
    color: #172033 !important;
    font-size: 24px;
    font-weight: 900;
    letter-spacing: -1.2px;
}

.section-description {
    color: #7c8798 !important;
    font-size: 13px;
    margin: 8px 0 14px 48px;
}

/* 그래프 카드 */
.graph-card {
    background: #ffffff;
    border: 1px solid #e3e7ee;
    border-radius: 21px;
    padding: 5px;
    box-shadow: 0 9px 28px rgba(17, 24, 39, 0.055);
}

/* 분석 카드 */
.analysis-card {
    background: #f8faff;
    border: 1px solid #dce6ff;
    border-radius: 16px;
    padding: 17px 20px;
    margin-top: 13px;
    color: #4c586b !important;
    font-size: 13px;
    line-height: 1.85;
}

.analysis-label {
    color: #3657a7 !important;
    font-size: 11px;
    font-weight: 900;
    letter-spacing: 1px;
    margin-bottom: 3px;
}

/* 하단 */
.footer {
    text-align: center;
    color: #98a2b3 !important;
    font-size: 12px;
    padding-top: 5px;
}

/* 모바일 */
@media (max-width: 700px) {
    .block-container {
        padding: 20px 13px 45px;
    }

    .hero {
        padding: 29px 24px;
        border-radius: 21px;
    }

    .hero-title {
        font-size: 30px;
    }

    .hero-description {
        font-size: 13px;
    }

    .section-title {
        font-size: 20px;
    }

    .section-description {
        margin-left: 0;
    }

    .kpi-card {
        margin-bottom: 10px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# UI 함수
# =========================================================
def section_header(number, title, description):
    st.markdown(
        f"""
        <div>
            <span class="section-number">{number:02d}</span>
            <span class="section-title">{title}</span>
            <div class="section-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def graph_card(fig):
    st.markdown('<div class="graph-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def analysis_card(text):
    st.markdown(
        f"""
        <div class="analysis-card">
            <div class="analysis-label">ANALYSIS</div>
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def divider():
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# =========================================================
# 타이틀
# =========================================================
st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">KOBIS · DATA VISUALIZATION</div>
        <div class="hero-title">영화 데이터 그래프 도감 2</div>
        <div class="hero-description">
            장르, 국가, 개봉 규모, 관객 수, 박스오피스 유지 기간을
            서로 다른 시각화 방법으로 비교하여 영화 흥행 데이터의 특징을 분석합니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# KPI
# =========================================================
valid_total = df["total_audi"].dropna()

if len(valid_total) > 0:
    top_movie = df.loc[df["total_audi"].idxmax()]
    top_movie_name = str(top_movie["movieNm"])
    top_movie_audience = f"{int(top_movie['total_audi']):,}명"
else:
    top_movie_name = "-"
    top_movie_audience = "-"

kpis = [
    ("분석 영화", f"{len(df):,}편", "전체 데이터"),
    ("장르", f"{df['genre'].nunique()}개", "첫 번째 장르 기준"),
    ("제작 국가", f"{df['nation'].nunique()}개", "첫 번째 국가 기준"),
    ("최다 총관객", top_movie_audience, top_movie_name),
]

kpi_cols = st.columns(4)

for col, (label, value, sub) in zip(kpi_cols, kpis):
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-sub">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# 01. 도넛
# =========================================================
divider()
section_header(
    1,
    "장르별 영화 편수",
    "전체 영화에서 각 장르가 차지하는 비율을 확인합니다.",
)

genre_count = (
    df["genre"]
    .value_counts()
    .rename_axis("genre")
    .reset_index(name="count")
)

fig1 = px.pie(
    genre_count,
    names="genre",
    values="count",
    hole=0.58,
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
    height=540,
    margin=dict(l=10, r=10, t=20, b=10),
)

graph_card(fig1)

most_genre = genre_count.iloc[0]
analysis_card(
    f"전체 데이터에서 <b>{most_genre['genre']}</b> 장르가 "
    f"<b>{int(most_genre['count'])}편</b>으로 가장 많이 포함되어 있습니다. "
    "이 그래프는 특정 장르의 흥행 정도보다 전체 데이터가 어떤 장르로 구성되어 있는지를 파악하는 데 의미가 있습니다."
)


# =========================================================
# 02. 트리맵
# =========================================================
divider()
section_header(
    2,
    "장르별 영화 흥행 규모",
    "타일의 크기를 총 관객 수로 설정하여 영화별 흥행 규모를 비교합니다.",
)

g2 = df.dropna(subset=["total_audi"]).copy()

fig2 = px.treemap(
    g2,
    path=["genre", "movieNm"],
    values="total_audi",
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명<extra></extra>"
    )
)

fig2.update_layout(
    height=620,
    margin=dict(l=5, r=5, t=20, b=5),
)

graph_card(fig2)

analysis_card(
    "타일이 클수록 총 관객 수가 많은 영화입니다. "
    "장르 전체의 규모뿐 아니라 같은 장르 안에서 어떤 영화가 특히 큰 흥행을 기록했는지도 한눈에 비교할 수 있습니다."
)


# =========================================================
# 03. 히스토그램
# =========================================================
divider()
section_header(
    3,
    "총 관객 수 분포",
    "영화들의 총 관객 수가 어느 구간에 집중되어 있는지 확인합니다.",
)

g3 = df.dropna(subset=["total_audi"]).copy()

fig3 = px.histogram(
    g3,
    x="total_audi",
    nbins=20,
)

fig3.update_layout(
    height=540,
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수",
    margin=dict(l=25, r=20, t=20, b=30),
)

graph_card(fig3)

if len(g3) > 0:
    bins = pd.cut(g3["total_audi"], bins=20)
    common_range = bins.value_counts().idxmax()

    analysis_card(
        f"영화가 가장 많이 몰려 있는 구간은 약 "
        f"<b>{int(common_range.left):,}~{int(common_range.right):,}명</b>입니다. "
        f"반면 가장 많은 총 관객을 기록한 영화는 <b>{top_movie_name}</b>으로 "
        f"<b>{top_movie_audience}</b>을 기록했습니다. "
        "따라서 전체 영화의 관객 분포와 최고 흥행 영화 사이에는 큰 차이가 나타날 수 있습니다."
    )


# =========================================================
# 04. 산점도
# =========================================================
divider()
section_header(
    4,
    "개봉일 스크린 수와 총 관객",
    "개봉 당시 확보한 스크린 규모와 최종 관객 수를 비교합니다.",
)

g4 = df.dropna(subset=["first_scrn", "total_audi"]).copy()

fig4 = px.scatter(
    g4,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
)

fig4.update_traces(
    marker=dict(size=9, opacity=0.7),
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린: %{x:,}개<br>"
        "총 관객: %{y:,}명<extra></extra>"
    ),
)

fig4.update_layout(
    height=590,
    xaxis_title="개봉일 스크린 수",
    yaxis_title="총 관객 수",
    margin=dict(l=25, r=20, t=20, b=30),
)

graph_card(fig4)

analysis_card(
    "개봉일 스크린 수가 많을수록 더 많은 관객을 확보할 가능성이 있는지 확인할 수 있습니다. "
    "다만 같은 스크린 규모에서도 영화마다 총 관객 수의 차이가 크게 나타날 수 있어, "
    "개봉 규모만으로 최종 흥행을 설명하기는 어렵습니다."
)


# =========================================================
# 05. 박스플롯
# =========================================================
divider()
section_header(
    5,
    "장르별 총 관객 분포",
    "영화가 10편 이상인 장르만 대상으로 관객 수의 분포와 이상치를 비교합니다.",
)

genre_over_10 = df["genre"].value_counts()
valid_genres = genre_over_10[genre_over_10 >= 10].index

g5 = df[
    df["genre"].isin(valid_genres)
].dropna(subset=["total_audi"]).copy()

fig5 = px.box(
    g5,
    x="genre",
    y="total_audi",
    color="genre",
    points="outliers",
    hover_name="movieNm",
)

fig5.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "총 관객: %{y:,}명<extra></extra>"
    )
)

fig5.update_layout(
    height=590,
    xaxis_title="장르",
    yaxis_title="총 관객 수",
    showlegend=False,
    margin=dict(l=25, r=20, t=20, b=30),
)

graph_card(fig5)

analysis_card(
    "상자와 중앙선을 통해 장르별 관객 수가 어느 범위에 모여 있는지 비교할 수 있습니다. "
    "상자 밖의 점은 해당 장르에서 다른 영화보다 특히 높은 관객 수를 기록한 이상치 영화입니다."
)


# =========================================================
# 06. 버블 그래프
# =========================================================
divider()
section_header(
    6,
    "개봉 규모·첫 주 관객·총 관객",
    "점의 크기를 첫 주 관객 수로 설정하여 세 가지 흥행 지표를 동시에 비교합니다.",
)

g6 = df.dropna(
    subset=["first_scrn", "total_audi", "first_week_audi"]
).copy()

fig6 = px.scatter(
    g6,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    custom_data=["first_week_audi"],
    size_max=42,
    opacity=0.68,
)

fig6.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린: %{x:,}개<br>"
        "총 관객: %{y:,}명<br>"
        "첫 주 관객: %{customdata[0]:,}명"
        "<extra></extra>"
    )
)

fig6.update_layout(
    height=610,
    xaxis_title="개봉일 스크린 수",
    yaxis_title="총 관객 수",
    margin=dict(l=25, r=20, t=20, b=30),
)

graph_card(fig6)

analysis_card(
    "가로축은 개봉일 스크린 수, 세로축은 총 관객 수이며 점의 크기는 첫 주 관객 수를 의미합니다. "
    "따라서 영화의 개봉 규모와 초반 관객, 최종 관객을 동시에 비교할 수 있습니다."
)


# =========================================================
# 07. 선버스트
# =========================================================
divider()
section_header(
    7,
    "제작 국가와 장르 구성",
    "국가별 영화 편수를 장르까지 나누어 영화 구성을 살펴봅니다.",
)

g7 = (
    df.groupby(["nation", "genre"])
    .size()
    .reset_index(name="count")
)

fig7 = px.sunburst(
    g7,
    path=["nation", "genre"],
    values="count",
)

fig7.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<extra></extra>"
    )
)

fig7.update_layout(
    height=620,
    margin=dict(l=5, r=5, t=20, b=5),
)

graph_card(fig7)

top_nation = df["nation"].value_counts().idxmax()

analysis_card(
    f"가장 많은 영화가 포함된 제작 국가는 <b>{top_nation}</b>입니다. "
    "선버스트의 바깥쪽 영역을 보면 각 국가에 어떤 장르의 영화가 많이 포함되어 있는지도 확인할 수 있습니다."
)


# =========================================================
# 08. 완전히 새로운 그래프
# 기존 '첫 주 관객 vs 총 관객' 산점도와 다른 주제
# =========================================================
divider()
section_header(
    8,
    "개봉 월별 영화 흥행 분포",
    "각 개봉 월의 영화들이 어느 정도의 관객 규모에 분포하는지 비교합니다.",
)

g8 = df.dropna(subset=["openDt", "total_audi", "movieNm"]).copy()
g8["개봉월"] = g8["openDt"].dt.month
g8["월"] = g8["개봉월"].astype(int).astype(str) + "월"

month_order = [f"{i}월" for i in range(1, 13)]

fig8 = px.box(
    g8,
    x="월",
    y="total_audi",
    category_orders={"월": month_order},
    points="all",
    custom_data=["movieNm"],
)

fig8.update_traces(
    marker_size=6,
    jitter=0.28,
    pointpos=0,
    boxmean=True,
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    ),
)

fig8.update_layout(
    yaxis_title="총 관객 수 (로그 스케일)",
    xaxis_title="개봉 월",
    showlegend=False,
    yaxis_type="log",
)

graph_card(fig8)

month_stats = (
    g8.groupby(["개봉월", "월"])["total_audi"]
    .agg(중앙값="median", 평균="mean", 영화_편수="count", 최소="min", 최대="max")
    .reset_index()
    .sort_values("개봉월")
)

if not month_stats.empty:
    median_row = month_stats.loc[month_stats["중앙값"].idxmax()]
    median_low_row = month_stats.loc[month_stats["중앙값"].idxmin()]
    analysis_text = (
        f"월별 영화의 **총 관객 수 분포**를 비교한 결과, "
        f"중앙값이 가장 높은 달은 **{median_row['월']}**로 "
        f"{median_row['중앙값']:,.0f}명이며, 가장 낮은 달은 "
        f"**{median_low_row['월']}**로 {median_low_row['중앙값']:,.0f}명이다. "
        f"박스플롯은 평균 하나만 비교하는 대신 중앙값과 영화들의 분포, "
        f"개별 흥행작을 함께 보여주기 때문에 특정 대작 하나의 영향이 과도하게 나타나는 것을 줄일 수 있다. "
        f"또한 월별 영화 편수도 다르므로, 개봉 월만으로 흥행 여부를 판단하기보다는 "
        f"각 월의 분포와 표본 수를 함께 살펴보는 것이 적절하다."
    )
    analysis_card(analysis_text)

divider()

st.markdown(
    f"""
    <div class="footer">
        총 {len(df):,}편의 영화 데이터를 활용한 인터랙티브 데이터 분석
    </div>
    """,
    unsafe_allow_html=True,
)
