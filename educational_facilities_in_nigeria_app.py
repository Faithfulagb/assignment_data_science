
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Nigeria Education Dashboard", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117;
        color: white;
    }

    section[data-testid="stSidebar"] {
        background-color: #0e1117 !important;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    header[data-testid="stHeader"] {
        background-color: #0e1117 !important;
    }

    div[data-baseweb="select"] * {
        color: black !important;
    }

    .stDownloadButton > button {
        background-color: #1f77b4;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
    }

    .stDownloadButton > button:hover {
        background-color: #125a8a;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

PRIMARY_COLOR = "#1f77b4"
SECONDARY_COLOR = "#ff7f0e"
ACCENT_COLOR = "#2ca02c"

df = pd.read_csv("educational-facilities-in-nigeria.csv", encoding="latin-1")

bool_cols = ["improved_water_supply", "improved_sanitation", "phcn_electricity"]

for col in bool_cols:
    df[col] = df[col].astype(str).str.lower().map({
        "true": True, "yes": True, "1": True,
        "false": False, "no": False, "0": False
    })

df[bool_cols] = df[bool_cols].fillna(False)

df["phcn_electricity"] = df["phcn_electricity"].map({True: "Yes", False: "No"})
df["improved_water_supply"] = df["improved_water_supply"].map({True: "Yes", False: "No"})


st.sidebar.header("🔎 Filters")

facility = st.sidebar.multiselect(
    "Facility Type",
    df["facility_type_display"].dropna().unique(),
    default=df["facility_type_display"].dropna().unique()
)

management = st.sidebar.multiselect(
    "Management",
    df["management"].dropna().unique(),
    default=df["management"].dropna().unique()
)

lga = st.sidebar.multiselect(
    "LGA",
    df["unique_lga"].dropna().unique(),
    default=df["unique_lga"].dropna().unique()
)

df_filtered = df[
    (df["facility_type_display"].isin(facility)) &
    (df["management"].isin(management)) &
    (df["unique_lga"].isin(lga))
]

st.title("📊 Nigeria Educational Facilities Dashboard")
st.markdown("### Overview of schools, infrastructure, and distribution")

total_students = int(df_filtered["num_students_total"].sum())

st.markdown("## 📌 Key Metrics")

col1, col2, col3, col4, col5 = st.columns([1.2, 1.8, 1.2, 1.2, 1.2])

col1.metric("Total Schools", f"{df_filtered.shape[0]:,}")
col2.metric("Total Students", "{:,}".format(total_students))
col3.metric("Avg Students/School", f"{df_filtered['num_students_total'].mean():.1f}")
col4.metric("Electricity (%)", f"{(df_filtered['phcn_electricity'] == 'Yes').mean()*100:.1f}%")
col5.metric("Water Access (%)", f"{(df_filtered['improved_water_supply'] == 'Yes').mean()*100:.1f}%")

def style_chart(fig):
    fig.update_layout(
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font=dict(color="white"),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

st.markdown("## 📊 School Distribution")

col1, col2 = st.columns(2)

school_type_counts = df_filtered["facility_type_display"].value_counts().reset_index()
school_type_counts.columns = ["facility_type", "count"]

fig1 = px.bar(
    school_type_counts,
    x="facility_type",
    y="count",
    title="Distribution of School Types",
    color_discrete_sequence=[PRIMARY_COLOR]
)

fig1.update_layout(xaxis_tickangle=-45)
fig1 = style_chart(fig1)

col1.plotly_chart(fig1, use_container_width=True)

fig2 = px.histogram(
    df_filtered,
    x="num_students_total",
    nbins=50,
    title="Student Population Distribution",
    color_discrete_sequence=[SECONDARY_COLOR]
)

fig2 = style_chart(fig2)

col2.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# ROW 2
# -----------------------------
st.markdown("## ⚡ Infrastructure & Management")

col1, col2, col3 = st.columns(3)

management_counts = df_filtered["management"].value_counts().reset_index()
management_counts.columns = ["management", "count"]

fig3 = px.bar(
    management_counts,
    x="management",
    y="count",
    title="Schools by Management",
    color_discrete_sequence=[ACCENT_COLOR]
)

fig3 = style_chart(fig3)

col1.plotly_chart(fig3, use_container_width=True)

electricity_counts = df_filtered["phcn_electricity"].value_counts().reset_index()
electricity_counts.columns = ["electricity", "count"]

fig4 = px.pie(
    electricity_counts,
    names="electricity",
    values="count",
    title="Electricity Availability",
    color_discrete_sequence=[PRIMARY_COLOR, "#444"]
)

fig4 = style_chart(fig4)

col2.plotly_chart(fig4, use_container_width=True)

water_counts = df_filtered["improved_water_supply"].value_counts().reset_index()
water_counts.columns = ["water", "count"]

fig5 = px.pie(
    water_counts,
    names="water",
    values="count",
    title="Water Access",
    color_discrete_sequence=[ACCENT_COLOR, "#444"]
)

fig5 = style_chart(fig5)

col3.plotly_chart(fig5, use_container_width=True)

st.markdown("## 🗺️ School Locations")

fig6 = px.scatter_mapbox(
    df_filtered,
    lat="latitude",
    lon="longitude",
    hover_name="facility_name",
    color="management",
    zoom=4,
    height=600,
    color_discrete_sequence=[PRIMARY_COLOR, SECONDARY_COLOR]
)

fig6.update_layout(
    mapbox_style="carto-darkmatter",
    paper_bgcolor="#0e1117"
)

st.plotly_chart(fig6, use_container_width=True)


st.markdown("## 📥 Download Data")

st.download_button(
    "Download Filtered Data",
    df_filtered.to_csv(index=False),
    "filtered_data.csv",
    "text/csv"
)