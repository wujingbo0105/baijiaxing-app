import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
import os

# ======================== 1. 全局美化配置 ========================
# 加载字体
font_path = 'SourceHanSerifCN-Bold.otf'
if os.path.exists(font_path):
    font_prop = FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
else:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'PingFang SC']
plt.rcParams['axes.unicode_minus'] = False

# 页面基础美化（自定义主题色+图标+布局）
st.set_page_config(
    page_title="百家姓可视化 | 起源地分布",
    page_icon="🏮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS（核心美化！修改颜色/圆角/阴影/字体大小）
st.markdown("""
    <style>
    /* 全局样式 */
    .stApp {
        background-color: #f8f9fa;
    }
    /* 标题样式 */
    h1, h2, h3, h4 {
        color: #2c3e50;
        font-weight: 600;
    }
    /* 卡片/容器样式 */
    .stContainer {
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        background-color: white;
        margin-bottom: 1rem;
    }
    /* 按钮/筛选框样式 */
    div[data-baseweb="select"] {
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    /* 信息提示框 */
    .stAlert {
        border-radius: 8px;
        border: none;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    /* 分割线 */
    hr {
        border: none;
        height: 1px;
        background-color: #e9ecef;
        margin: 1.5rem 0;
    }
    /* 表格样式 */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ======================== 2. 加载数据（移到筛选控件前面！） ========================
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("百家姓_项目完整数据.xlsx")
        df = df[["排名", "姓氏", "起源地", "省份", "人口占比(%)", "姓氏类型", "起源类型"]].copy()
        df.rename(columns={"人口占比(%)": "人口占比"}, inplace=True)
        return df.dropna(subset=["省份"])
    except FileNotFoundError:
        st.error("❌ 未找到Excel文件！请确保Excel文件和代码在同一个文件夹。")
        st.stop()

df = load_data()  # 这里先定义df，后面才能用

# ======================== 3. 顶部标题+副标题 ========================
st.markdown("<h1 style='text-align: center; margin-bottom: 0.5rem;'>🏮 中国百家姓起源地可视化</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6c757d; font-size: 16px; margin-bottom: 2rem;'>基于省份/类型的实时筛选 & 数据可视化分析</p>", unsafe_allow_html=True)

# ======================== 4. 筛选区美化（现在df已经定义好了，不会报错） ========================
with st.container():
    st.markdown("<h3 style='margin-bottom: 1rem;'>🔍 数据筛选</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1], gap="large")

    with col1:
        province = st.selectbox(
            "选择省份",
            options=["全部"] + sorted(df["省份"].unique()),
            index=0,
            label_visibility="collapsed"
        )
        st.markdown("<p style='font-size: 14px; color: #6c757d; margin-top: -0.5rem;'>📍 省份</p>", unsafe_allow_html=True)

    with col2:
        surname_type = st.selectbox(
            "选择姓氏类型",
            options=["全部"] + sorted(df["姓氏类型"].unique()),
            index=0,
            label_visibility="collapsed"
        )
        st.markdown("<p style='font-size: 14px; color: #6c757d; margin-top: -0.5rem;'>👤 姓氏类型</p>", unsafe_allow_html=True)

    with col3:
        origin_type = st.selectbox(
            "选择起源类型",
            options=["全部"] + sorted(df["起源类型"].unique()),
            index=0,
            label_visibility="collapsed"
        )
        st.markdown("<p style='font-size: 14px; color: #6c757d; margin-top: -0.5rem;'>🌱 起源类型</p>", unsafe_allow_html=True)

# 筛选结果提示
df_filtered = df.copy()
if province != "全部":
    df_filtered = df_filtered[df_filtered["省份"] == province]
if surname_type != "全部":
    df_filtered = df_filtered[df_filtered["姓氏类型"] == surname_type]
if origin_type != "全部":
    df_filtered = df_filtered[df_filtered["起源类型"] == origin_type]

st.success(f"📊 筛选结果：共 <b>{len(df_filtered)}</b> 个姓氏（总数据：438个）", unsafe_allow_html=True)
st.divider()

# ======================== 5. 地图模块 ========================
with st.container():
    st.markdown("<h3 style='margin-bottom: 1rem;'>🗺️ 姓氏起源地分布</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 14px; color: #6c757d; margin-bottom: 1rem;'>📍 圆点大小 = 人口占比 | 点击省份筛选后地图会自动放大</p>", unsafe_allow_html=True)
    
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
        color="#2e86ab",
        zoom=4 if province == "全部" else 7
    )
st.divider()

# ======================== 6. 图表模块 ========================
col_chart1, col_chart2 = st.columns([2,1], gap="large")

# 柱状图
with col_chart1:
    with st.container():
        st.markdown("<h3 style='margin-bottom: 1rem;'>📊 姓氏人口占比Top10</h3>", unsafe_allow_html=True)
        df_top10 = df_filtered.sort_values("人口占比", ascending=False).head(10)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = plt.cm.SkyBlue(np.linspace(0.5, 0.9, len(df_top10)))
        bars = ax.bar(
            df_top10["姓氏"],
            df_top10["人口占比"],
            color=colors,
            edgecolor="#2e86ab",
            linewidth=1.5,
            border_radius=8
        )
        
        ax.set_xlabel("姓氏", fontproperties=font_prop, fontsize=12, color="#2c3e50")
        ax.set_ylabel("人口占比(%)", fontproperties=font_prop, fontsize=12, color="#2c3e50")
        ax.set_title(f"{'全国' if province == '全部' else province} 姓氏人口占比Top10", 
                    fontproperties=font_prop, fontsize=14, color="#2c3e50", pad=15)
        ax.set_facecolor("white")
        fig.patch.set_facecolor("white")
        
        ax.grid(True, axis="y", alpha=0.2, color="#cccccc", linestyle="--")
        ax.set_axisbelow(True)
        ax.tick_params(axis="x", colors="#2c3e50", rotation=45, labelsize=10)
        ax.tick_params(axis="y", colors="#2c3e50", labelsize=10)
        
        for label in ax.get_xticklabels():
            label.set_fontproperties(font_prop)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2.,
                height + 0.05,
                f"{height:.2f}%",
                ha="center", va="bottom", color="#2e86ab", fontsize=9, fontweight=600
            )
        st.pyplot(fig)

# 饼图
with col_chart2:
    with st.container():
        st.markdown("<h3 style='margin-bottom: 1rem;'>🥧 类型分布</h3>", unsafe_allow_html=True)
        
        # 姓氏类型饼图
        type_counts = df_filtered["姓氏类型"].value_counts()
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        colors1 = ["#2e86ab", "#e67e22"]
        wedges, texts, autotexts = ax1.pie(
            type_counts.values,
            labels=type_counts.index,
            autopct="%1.1f%%",
            colors=colors1,
            startangle=90,
            textprops={"fontproperties": font_prop, "color": "#2c3e50", "fontsize": 11}
        )
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")
            autotext.set_fontsize(10)
        ax1.set_title("单姓/复姓占比", fontproperties=font_prop, fontsize=12, color="#2c3e50", pad=10)
        ax1.set_facecolor("white")
        fig1.patch.set_facecolor("white")
        st.pyplot(fig1)
        
        # 起源类型饼图
        origin_counts = df_filtered["起源类型"].value_counts()
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        colors2 = plt.cm.Pastel1(np.linspace(0, 1, len(origin_counts)))
        wedges2, texts2, autotexts2 = ax2.pie(
            origin_counts.values,
            labels=origin_counts.index,
            autopct="%1.1f%%",
            colors=colors2,
            startangle=90,
            textprops={"fontproperties": font_prop, "color": "#2c3e50", "fontsize": 10}
        )
        for autotext in autotexts2:
            autotext.set_color("white")
            autotext.set_fontweight("bold")
            autotext.set_fontsize(9)
        ax2.set_title("起源类型占比", fontproperties=font_prop, fontsize=12, color="#2c3e50", pad=10)
        ax2.set_facecolor("white")
        fig2.patch.set_facecolor("white")
        st.pyplot(fig2)

st.divider()

# ======================== 7. 数据表格 ========================
with st.container():
    st.markdown("<h3 style='margin-bottom: 1rem;'>📋 姓氏详细列表</h3>", unsafe_allow_html=True)
    st.dataframe(
        df_filtered[["排名", "姓氏", "起源地", "省份", "人口占比", "起源类型"]],
        use_container_width=True,
        column_config={
            "排名": st.column_config.NumberColumn("排名", width="small"),
            "姓氏": st.column_config.TextColumn("姓氏", width="small"),
            "起源地": st.column_config.TextColumn("起源地", width="medium"),
            "省份": st.column_config.TextColumn("省份", width="small"),
            "人口占比": st.column_config.NumberColumn("人口占比(%)", format="%.2f", width="small"),
            "起源类型": st.column_config.TextColumn("起源类型", width="medium"),
        },
        hide_index=True
    )

# ======================== 8. 底部说明 ========================
st.markdown("""
<div style='background-color: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-top: 2rem;'>
    <h4 style='color: #2c3e50; margin-bottom: 1rem;'>📝 操作说明</h4>
    <ul style='color: #6c757d; line-height: 1.8; font-size: 14px;'>
        <li>筛选功能：选择省份/姓氏类型/起源类型，所有图表会<strong>实时更新</strong>；</li>
        <li>地图交互：点击地图可放大/缩小，圆点大小代表该姓氏的人口占比；</li>
        <li>图表细节：柱状图顶部显示具体数值，饼图显示百分比占比；</li>
        <li>数据表格：可排序/筛选，支持复制/导出数据。</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# 底部版权
st.markdown("<p style='text-align: center; color: #adb5bd; font-size: 12px; margin-top: 2rem;'>© 2025 百家姓可视化项目 | 数据来源：百家姓统计库</p>", unsafe_allow_html=True)
