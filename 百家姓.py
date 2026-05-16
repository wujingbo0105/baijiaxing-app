import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
from PIL import Image
import os

# ========== 核心修复1：解决图片像素超限 + 合理设置图表尺寸 ==========
Image.MAX_IMAGE_PIXELS = 200000000  # 限制为2亿像素（足够用且避免DOS风险）
plt.rcParams['figure.max_open_warning'] = 0  # 关闭图表数量警告

# ========== 核心修复2：服务器中文字体兼容（无需本地字体文件） ==========
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
# 兜底字体配置（无需本地otf文件）
font_prop = FontProperties(family='DejaVu Sans')

# ========== 页面基础配置（优化布局） ==========
st.set_page_config(
    page_title="百家姓可视化",
    page_icon="🏮",
    layout="wide"
)

# 古风CSS（适配字体+优化页面间距）
st.markdown("""
<style>
.stApp {background-color: #f8f1e3; padding: 1rem;}
h1, h2, h3 {color: #9c2c1a !important; font-family: sans-serif;}
.stDataFrame, .stSelectbox, .stTextInput {font-family: sans-serif !important;}
.stSlider > div {padding: 0 1rem;}
</style>
""", unsafe_allow_html=True)

# ========== 加载数据（修复openpyxl依赖 + 容错处理） ==========
@st.cache_data
def load_all_data():
    try:
        # 核心数据（原有）
        df_core = pd.read_excel("百家姓_项目完整数据.xlsx", engine="openpyxl")
        df_core = df_core[["排名", "姓氏", "起源地", "省份", "人口占比(%)", "姓氏类型", "起源类型"]].copy()
        df_core.rename(columns={"人口占比(%)": "人口占比"}, inplace=True)
        df_core = df_core.dropna(subset=["省份"])
        
        # 新增：前300名数据（容错）
        try:
            df_top300 = pd.read_excel("2026 中国姓氏前300名排名 + 人口（万人）+ 占比（%）.xlsx", engine="openpyxl")
            df_top300.columns = ["排名_300", "姓氏_300", "人口_万人", "占比_300%"]
            # 清理数据（避免空值/非数值）
            df_top300["人口_万人"] = pd.to_numeric(df_top300["人口_万人"], errors='coerce').fillna(0)
        except FileNotFoundError:
            df_top300 = pd.DataFrame()
        
        # 新增：郡望堂号数据（容错）
        try:
            df_culture = pd.read_excel("完整姓氏 - 郡望 - 今地 - 堂号总表.xlsx", engine="openpyxl")
        except FileNotFoundError:
            df_culture = pd.DataFrame()
            
        return df_core, df_top300, df_culture
    except FileNotFoundError as e:
        st.error(f"❌ 核心Excel文件未找到：{e.filename}")
        st.stop()
    except Exception as e:
        st.error(f"❌ 数据加载失败：{str(e)}")
        st.stop()

df, df_top300, df_culture = load_all_data()

# ========== 标题与筛选控件 ==========
st.title("🏮 中国百家姓起源地可视化")
st.divider()

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

st.info(f"当前筛选结果：共 {len(df_filtered)} 个姓氏（总数据：{len(df)} 个）")
st.divider()

# ========== 地图可视化（优化缩放） ==========
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
    color="#9c2c1a",
    zoom=4 if province == "全部" else 7
)
st.divider()

# ========== 柱状图（优化尺寸 + 修复字体） ==========
st.subheader("📊 姓氏人口占比Top10")
df_top10 = df_filtered.sort_values("人口占比", ascending=False).head(10)

# 优化图表尺寸（从10,5改为8,4，更适配页面）
fig, ax = plt.subplots(figsize=(8, 4), dpi=100)  # dpi=100保证清晰度且不超尺寸
colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(df_top10)))
bars = ax.bar(
    df_top10["姓氏"],
    df_top10["人口占比"],
    color=colors,
    edgecolor="#9c2c1a",
    linewidth=1
)

# 字体配置（兼容服务器）
ax.set_xlabel("姓氏", fontproperties=font_prop, fontsize=10, color="#333")
ax.set_ylabel("人口占比(%)", fontproperties=font_prop, fontsize=10, color="#333")
ax.set_title(f"{'全国' if province == '全部' else province} 姓氏人口占比Top10", 
             fontproperties=font_prop, fontsize=12, color="#9c2c1a", pad=10)
ax.set_facecolor("#f8f1e3")
fig.patch.set_facecolor("#f8f1e3")

ax.grid(True, axis="y", alpha=0.3, color="#9c2c1a")
ax.set_axisbelow(True)
ax.tick_params(axis="x", colors="#333", rotation=45, labelsize=9)
ax.tick_params(axis="y", colors="#333", labelsize=9)

# 刻度标签字体
for label in ax.get_xticklabels():
    label.set_fontproperties(font_prop)
for label in ax.get_yticklabels():
    label.set_fontproperties(font_prop)

# 数值标签
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width()/2.,
        height + 0.05,
        f"{height:.2f}%",
        ha="center", va="bottom", color="#9c2c1a", fontsize=8,
        fontproperties=font_prop
    )
st.pyplot(fig)
st.divider()

# ========== 饼图（优化尺寸 + 修复字体） ==========
st.subheader("🥧 姓氏类型 & 起源类型分布")
col_pie1, col_pie2 = st.columns(2)

with col_pie1:
    type_counts = df_filtered["姓氏类型"].value_counts()
    fig1, ax1 = plt.subplots(figsize=(5, 4), dpi=100)  # 缩小尺寸
    colors1 = ["#9c2c1a", "#d2b48c"]
    wedges, texts, autotexts = ax1.pie(
        type_counts.values,
        labels=type_counts.index,
        autopct="%1.1f%%",
        colors=colors1,
        startangle=90,
        textprops={"fontproperties": font_prop, "color": "#333", "fontsize": 9}
    )
    for autotext in autotexts:
        autotext.set_color("#fff")
        autotext.set_fontweight("bold")
        autotext.set_fontproperties(font_prop)
    ax1.set_title("单姓/复姓占比", fontproperties=font_prop, fontsize=11, color="#9c2c1a", pad=10)
    fig1.patch.set_facecolor("#f8f1e3")
    st.pyplot(fig1)

with col_pie2:
    origin_counts = df_filtered["起源类型"].value_counts()
    fig2, ax2 = plt.subplots(figsize=(5, 4), dpi=100)  # 缩小尺寸
    colors2 = plt.cm.Set3(np.linspace(0, 1, len(origin_counts)))
    wedges2, texts2, autotexts2 = ax2.pie(
        origin_counts.values,
        labels=origin_counts.index,
        autopct="%1.1f%%",
        colors=colors2,
        startangle=90,
        textprops={"fontproperties": font_prop, "color": "#333", "fontsize": 8}
    )
    for autotext in autotexts2:
        autotext.set_color("#fff")
        autotext.set_fontweight("bold")
        autotext.set_fontproperties(font_prop)
    ax2.set_title("起源类型占比", fontproperties=font_prop, fontsize=11, color="#9c2c1a", pad=10)
    fig2.patch.set_facecolor("#f8f1e3")
    st.pyplot(fig2)

st.divider()

# ========== 前300名人口对比（优化尺寸 + 修复弃用警告） ==========
if not df_top300.empty:
    st.subheader("📈 前300名姓氏人口对比")
    rank_range = st.slider("选择排名区间", 1, 300, (1, 50))
    df_rank = df_top300[(df_top300["排名_300"] >= rank_range[0]) & (df_top300["排名_300"] <= rank_range[1])]

    # 优化图表尺寸（从8,4改为7,3.5）
    fig, ax = plt.subplots(figsize=(7, 3.5), dpi=100)
    colors = plt.cm.Reds(np.linspace(0.4, 0.8, len(df_rank)))
    bars = ax.bar(df_rank["姓氏_300"], df_rank["人口_万人"], color=colors, edgecolor="#9c2c1a")

    ax.set_title("姓氏人口对比", fontproperties=font_prop, color="#9c2c1a", fontsize=11)
    ax.set_ylabel("人口（万人）", fontproperties=font_prop, color="#5c2c21", fontsize=9)
    ax.set_facecolor("#f8f1e3")
    fig.patch.set_facecolor("#f8f1e3")
    
    # 刻度标签
    for label in ax.get_xticklabels():
        label.set_fontproperties(font_prop)
        label.set_fontsize(8)  # 缩小字体避免重叠
    for label in ax.get_yticklabels():
        label.set_fontproperties(font_prop)
        label.set_fontsize(8)

    # 数值标签（优化位置）
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x()+bar.get_width()/2, h+50, f"{int(h)}万", 
                ha="center", color="#9c2c1a", fontproperties=font_prop, fontsize=7)

    st.pyplot(fig)
    st.dataframe(df_top300, width='stretch')  # 修复use_container_width弃用警告
    st.divider()

# ========== 郡望堂号查询（修复弃用警告） ==========
if not df_culture.empty:
    st.subheader("🏯 姓氏郡望·堂号查询")
    search = st.text_input("输入姓氏查询（如：李、王）")
    if search:
        res = df_culture[df_culture["姓氏"].str.contains(search, na=False)]
        if len(res) > 0:
            st.success(f"找到 {len(res)} 条信息")
            st.dataframe(res, width='stretch')
        else:
            st.warning("未找到相关信息")
    else:
        st.dataframe(df_culture.head(20), width='stretch')  # 修复use_container_width弃用警告
    st.divider()

# ========== 数据表格（优化宽度） ==========
st.subheader("📋 当前筛选的姓氏列表")
st.dataframe(df_filtered, width='stretch')

# ========== 操作说明 ==========
st.markdown("""
### 📝 操作说明
1. **筛选功能**：选省份/姓氏类型/起源类型，所有图表实时更新；
2. **数据表格**：底部表格可查看所有筛选后的姓氏详细信息；
3. **图表细节**：柱状图顶部有具体数值，饼图显示百分比。
""")
