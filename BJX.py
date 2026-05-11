import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ======================== 1. 基础配置 ========================
st.set_page_config(
    page_title="百家姓可视化项目",
    page_icon="🏮",
    layout="wide"
)
st.title("🏮 中国百家姓起源地实时可视化")
st.divider()

# ======================== 2. 加载数据 ========================
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

df = load_data()

# ======================== 3. 实时筛选控件 ========================
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

df_filtered = df.copy()
if province != "全部":
    df_filtered = df_filtered[df_filtered["省份"] == province]
if surname_type != "全部":
    df_filtered = df_filtered[df_filtered["姓氏类型"] == surname_type]
if origin_type != "全部":
    df_filtered = df_filtered[df_filtered["起源类型"] == origin_type]

st.info(f"当前筛选结果：共 {len(df_filtered)} 个姓氏（总数据：438个）")
st.divider()

# ======================== 4. 核心图表1：Streamlit 原生地图 ========================
st.subheader("🗺️ 姓氏起源地分布（带省份轮廓）")

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
df_map["经度"] = df_map["省份"].map(lambda x: province_lonlat.get(x, [104.07, 30.67])[0])
df_map["纬度"] = df_map["省份"].map(lambda x: province_lonlat.get(x, [104.07, 30.67])[1])

st.map(
    df_map,
    latitude="纬度",
    longitude="经度",
    size="人口占比",
    color="#0066cc",
    zoom=4 if province == "全部" else 7
)

st.divider()

# ======================== 5. 核心图表2：Top10柱状图（Plotly版） ========================
st.subheader("📊 姓氏人口占比Top10")
df_top10 = df_filtered.sort_values("人口占比", ascending=False).head(10)

fig_bar = px.bar(
    df_top10,
    x="姓氏",
    y="人口占比",
    title=f"{'全国' if province == '全部' else province} 姓氏人口占比Top10",
    color="人口占比",
    color_continuous_scale="Blues",
    labels={"姓氏": "姓氏", "人口占比": "人口占比(%)"},
    text_auto=".2f",  # 显示数值，保留2位小数
)
# 美化样式
fig_bar.update_layout(
    plot_bgcolor="#f0f2f6",
    paper_bgcolor="#f0f2f6",
    font={"family": "SimHei, Microsoft YaHei", "color": "#333"},
    title={"font_size": 16, "color": "#0066cc"},
    xaxis={"tickangle": 45, "title_font_size": 12},
    yaxis={"title_font_size": 12},
)
st.plotly_chart(fig_bar, use_container_width=True)
st.divider()

# ======================== 6. 核心图表3：双饼图（Plotly版） ========================
st.subheader("🥧 姓氏类型 & 起源类型分布")
col_pie1, col_pie2 = st.columns(2)

with col_pie1:
    type_counts = df_filtered["姓氏类型"].value_counts()
    fig_pie1 = px.pie(
        values=type_counts.values,
        names=type_counts.index,
        title="单姓/复姓占比",
        color_discrete_sequence=["#0066cc", "#ff6b6b"],
    )
    fig_pie1.update_layout(
        plot_bgcolor="#f0f2f6",
        paper_bgcolor="#f0f2f6",
        font={"family": "SimHei, Microsoft YaHei", "color": "#333"},
        title={"font_size": 14, "color": "#0066cc"},
    )
    st.plotly_chart(fig_pie1, use_container_width=True)

with col_pie2:
    origin_counts = df_filtered["起源类型"].value_counts()
    fig_pie2 = px.pie(
        values=origin_counts.values,
        names=origin_counts.index,
        title="起源类型占比",
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig_pie2.update_layout(
        plot_bgcolor="#f0f2f6",
        paper_bgcolor="#f0f2f6",
        font={"family": "SimHei, Microsoft YaHei", "color": "#333"},
        title={"font_size": 14, "color": "#0066cc"},
    )
    st.plotly_chart(fig_pie2, use_container_width=True)

st.divider()

# ======================== 7. 补充：数据表格 ========================
st.subheader("📋 当前筛选的姓氏列表")
st.dataframe(
    df_filtered[["排名", "姓氏", "起源地", "省份", "人口占比", "起源类型"]],
    use_container_width=True,
    column_config={
        "排名": st.column_config.NumberColumn("排名"),
        "姓氏": st.column_config.TextColumn("姓氏"),
        "起源地": st.column_config.TextColumn("起源地"),
        "省份": st.column_config.TextColumn("省份"),
        "人口占比": st.column_config.NumberColumn("人口占比(%)", format="%.2f"),
        "起源类型": st.column_config.TextColumn("起源类型"),
    }
)

st.markdown("""
### 📝 操作说明
1. **筛选功能**：选省份/姓氏类型/起源类型，所有图表实时更新；
2. **数据表格**：底部表格可查看所有筛选后的姓氏详细信息；
3. **图表细节**：柱状图顶部有具体数值，饼图显示百分比，点击图例可隐藏/显示对应类别。
""")
