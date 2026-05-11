import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
import os

# ======================== 字体加载 ========================
font_path = 'SourceHanSerifCN-Bold.otf'
if os.path.exists(font_path):
    font_prop = FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
else:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# ======================== 页面基础配置 ========================
st.set_page_config(
    page_title="百家姓古风可视化",
    page_icon="🏮",
    layout="wide"
)

# ======================== 古风全局CSS（仿新华网宋词风格） ========================
st.markdown("""
<style>
/* 全局古风背景 */
.stApp {
    background-color: #f5efe6;
    background-image: url("https://img0.baidu.com/it/u=2676132399,2879307239&fm=253&fmt=auto&app=138&f=JPEG?w=800&h=500");
    background-attachment: fixed;
    background-size: cover;
}
/* 主标题古风样式 */
h1 {
    color: #8c3123 !important;
    font-family: 思源宋体, SimHei !important;
    text-align: center;
    letter-spacing: 6px;
}
h2,h3,h4 {
    color: #5c2c21 !important;
    font-family: 思源宋体, SimHei !important;
}
/* 卡片古风白底磨砂 */
.block-container {
    background-color: rgba(255,255,255,0.85);
    border-radius: 16px;
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 4px 15px rgba(92,44,33,0.15);
}
/* 下拉选择框古风圆角 */
div[data-baseweb="select"] {
    border-radius: 10px !important;
    border: 1px solid #c9b79c !important;
}
/* 分割线古风 */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, #8c3123, transparent);
    margin: 2rem 0;
}
/* 表格圆角古风 */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# ======================== 加载数据 ========================
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("百家姓_项目完整数据.xlsx")
        df = df[["排名", "姓氏", "起源地", "省份", "人口占比(%)", "姓氏类型", "起源类型"]].copy()
        df.rename(columns={"人口占比(%)": "人口占比"}, inplace=True)
        return df.dropna(subset=["省份"])
    except FileNotFoundError:
        st.error("❌ 未找到Excel文件！")
        st.stop()

df = load_data()

# ======================== 标题 ========================
st.title("🏮 中华百家姓 · 起源地古风可视化")
st.divider()

# ======================== 筛选控件 ========================
st.subheader("🔍 多维数据筛选")
col1, col2, col3 = st.columns(3)

with col1:
    province = st.selectbox(
        "选择省份",
        options=["全部"] + sorted(df["省份"].unique()),
        index=0
    )

with col2:
    surname_type = st.selectbox(
        "选择姓氏类型",
        options=["全部"] + sorted(df["姓氏类型"].unique()),
        index=0
    )

with col3:
    origin_type = st.selectbox(
        "选择起源类型",
        options=["全部"] + sorted(df["起源类型"].unique()),
        index=0
    )

# 筛选逻辑
df_filtered = df.copy()
if province != "全部":
    df_filtered = df_filtered[df_filtered["省份"] == province]
if surname_type != "全部":
    df_filtered = df_filtered[df_filtered["姓氏类型"] == surname_type]
if origin_type != "全部":
    df_filtered = df_filtered[df_filtered["起源类型"] == origin_type]

st.info(f"📜 当前筛选结果：共 {len(df_filtered)} 个姓氏 | 全域总计438个姓氏")
st.divider()

# ======================== 地图 ========================
st.subheader("🗺️ 姓氏起源地理分布图")
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
df_map["lon"] = df_map["省份"].map(lambda x: province_lonlat.get(x, [104.07, 30.67])[0])
df_map["lat"] = df_map["省份"].map(lambda x: province_lonlat.get(x, [104.07, 30.67])[1])

st.map(
    df_map,
    latitude="lat",
    longitude="lon",
    size="人口占比",
    color="#8c3123",
    zoom=4 if province == "全部" else 7
)
st.divider()

# ======================== 柱状图 ========================
st.subheader("📊 姓氏人口占比TOP10")
df_top10 = df_filtered.sort_values("人口占比", ascending=False).head(10)

fig, ax = plt.subplots(figsize=(10, 5))
colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(df_top10)))
bars = ax.bar(
    df_top10["姓氏"],
    df_top10["人口占比"],
    color=colors,
    edgecolor="#8c3123",
    linewidth=1
)

ax.set_xlabel("姓氏", fontproperties=font_prop, fontsize=10, color="#5c2c21")
ax.set_ylabel("人口占比(%)", fontproperties=font_prop, fontsize=10, color="#5c2c21")
ax.set_title(f"{'全国' if province == '全部' else province} 姓氏人口占比排行", 
             fontproperties=font_prop, fontsize=12, color="#8c3123", pad=10)
ax.set_facecolor("#f5efe6")
fig.patch.set_facecolor("#f5efe6")

ax.grid(True, axis="y", alpha=0.3, color="#8c3123")
ax.set_axisbelow(True)
ax.tick_params(axis="x", colors="#5c2c21", rotation=45, labelsize=9)
ax.tick_params(axis="y", colors="#5c2c21", labelsize=9)

for label in ax.get_xticklabels():
    label.set_fontproperties(font_prop)

for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width()/2.,
        height + 0.05,
        f"{height:.2f}%",
        ha="center", va="bottom", color="#8c3123", fontsize=8
    )
st.pyplot(fig)
st.divider()

# ======================== 双饼图 ========================
st.subheader("🥧 姓氏类型与起源分布")
col_pie1, col_pie2 = st.columns(2)

with col_pie1:
    type_counts = df_filtered["姓氏类型"].value_counts()
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    colors1 = ["#8c3123", "#c9b79c"]
    wedges, texts, autotexts = ax1.pie(
        type_counts.values,
        labels=type_counts.index,
        autopct="%1.1f%%",
        colors=colors1,
        startangle=90,
        textprops={"fontproperties": font_prop, "color": "#5c2c21", "fontsize": 10}
    )
    for autotext in autotexts:
        autotext.set_color("#fff")
        autotext.set_fontweight("bold")
    ax1.set_title("单姓/复姓占比", fontproperties=font_prop, fontsize=12, color="#8c3123", pad=10)
    fig1.patch.set_facecolor("#f5efe6")
    st.pyplot(fig1)

with col_pie2:
    origin_counts = df_filtered["起源类型"].value_counts()
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    colors2 = plt.cm.Pastel1(np.linspace(0, 1, len(origin_counts)))
    wedges2, texts2, autotexts2 = ax2.pie(
        origin_counts.values,
        labels=origin_counts.index,
        autopct="%1.1f%%",
        colors=colors2,
        startangle=90,
        textprops={"fontproperties": font_prop, "color": "#5c2c21", "fontsize": 9}
    )
    for autotext in autotexts2:
        autotext.set_color("#fff")
        autotext.set_fontweight("bold")
    ax2.set_title("起源类型占比", fontproperties=font_prop, fontsize=12, color="#8c3123", pad=10)
    fig2.patch.set_facecolor("#f5efe6")
    st.pyplot(fig2)

st.divider()

# ======================== 数据表格 ========================
st.subheader("📜 姓氏详细典籍列表")
st.dataframe(df_filtered[["排名", "姓氏", "起源地", "省份", "人口占比", "起源类型"]], use_container_width=True)

# 底部古风说明
st.markdown("""
<div style="background:rgba(255,255,255,0.85);padding:1.5rem;border-radius:16px;color:#5c2c21;font-family:思源宋体;">
<h4>📖 项目说明</h4>
<p>本项目以中华百家姓为研究对象，依托Python数据分析技术，结合地理信息与人口占比数据，
实现多条件筛选、地理分布可视化、统计图表分析，复刻传统国风典籍展示风格，
兼具文化性与数据可视化研究价值。</p>
</div>
""", unsafe_allow_html=True)
