import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
import os

# ======================== 1. 字体配置（用你上传的字体） ========================
font_path = 'SourceHanSerifCN-Bold.otf'
if os.path.exists(font_path):
    font_prop = FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
else:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# ======================== 2. 页面基础配置（轻量美化） ========================
st.set_page_config(
    page_title="百家姓可视化",
    page_icon="🏮",
    layout="wide"
)

# 轻量CSS美化（只改背景色，不影响稳定性）
st.markdown("""
<style>
.stApp {background-color: #f8f9fa;}
h1, h2, h3 {color: #2c3e50;}
</style>
""", unsafe_allow_html=True)

# ======================== 3. 加载数据（保持原来的写法） ========================
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

# ======================== 4. 标题（简化版） ========================
st.title("🏮 中国百家姓起源地可视化")
st.divider()

# ======================== 5. 筛选控件（保持原来的写法，不改动） ========================
st.subheader("🔍 数据筛选")
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

# 提示框（去掉HTML格式，避免报错）
st.info(f"当前筛选结果：共 {len(df_filtered)} 个姓氏（总数据：438个）")
st.divider()

# ======================== 6. 地图（保持原来的写法） ========================
st.subheader("🗺️ 姓氏起源地分布")
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
    color="#0066cc",
    zoom=4 if province == "全部" else 7
)
st.divider()

# ======================== 7. 柱状图（用你的字体，不改动逻辑） ========================
st.subheader("📊 姓氏人口占比Top10")
df_top10 = df_filtered.sort_values("人口占比", ascending=False).head(10)

fig, ax = plt.subplots(figsize=(10, 5))
colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(df_top10)))
bars = ax.bar(
    df_top10["姓氏"],
    df_top10["人口占比"],
    color=colors,
    edgecolor="#0066cc",
    linewidth=1
)

# 所有标签强制用你的字体
ax.set_xlabel("姓氏", fontproperties=font_prop, fontsize=10, color="#333")
ax.set_ylabel("人口占比(%)", fontproperties=font_prop, fontsize=10, color="#333")
ax.set_title(f"{'全国' if province == '全部' else province} 姓氏人口占比Top10", 
             fontproperties=font_prop, fontsize=12, color="#0066cc", pad=10)
ax.set_facecolor("#f0f2f6")
fig.patch.set_facecolor("#f0f2f6")

ax.grid(True, axis="y", alpha=0.3, color="#0066cc")
ax.set_axisbelow(True)
ax.tick_params(axis="x", colors="#333", rotation=45, labelsize=9)
ax.tick_params(axis="y", colors="#333", labelsize=9)

# 刻度标签字体
for label in ax.get_xticklabels():
    label.set_fontproperties(font_prop)

for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width()/2.,
        height + 0.05,
        f"{height:.2f}%",
        ha="center", va="bottom", color="#0066cc", fontsize=8
    )
st.pyplot(fig)
st.divider()

# ======================== 8. 饼图（用你的字体，不改动逻辑） ========================
st.subheader("🥧 姓氏类型 & 起源类型分布")
col_pie1, col_pie2 = st.columns(2)

with col_pie1:
    type_counts = df_filtered["姓氏类型"].value_counts()
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    colors1 = ["#0066cc", "#ff6b6b"]
    wedges, texts, autotexts = ax1.pie(
        type_counts.values,
        labels=type_counts.index,
        autopct="%1.1f%%",
        colors=colors1,
        startangle=90,
        textprops={"fontproperties": font_prop, "color": "#333", "fontsize": 10}
    )
    for autotext in autotexts:
        autotext.set_color("#fff")
        autotext.set_fontweight("bold")
    ax1.set_title("单姓/复姓占比", fontproperties=font_prop, fontsize=12, color="#0066cc", pad=10)
    fig1.patch.set_facecolor("#f0f2f6")
    st.pyplot(fig1)

with col_pie2:
    origin_counts = df_filtered["起源类型"].value_counts()
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    colors2 = plt.cm.Set3(np.linspace(0, 1, len(origin_counts)))
    wedges2, texts2, autotexts2 = ax2.pie(
        origin_counts.values,
        labels=origin_counts.index,
        autopct="%1.1f%%",
        colors=colors2,
        startangle=90,
        textprops={"fontproperties": font_prop, "color": "#333", "fontsize": 9}
    )
    for autotext in autotexts2:
        autotext.set_color("#fff")
        autotext.set_fontweight("bold")
    ax2.set_title("起源类型占比", fontproperties=font_prop, fontsize=12, color="#0066cc", pad=10)
    fig2.patch.set_facecolor("#f0f2f6")
    st.pyplot(fig2)

st.divider()

# ======================== 9. 数据表格（保持原来的写法） ========================
st.subheader("📋 当前筛选的姓氏列表")
st.dataframe(df_filtered[["排名", "姓氏", "起源地", "省份", "人口占比", "起源类型"]], use_container_width=True)

st.markdown("""
### 📝 操作说明
1. **筛选功能**：选省份/姓氏类型/起源类型，所有图表实时更新；
2. **数据表格**：底部表格可查看所有筛选后的姓氏详细信息；
3. **图表细节**：柱状图顶部有具体数值，饼图显示百分比。
""")
