import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ======================== 字体加载 ========================
font_path = 'SourceHanSerifCN-Bold.otf'
if os.path.exists(font_path):
    font_prop = FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
else:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# ======================== 百家姓古风主题配色（典雅书卷风） ========================
st.markdown("""
<style>
.stApp {
    background-color: #f8f1e3; /* 宣纸米黄底 */
}
.block-container {
    background-color: #fff9ec; /* 淡宣纸白 */
    border-radius: 14px;
    box-shadow: 0 3px 12px rgba(160, 82, 45, 0.15);
    padding: 2rem;
}
h1, h2, h3 {
    color: #9c2c1a !important; /* 朱砂暗红 */
    font-family: SimHei, KaiTi, serif;
}
div[data-baseweb="select"] {
    border: 1px solid #d2b48c;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ======================== 字体（支持中文+古风） ========================
plt.rcParams['font.sans-serif'] = ['SimHei', 'KaiTi', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# ======================== 页面标题 ========================
st.set_page_config(
    page_title="中华百家姓可视化",
    page_icon="📜",
    layout="wide"
)
st.title("📜 中华百家姓·起源与分布可视化")
st.divider()

# ======================== 加载全部数据 ========================
@st.cache_data
def load_all_data():
    # 核心数据
    df_core = pd.read_excel("百家姓_项目完整数据.xlsx")
    df_core = df_core[["排名", "姓氏", "起源地", "省份", "人口占比(%)", "姓氏类型", "起源类型"]]
    df_core.rename(columns={"人口占比(%)": "人口占比"}, inplace=True)
    df_core = df_core.dropna(subset=["省份"])

    # 前300名
    df_top300 = pd.read_excel("2026 中国姓氏前300名排名 + 人口（万人）+ 占比（%）.xlsx")
    df_top300.columns = ["排名_300", "姓氏_300", "人口_万人", "占比_300%"]

    # 郡望堂号
    df_culture = pd.read_excel("完整姓氏 - 郡望 - 今地 - 堂号总表.xlsx")

    return df_core, df_top300, df_culture

df, df_top300, df_culture = load_all_data()

# ======================== 一、数据筛选 ========================
st.subheader("🔍 数据筛选")
col1, col2, col3 = st.columns(3)

with col1:
    province = st.selectbox("选择省份", ["全部"] + sorted(df["省份"].unique()))
with col2:
    stype = st.selectbox("选择姓氏类型", ["全部"] + sorted(df["姓氏类型"].unique()))
with col3:
    otype = st.selectbox("选择起源类型", ["全部"] + sorted(df["起源类型"].unique()))

df_filtered = df.copy()
if province != "全部":
    df_filtered = df_filtered[df_filtered["省份"] == province]
if stype != "全部":
    df_filtered = df_filtered[df_filtered["姓氏类型"] == stype]
if otype != "全部":
    df_filtered = df_filtered[df_filtered["起源类型"] == otype]

st.info(f"筛选结果：共 {len(df_filtered)} 个姓氏")
st.divider()

# ======================== 二、姓氏起源地图 ========================
st.subheader("🗺️ 姓氏起源地理分布")
province_lonlat = {
    "北京": [116.40, 39.90], "天津": [117.20, 39.13], "河北": [114.30, 38.04], "山西": [112.53, 37.87],
    "内蒙古": [111.67, 40.82], "辽宁": [123.43, 41.80], "吉林": [125.32, 43.88], "黑龙江": [126.53, 45.80],
    "上海": [121.47, 31.23], "江苏": [118.78, 32.04], "浙江": [120.15, 30.27], "安徽": [117.28, 31.86],
    "福建": [119.30, 26.08], "江西": [115.89, 28.68], "山东": [117.00, 36.67], "河南": [113.63, 34.76],
    "湖北": [114.31, 30.52], "湖南": [112.94, 28.23], "广东": [113.26, 23.13], "广西": [108.37, 22.82],
    "海南": [110.35, 20.02], "重庆": [106.55, 29.57], "四川": [104.07, 30.67], "贵州": [106.71, 26.57],
    "云南": [102.71, 25.04], "西藏": [91.11, 29.66], "陕西": [108.95, 34.27], "甘肃": [103.82, 36.06],
    "青海": [101.78, 36.62], "宁夏": [106.27, 38.47], "新疆": [87.62, 43.83]
}

df_map = df_filtered.copy()
# 修复：分别提取经度和纬度
df_map["lon"] = df_map["省份"].map(lambda x: province_lonlat.get(x, [104.07, 30.67])[0])
df_map["lat"] = df_map["省份"].map(lambda x: province_lonlat.get(x, [104.07, 30.67])[1])

st.map(
    df_map,
    latitude="lat",
    longitude="lon",
    size="人口占比",
    color="#9c2c1a",
    zoom=4 if province == "全部" else 7
)
st.divider()

# ======================== 三、人口TOP10柱状图（古风棕红） ========================
st.subheader("📊 姓氏人口占比 TOP10")
df_top10 = df_filtered.sort_values("人口占比", ascending=False).head(10)

fig, ax = plt.subplots(figsize=(10, 5))
colors = plt.cm.Reds(np.linspace(0.4, 0.8, len(df_top10)))
bars = ax.bar(df_top10["姓氏"], df_top10["人口占比"], color=colors, edgecolor="#9c2c1a")

ax.set_title("姓氏人口占比TOP10", color="#9c2c1a", fontsize=12)
ax.set_ylabel("人口占比(%)", color="#5c2c21")
ax.set_facecolor("#f8f1e3")
fig.patch.set_facecolor("#f8f1e3")

for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x()+bar.get_width()/2, h+0.08, f"{h:.2f}%", ha="center", color="#9c2c1a")

st.pyplot(fig)
st.divider()

# ======================== 四、双饼图（古风配色） ========================
st.subheader("🥧 姓氏类型 & 起源类型分布")
c1, c2 = st.columns(2)

with c1:
    type_counts = df_filtered["姓氏类型"].value_counts()
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    colors1 = ["#9c2c1a", "#d2b48c"]
    wedges, texts, autotexts = ax1.pie(
        type_counts.values, labels=type_counts.index, autopct="%1.1f%%",
        colors=colors1, startangle=90
    )
    for a in autotexts:
        a.set_color("white")
    ax1.set_title("单姓/复姓占比", color="#9c2c1a")
    fig1.patch.set_facecolor("#f8f1e3")
    st.pyplot(fig1)

with c2:
    origin_counts = df_filtered["起源类型"].value_counts()
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    colors2 = ["#a0522d", "#cd853f", "#d2b48c", "#9c2c1a"]
    wedges2, texts2, autotexts2 = ax2.pie(
        origin_counts.values, labels=origin_counts.index, autopct="%1.1f%%",
        colors=colors2, startangle=90
    )
    for a in autotexts2:
        a.set_color("white")
    ax2.set_title("起源类型占比", color="#9c2c1a")
    fig2.patch.set_facecolor("#f8f1e3")
    st.pyplot(fig2)

st.divider()

# ======================== 五、前300名人口对比 ========================
if not df_top300.empty:
    st.subheader("📈 前300名姓氏人口对比")
    rank_range = st.slider("选择排名区间", 1, 300, (1, 50))
    df_rank = df_top300[(df_top300["排名_300"] >= rank_range[0]) & (df_top300["排名_300"] <= rank_range[1])]

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = plt.cm.Reds(np.linspace(0.4, 0.8, len(df_rank)))
    bars = ax.bar(df_rank["姓氏_300"], df_rank["人口_万人"], color=colors, edgecolor="#9c2c1a")

    ax.set_title("姓氏人口对比", color="#9c2c1a")
    ax.set_ylabel("人口（万人）", color="#5c2c21")
    ax.set_facecolor("#f8f1e3")
    fig.patch.set_facecolor("#f8f1e3")

    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x()+bar.get_width()/2, h+50, f"{int(h)}万", ha="center", color="#9c2c1a")

    st.pyplot(fig)
    st.dataframe(df_top300, use_container_width=True)
    st.divider()

# ======================== 六、郡望·堂号查询 ========================
if not df_culture.empty:
    st.subheader("🏯 姓氏郡望·堂号查询")
    search = st.text_input("输入姓氏查询（如：李、王）")
    if search:
        res = df_culture[df_culture["姓氏"].str.contains(search, na=False)]
        if len(res) > 0:
            st.success(f"找到 {len(res)} 条信息")
            st.dataframe(res, use_container_width=True)
        else:
            st.warning("未找到")
    else:
        st.dataframe(df_culture.head(20), use_container_width=True)
    st.divider()

# ======================== 七、数据列表 ========================
st.subheader("📜 筛选结果列表")
st.dataframe(df_filtered, use_container_width=True)

# ======================== 说明 ========================
st.markdown("""
### 📜 项目说明
本系统基于中华百家姓数据，整合姓氏起源、地理分布、人口统计、郡望堂号文化信息，
实现古风典雅的数据可视化，兼具文化性与学术价值。
""")
