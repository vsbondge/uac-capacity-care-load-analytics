import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
st.set_page_config(page_title="UAC Care Load Analytics",page_icon="📊",layout="wide")
st.title("System Capacity & Care Load Analytics")
st.caption("Exploratory analysis of reported CBP and HHS care loads; not a direct measure of facility capacity or care quality.")
DEFAULT=Path(__file__).parent/"uac_cleaned_analytics_dataset.csv"
uploaded=st.sidebar.file_uploader("Upload a replacement CSV (optional)",type=["csv"])
@st.cache_data
def load_default(path):
    d=pd.read_csv(path); d["Date"]=pd.to_datetime(d["Date"],errors="coerce"); return d.dropna(subset=["Date"]).sort_values("Date")
if uploaded:
    df=pd.read_csv(uploaded); df["Date"]=pd.to_datetime(df["Date"],errors="coerce")
    for c in df.columns[1:]: df[c]=pd.to_numeric(df[c].astype(str).str.replace(",","",regex=False),errors="coerce")
    df=df.dropna(subset=["Date"]).sort_values("Date")
else: df=load_default(str(DEFAULT))
cbp="Children in CBP custody"; hhs="Children in HHS Care"
transfer="Children transferred out of CBP custody"; discharge="Children discharged from HHS Care"
required=[cbp,hhs,transfer,discharge]
missing=[c for c in required if c not in df.columns]
if missing: st.error("Missing columns: "+", ".join(missing)); st.stop()
for c in required: df[c]=pd.to_numeric(df[c].astype(str).str.replace(",","",regex=False),errors="coerce")
df["Total System Load"]=df[cbp]+df[hhs]; df["Net HHS Intake"]=df[transfer]-df[discharge]
min_d,max_d=df.Date.min().date(),df.Date.max().date()
date_range=st.sidebar.date_input("Reporting date range",value=(min_d,max_d),min_value=min_d,max_value=max_d)
view=df.copy()
if isinstance(date_range,tuple) and len(date_range)==2:
    view=view[(view.Date>=pd.Timestamp(date_range[0]))&(view.Date<=pd.Timestamp(date_range[1]))]
metrics=st.sidebar.multiselect("Load metrics",["CBP custody","HHS care","Total system load"],default=["CBP custody","HHS care","Total system load"])
gran=st.sidebar.selectbox("Time granularity",["Daily","Weekly","Monthly"])
chart=view.copy()
if gran=="Weekly": chart=view.set_index("Date").resample("W").mean(numeric_only=True).reset_index()
elif gran=="Monthly": chart=view.set_index("Date").resample("MS").mean(numeric_only=True).reset_index()
k1,k2,k3,k4=st.columns(4)
avg_total=view["Total System Load"].mean(); avg_net=view["Net HHS Intake"].mean()
k1.metric("Average total load",f"{avg_total:,.0f}" if pd.notna(avg_total) else "N/A")
k2.metric("Average CBP custody",f"{view[cbp].mean():,.0f}" if pd.notna(view[cbp].mean()) else "N/A")
k3.metric("Average HHS care",f"{view[hhs].mean():,.0f}" if pd.notna(view[hhs].mean()) else "N/A")
k4.metric("Average net HHS intake",f"{avg_net:,.1f}" if pd.notna(avg_net) else "N/A",help="Transfers minus discharges; positive means net inflow under this simplified definition.")
st.subheader("Care-load trends")
mp={"CBP custody":cbp,"HHS care":hhs,"Total system load":"Total System Load"}
if metrics:
    long=chart[["Date"]+[mp[m] for m in metrics]].melt("Date",var_name="Metric",value_name="Children")
    long["Metric"]=long["Metric"].replace({cbp:"CBP custody",hhs:"HHS care","Total System Load":"Total system load"})
    st.plotly_chart(px.line(long,x="Date",y="Children",color="Metric",markers=gran!="Daily"),use_container_width=True)
else: st.info("Choose at least one load metric.")
left,right=st.columns(2)
with left:
    st.subheader("Transfers and discharges")
    flows=chart[["Date",transfer,discharge]].melt("Date",var_name="Flow",value_name="Children")
    flows["Flow"]=flows["Flow"].replace({transfer:"Transferred from CBP",discharge:"Discharged from HHS"})
    st.plotly_chart(px.line(flows,x="Date",y="Children",color="Flow"),use_container_width=True)
with right:
    st.subheader("Simplified net HHS intake")
    st.plotly_chart(px.bar(chart,x="Date",y="Net HHS Intake"),use_container_width=True)
st.subheader("Operational indicators")
a,b,c=st.columns(3)
a.metric("Positive net-intake records",f"{(view['Net HHS Intake']>0).mean()*100:.1f}%" if len(view) else "N/A")
b.metric("Peak reported total load",f"{view['Total System Load'].max():,.0f}" if len(view) else "N/A")
c.metric("Reporting records",f"{len(view):,}")
if len(view):
    days=(view.Date.max()-view.Date.min()).days+1
    st.write(f"Selected range: **{len(view):,} records** across **{days:,} calendar days**; **{max(0,days-view.Date.nunique()):,} dates** are not represented.")
st.warning("Reporting dates are irregular. Missing dates are not imputed as zero. Transfers/discharges are flows, while custody/care counts are snapshots. This dashboard cannot establish overcrowding without facility-capacity data.")
st.subheader("Filtered data")
st.dataframe(view,use_container_width=True,hide_index=True)
st.download_button("Download filtered CSV",view.to_csv(index=False).encode("utf-8"),"uac_filtered_data.csv","text/csv")
