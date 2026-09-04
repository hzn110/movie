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

# =========================================================
# UI 디자인
# =========================================================
st.markdown("""
<style>
    /* 전체 배경과 기본 글자 */
    .stApp {
        background: #f5f7fb;
    }

    .main .block-container {
        max-width: 1200px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }

    /* 모든 기본 텍스트를 어두운 색으로 */
    html, body, [class*="css"] {
        color: #172033 !important;
    }

    p, li, span, label, div {
        color: #172033;
    }

    /* 제목 */
    h1 {
        color: #111827 !important;
        font-size: 2.35rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.04em;
        margin-bottom: 0.35rem !important;
    }

    h2 {
        color: #111827 !important;
        font-size: 1.55rem !important;
        font-weight: 750 !important;
        letter-spacing: -0.025em;
        margin-top: 0.4rem !important;
    }

    h3 {
        color: #1f2937 !important;
        font-weight: 700 !important;
    }

    /* 상단 설명 */
    .intro {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 20px 24px;
        margin: 0.5rem 0 1.5rem 0;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
    }

    .intro-title {
        color: #111827 !important;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .intro-text {
        color: #4b5563 !important;
        line-height: 1.7;
        font-size: 0.94rem;
    }

    /* 그래프 섹션 */
    .section-label {
        display: inline-block;
        background: #111827;
        color: #ffffff !important;
        border-radius: 8px;
        padding: 5px 10px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-bottom: 7px;
    }

    .section-description {
        color: #6b7280 !important;
        font-size: 0.91rem;
        margin-bottom: 8px;
    }

    /* 설명/인사이트 박스 */
    .insight-box {
        background: #ffffff !important;
        border: 1px solid #dbe2ea;
        border-left: 5px solid #4f46e5;
        border-radius: 10px;
        padding: 15px 18px;
        margin: 12px 0 28px 0;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.04);
    }

    .insight-title {
        color: #312e81 !important;
        font-weight: 800;
        font-size: 0.92rem;
        margin-bottom: 5px;
    }

    .insight-text {
        color: #374151 !important;
        line-height: 1.65;
        font-size: 0.9rem;
    }

    /* Streamlit 알림 박스의 글씨 */
    [data-testid="stAlert"] {
        color: #172033 !important;
    }

    [data-testid="stAlert"] p,
    [data-testid="stAlert"] div,
    [data-testid="stAlert"] span {
        color: #172033 !important;
    }

    /* 그래프 주변 */
    [data-testid="stPlotlyChart"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 8px;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.045);
        margin-bottom: 8px;
    }

    /* 구분선 */
    hr {
        border: 0 !important;
        border-top: 1px solid #e1e6ed !important;
        margin: 2.2rem 0 1.8rem 0 !important;
    }

    /* 성공/정보 박스 */
    [data-testid="stAlert"][kind="info"] {
        background: #eef2ff !important;
        border: 1px solid #c7d2fe !important;
    }

    [data-testid="stAlert"][kind="success"] {
        background: #ecfdf5 !important;
        border: 1px solid #a7f3d0 !important;
    }

    /* 모바일 */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1.2rem 0.8rem 3rem 0.8rem;
        }

        h1 {
            font-size: 1.8rem !important;
        }

        h2 {
            font-size: 1.3rem !important;
        }

        .intro {
            padding: 16px;
        }
    }
</style>
""", unsafe_allow_html=True)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

st.title("🎬 영화 데이터 그래프 도감 2")
st.markdown(
    """
    <div class="intro">
        <div class="intro-title">분포와 관계를 한눈에 살펴보는 영화 데이터 분석</div>
        <div class="intro-text">
            1년간 박스오피스 10위권에 든 영화 가운데 해당 기간에 개봉한
            <b>216편</b>의 데이터를 바탕으로 장르, 관객 수, 개봉 규모,
            제작 국가 등의 관계를 시각적으로 분석합니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
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
        <div class="insight-box">
            <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
            <div class="insight-text">{text}</div>
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
st.header("⑥ 개봉 규모 × 총관객 × 첫 주 관객")
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
st.header("⑦ 제작 국가 → 장르 구성")
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
# =========================================================
# ⑧ 개봉 첫 주 관객과 총 관객의 관계
# =========================================================
separator()

st.header("⑧ 개봉 첫 주 관객이 높은 영화는 총관객도 높은가?")
st.caption("개봉 첫 주 관객 수와 총 관객 수가 실제로 함께 증가하는지 확인합니다.")

week_df = df[["movieNm", "genre", "first_week_audi", "total_audi"]].copy()
week_df["first_week_audi"] = pd.to_numeric(week_df["first_week_audi"], errors="coerce")
week_df["total_audi"] = pd.to_numeric(week_df["total_audi"], errors="coerce")
week_df = week_df.dropna(
    subset=["movieNm", "first_week_audi", "total_audi"]
)

fig8 = px.scatter(
    week_df,
    x="first_week_audi",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    hover_data={
        "first_week_audi": ":,",
        "total_audi": ":,",
        "genre": True,
    },
    labels={
        "first_week_audi": "개봉 첫 주 관객 수",
        "total_audi": "총 관객 수",
        "genre": "장르",
    },
)

fig8.update_layout(
    title="개봉 첫 주 관객 수와 총 관객 수의 관계",
    xaxis_title="개봉 첫 주 관객 수(명)",
    yaxis_title="총 관객 수(명)",
    height=650,
)

st.plotly_chart(fig8, use_container_width=True)

corr = week_df["first_week_audi"].corr(week_df["total_audi"])

if pd.notna(corr):
    st.info(
        f"**상관계수: {corr:.2f}**  \n"
        "상관계수가 1에 가까울수록 개봉 첫 주 관객이 많은 영화가 "
        "총 관객도 많은 경향이 강하다는 의미입니다."
    )

explanation(
    "개봉 첫 주 관객 수와 총 관객 수를 직접 비교한 그래프입니다. "
    "점들이 오른쪽 위 방향으로 뚜렷하게 모여 있다면 "
    "개봉 초반 흥행이 최종 흥행과 관련이 있다고 볼 수 있습니다."
)
