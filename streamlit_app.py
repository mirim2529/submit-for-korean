import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# ==============================
# 폰트 설정 (있으면 적용)
# ==============================
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Malgun Gothic"  # 기본 한글 폰트
try:
    import matplotlib.font_manager as fm
    font_path = "/fonts/Pretendard-Bold.ttf"
    fm.fontManager.addfont(font_path)
    plt.rcParams["font.family"] = "Pretendard"
except:
    pass


# ==============================
# Streamlit 기본 설정
# ==============================
st.set_page_config(page_title="해수면 상승 데이터 대시보드", layout="wide")
st.title("🌍 해수면 상승과 기후 변화 대시보드")

st.markdown("""
이 대시보드는 **공식 공개 데이터**와 **보고서 입력 데이터**를 기반으로  
지구 온난화, 해수면 상승, 빙하 질량 변화, 온실가스 배출량을 시각화합니다.  
""")


# ==============================
# 데이터 불러오기 함수
# ==============================
@st.cache_data
def load_global_temp():
    # NASA GISTEMP 데이터
    url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
    try:
        df = pd.read_csv(url, skiprows=1)
        df = df.rename(columns={"Year": "date"})
        df = df[["date", "J-D"]].rename(columns={"J-D": "value"})
        df = df[df["date"] <= datetime.now().year]
        return df
    except:
        st.warning("NASA GISTEMP 데이터를 불러올 수 없어 예시 데이터를 사용합니다.")
        years = np.arange(1990, 2023)
        values = np.linspace(0.2, 1.2, len(years)) + np.random.normal(0, 0.1, len(years))
        return pd.DataFrame({"date": years, "value": values})

@st.cache_data
def load_sea_level():
    # NOAA 해수면 데이터
    url = "https://datahub.io/core/sea-level-rise/r/csiro_recons_gmsl_mo_2015.csv"
    try:
        df = pd.read_csv(url)
        df = df.rename(columns={"Time": "date", "GMSL": "value"})
        df["date"] = pd.to_datetime(df["date"]).dt.year
        df = df.groupby("date")["value"].mean().reset_index()
        df = df[df["date"] <= datetime.now().year]
        return df
    except:
        st.warning("NOAA 해수면 데이터를 불러올 수 없어 예시 데이터를 사용합니다.")
        years = np.arange(1990, 2023)
        values = np.linspace(0, 100, len(years)) + np.random.normal(0, 5, len(years))
        return pd.DataFrame({"date": years, "value": values})


# ==============================
# 데이터 불러오기
# ==============================
temp_df = load_global_temp()
sea_df = load_sea_level()

# 온실가스 배출량 (재현 데이터)
years = np.arange(1990, 2023)
total_emission = np.linspace(300, 750, len(years)) + np.random.normal(0, 20, len(years))
net_emission = total_emission - np.random.normal(30, 5, len(years))
co2_emission = net_emission - np.random.normal(20, 5, len(years))
emission_df = pd.DataFrame({
    "date": years,
    "총배출량": total_emission,
    "순배출량": net_emission,
    "CO2": co2_emission
})


# ==============================
# (공통) 연도 범위 선택 UI
# ==============================
st.sidebar.header("⚙️ 대시보드 설정")

year_min = int(min(temp_df["date"].min(), sea_df["date"].min(), emission_df["date"].min()))
year_max = int(max(temp_df["date"].max(), sea_df["date"].max(), emission_df["date"].max()))

year_range = st.sidebar.slider(
    "연도 범위 선택",
    min_value=year_min,
    max_value=year_max,
    value=(1990, 2020)
)


# ==============================
# (1) 공식 공개 데이터 대시보드
# ==============================
st.header("📊 1. 공식 공개 데이터 대시보드")

filtered_temp = temp_df[(temp_df["date"] >= year_range[0]) & (temp_df["date"] <= year_range[1])]
fig1 = px.line(filtered_temp, x="date", y="value",
               title="지구 평균기온 변화 (NASA GISTEMP)",
               labels={"date": "연도", "value": "평균 온도 편차 (℃)"})
st.plotly_chart(fig1, use_container_width=True)

filtered_sea = sea_df[(sea_df["date"] >= year_range[0]) & (sea_df["date"] <= year_range[1])]
fig2 = px.area(filtered_sea, x="date", y="value",
               title="전 지구 평균 해수면 상승 (NOAA)",
               labels={"date": "연도", "value": "해수면 높이 (mm)"})
st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
**데이터 출처**  
- NASA GISTEMP: https://data.giss.nasa.gov/gistemp  
- NOAA Sea Level: https://datahub.io/core/sea-level-rise  
""")


# ==============================
# (2) 사용자 입력 데이터 대시보드
# ==============================
st.header("📊 2. 사용자 입력 데이터 대시보드")

filtered_emission = emission_df[
    (emission_df["date"] >= year_range[0]) & (emission_df["date"] <= year_range[1])
]

fig3 = px.line(filtered_emission, x="date", y=["총배출량", "순배출량", "CO2"],
               title="국가 온실가스 배출량 추이 (재현 데이터)",
               labels={"date": "연도", "value": "배출량 (백만 tCO₂eq)"})
st.plotly_chart(fig3, use_container_width=True)

csv = filtered_emission.to_csv(index=False).encode("utf-8-sig")
st.download_button("📥 온실가스 배출량 CSV 다운로드", csv, "emission_data.csv", "text/csv")

st.markdown("""
- 위 데이터는 보고서의 이미지 설명을 기반으로 재현한 예시 데이터입니다.  
- 실제 통계는 KOSIS 국가 온실가스 통계에서 확인 가능합니다.  
""")
