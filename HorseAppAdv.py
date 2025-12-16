#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

##################################################################################

st.set_page_config(page_title="Horse Racing Dashboard", layout="wide", page_icon="🏇")

# ---------------------------
# Initialize session state
# ---------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'country'

if 'country' not in st.session_state:
    st.session_state.country = None

# ---------------------------
# Functions
# ---------------------------
def go_to_dashboard():
    if st.session_state.country:  # make sure country is selected
        st.session_state.page = 'dashboard'

def go_back_to_country():
    st.session_state.page = 'country_selection'

# ---------------------------
# Page rendering
# ---------------------------

if st.session_state.page == "country":

    st.title("🐎 Horse Racing Dashboard")
    st.subheader("Select a Country")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🇿🇦 South Africa"):
            st.session_state.country = "South Africa"
            st.session_state.page = "dashboard"

    with col2:
        if st.button("🇭🇰 Hong Kong"):
            st.session_state.country = "Hong Kong"
            st.session_state.page = "dashboard"

    with col3:
        if st.button("🇲🇾 Malaysia"):
            st.session_state.country = "Malaysia"
            st.session_state.page = "dashboard"


elif st.session_state.page == "dashboard":

    country = st.session_state.country
    st.header(f"🏁 {country} Horse Racing Dashboard")

    if st.button("⬅️ Back to Country Selection"):
        st.session_state.page = "country"
        st.session_state.country = None


####################################################################################


# -----------------------------
# Session state for country selection
# -----------------------------
# if "country" not in st.session_state:
#     st.session_state.country = None

# -----------------------------
# Country selection front page
# -----------------------------
if st.session_state.country is None:
    st.title("🐎 Horse Racing Dashboard")
    st.subheader("Select a Country")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🇿🇦 South Africa"):
            st.session_state.country = "South Africa"

    with col2:
        if st.button("🇭🇰 Hong Kong"):
            st.session_state.country = "Hong Kong"

    with col3:
        if st.button("🇲🇾 Malaysia"):
            st.session_state.country = "Malaysia"

# -----------------------------
# Load country-specific dashboard
# -----------------------------
else:
    country = st.session_state.country
    st.header(f"🏁 {country} Horse Racing Dashboard")

    # Map country to CSV files

    files = {
        "South Africa": ("sa_race_data.csv", "sa_horse_result.csv"),
        "Hong Kong": ("hk_race_data.csv", "hk_horse_result.csv"),
        "Malaysia": ("mal_race_data.csv", "mal_horse_result.csv"),
    }

    data_file, result_file = files[country]

    @st.cache_data
    def load_data(data_file, result_file):
        hist = pd.read_csv(data_file, dtype=str)
        daily = pd.read_csv(result_file, dtype=str)
        return hist, daily

    hist, daily = load_data(data_file, result_file)

    # 👉 Your charts go here
    
   ##################################################### 
    
#####################################################################
        # HISTORICAL
        if "RaceDate" in hist.columns:
            hist["RaceDate"] = pd.to_datetime(hist["RaceDate"], errors="coerce", dayfirst=True)
        else:
            hist["RaceDate"] = pd.NaT
        hist["Placing"] = pd.to_numeric(hist.get("Placing", pd.NA), errors="coerce")
        hist = hist.rename(columns={"HorseName": "Horse"})
        hist["Jockey"] = hist.get("Jockey", None)

        # DAILY
        daily = daily.rename(columns={"HorseName": "Horse"})
        daily["Jockey"] = daily.get("Jockey", None)
        daily["P_top3"] = pd.to_numeric(daily.get("1", daily.get("P_top3", pd.NA)), errors="coerce")
        daily["P_not_top3"] = pd.to_numeric(daily.get("0", daily.get("P_not_top3", pd.NA)), errors="coerce")
        daily["PredictedTop3"] = pd.to_numeric(daily.get("Top3_Prediction", daily.get("PredictedTop3", pd.NA)), errors="coerce")

        return hist, daily

    try:
        hist_df, daily_df = load_data(data_file, result_file)
    except Exception as e:
        st.error(f"Error loading {country} files: {e}")
        st.stop()

    # -------------------------
    # Tabs
    # -------------------------
    tab_today, tab_history = st.tabs(["📅 Today's Race", "📚 Historical Analysis"])

    # -------------------------
    # Sidebar filters
    # -------------------------
    st.sidebar.header(f"📌 {country} Filters")
    race_numbers = sorted(daily_df["RaceNumber"].dropna().unique().tolist())
    selected_race = st.sidebar.selectbox("Select Race Number:", race_numbers)

    sel_horse = st.sidebar.selectbox("Horse", ["All"] + sorted(hist_df["Horse"].dropna().unique()))
    sel_jockey = st.sidebar.selectbox("Jockey", ["All"] + sorted(hist_df["Jockey"].dropna().unique()))
    sel_track = st.sidebar.selectbox("Track", ["All"] + sorted(hist_df["Track"].dropna().unique()))
    sel_distance = st.sidebar.selectbox("Distance", ["All"] + sorted(hist_df["Distance"].dropna().unique()))
    sel_class = st.sidebar.selectbox("Class", ["All"] + sorted(hist_df["Class"].dropna().unique()))

    # =========================
    # TAB 1 — Today's Race
    # =========================
    with tab_today:
        st.header("📅 Today's Race — Predictions & Top 3 Grid")

        daily_race_df = daily_df[daily_df["RaceNumber"] == selected_race].copy()
        if daily_race_df.empty:
            st.warning("No records found for the selected race.")
        else:
            selected_track = daily_race_df["Track"].iloc[0] if "Track" in daily_race_df.columns else None
            selected_class = daily_race_df["Class"].iloc[0] if "Class" in daily_race_df.columns else None
            selected_distance = daily_race_df["Distance"].iloc[0] if "Distance" in daily_race_df.columns else None

            st.markdown(f"**Track:** {selected_track} | **Class:** {selected_class} | **Distance:** {selected_distance}")

            st.subheader("Key Metrics — Today")
            total_horses = daily_race_df["Horse"].nunique()
            prob_col = "P_top3" if "P_top3" in daily_race_df.columns else "PredictedTop3"
            avg_probs = daily_race_df.groupby("Horse")[prob_col].mean().reset_index(name="avg_prob")
            top_prob_row = avg_probs.sort_values("avg_prob", ascending=False).iloc[0]
            highest_prob_text = f"{top_prob_row['Horse']} ({top_prob_row['avg_prob']:.2f})"
            avg_top3_prob = avg_probs["avg_prob"].mean()
            top_jockey_row = daily_race_df.groupby("Jockey")[prob_col].mean().reset_index(name="avg_prob").sort_values("avg_prob", ascending=False).iloc[0]
            top_jockey_text = f"{top_jockey_row['Jockey']} ({top_jockey_row['avg_prob']:.2f})"

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Horses Today", total_horses)
            c2.metric("Highest Prob Horse", highest_prob_text)
            c3.metric("Top Jockey (avg prob)", top_jockey_text)
            c4.metric("Avg Top3 Prob (horse avg)", f"{avg_top3_prob:.2f}")

            st.markdown("---")

            # Overlayed charts
            st.subheader("📊 Probability vs Historical Top 3 per Year")
            charts_per_row = st.slider("Charts per Row", min_value=1, max_value=4, value=2)
            horses_today = daily_race_df["Horse"].dropna().unique().tolist()

            for i in range(0, len(horses_today), charts_per_row):
                cols = st.columns(charts_per_row)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx >= len(horses_today):
                        break
                    horse = horses_today[idx]
                    today_sub = daily_race_df[daily_race_df["Horse"] == horse]
                    jockeys_today = today_sub["Jockey"].dropna().unique().tolist()
                    for jockey in jockeys_today:
                        with col:
                            st.markdown(f"**{horse} — {jockey}**")
                            prob_value = today_sub[today_sub["Jockey"]==jockey][prob_col].values[0] if prob_col in today_sub.columns else 0
                            hist_sub = hist_df[(hist_df["Horse"]==horse) & (hist_df["Jockey"]==jockey)]
                            if "Placing" in hist_sub.columns:
                                hist_top3 = hist_sub[hist_sub["Placing"]<=3].copy()
                                hist_top3["Year"] = hist_top3["RaceDate"].dt.year
                                year_counts = hist_top3.groupby("Year").size().reset_index(name="Top3Count").sort_values("Year")
                            else:
                                year_counts = pd.DataFrame(columns=["Year","Top3Count"])

                            if year_counts.empty:
                                year_counts = pd.DataFrame({"Year":[1], "Top3Count":[0]})
#####################################################################################################
                            fig = go.Figure()

                            # Historical Top3 per year
                            fig.add_trace(go.Bar(
                                x=year_counts["Year"],
                                y=year_counts["Top3Count"],
                                name="Historical Top3",
                                marker_color="orange",
                                opacity=0.6,
                                text=year_counts["Top3Count"],
                                textposition="outside",
                                texttemplate="%{text}",  # force text to show
                                cliponaxis=False          # allow text to go above axis if needed
                            ))

                            # Today's probability (same x-axis)
                            fig.add_trace(go.Bar(
                                x=year_counts["Year"],
                                y=[prob_value]*len(year_counts),
                                name="Today's Prob",
                                marker_color="blue",
                                opacity=0.6,
                                text=[f"{prob_value:.2f}"]*len(year_counts),
                                textposition="outside",
                                texttemplate="%{text}",
                                cliponaxis=False
                            ))

                            fig.update_layout(
                                barmode="overlay",
                                title=f"{horse} — {jockey}: Today's Prob vs Historical Top3",
                                xaxis_title="Year",
                                yaxis_title="Count / Probability",
                                height=300,
                                margin=dict(l=10, r=10, t=35, b=10)
                            )

                            st.plotly_chart(fig, use_container_width=True)


######################################################################################################
#                             fig = go.Figure()
#                             fig.add_trace(go.Bar(
#                                 x=year_counts["Year"],
#                                 y=year_counts["Top3Count"],
#                                 name="Historical Top3",
#                                 marker_color="orange",
#                                 opacity=0.6,
#                                 text=year_counts["Top3Count"],
#                                 textposition="outside"
#                             ))
#                             fig.add_trace(go.Bar(
#                                 x=year_counts["Year"],
#                                 y=[prob_value]*len(year_counts),
#                                 name="Today's Prob",
#                                 marker_color="blue",
#                                 opacity=0.6,
#                                 text=[f"{prob_value:.2f}"]*len(year_counts),
#                                 textposition="outside"
#                             ))
#                             fig.update_layout(
#                                 barmode="overlay",
#                                 title=f"{horse} — {jockey}: Today's Prob vs Historical Top3",
#                                 xaxis_title="Year",
#                                 yaxis_title="Count / Probability",
#                                 height=300,
#                                 margin=dict(l=10,r=10,t=35,b=10)
#                             )
#                             st.plotly_chart(fig, use_container_width=True)

    # =========================
    # TAB 2 — Historical Analysis
    # =========================
    with tab_history:
        st.header("📚 Historical Analysis — Full Data")

        hist_filtered = hist_df.copy()
        if sel_horse!="All": hist_filtered = hist_filtered[hist_filtered["Horse"]==sel_horse]
        if sel_jockey!="All": hist_filtered = hist_filtered[hist_filtered["Jockey"]==sel_jockey]
        if sel_track!="All": hist_filtered = hist_filtered[hist_filtered["Track"]==sel_track]
        if sel_distance!="All": hist_filtered = hist_filtered[hist_filtered["Distance"]==sel_distance]
        if sel_class!="All": hist_filtered = hist_filtered[hist_filtered["Class"]==sel_class]

        total_records = len(hist_filtered)
        total_wins = int((hist_filtered["Placing"]==1).sum()) if "Placing" in hist_filtered.columns else 0
        top_jockey_row = hist_filtered[hist_filtered["Placing"]==1].groupby("Jockey").size().reset_index(name="Wins").sort_values("Wins",ascending=False)
        top_jockey = f"{top_jockey_row.iloc[0]['Jockey']} ({top_jockey_row.iloc[0]['Wins']})" if not top_jockey_row.empty else "-"
        top_horse_row = hist_filtered[hist_filtered["Placing"]==1].groupby("Horse").size().reset_index(name="Wins").sort_values("Wins",ascending=False)
        top_horse = f"{top_horse_row.iloc[0]['Horse']} ({top_horse_row.iloc[0]['Wins']})" if not top_horse_row.empty else "-"

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Records", total_records)
        k2.metric("Total Wins", total_wins)
        k3.metric("Top Jockey", top_jockey)
        k4.metric("Top Horse", top_horse)

        st.markdown("---")
        st.subheader("🏆 Wins by Jockey")
        if not hist_filtered.empty and "Placing" in hist_filtered.columns:
            wins_jockey = hist_filtered[hist_filtered["Placing"]==1].groupby("Jockey").size().reset_index(name="Wins")
            if not wins_jockey.empty:
                fig = px.bar(wins_jockey, x="Jockey", y="Wins", title="Wins by Jockey")
                st.plotly_chart(fig, use_container_width=True)

        st.subheader("🐎 Wins by Horse")
        if not hist_filtered.empty and "Placing" in hist_filtered.columns:
            wins_horse = hist_filtered[hist_filtered["Placing"]==1].groupby("Horse").size().reset_index(name="Wins")
            if not wins_horse.empty:
                fig = px.bar(wins_horse, x="Horse", y="Wins", title="Wins by Horse")
                st.plotly_chart(fig, use_container_width=True)

        st.subheader("📈 Yearly Wins Trend")
        if "RaceDate" in hist_filtered.columns and not hist_filtered["RaceDate"].isna().all() and "Placing" in hist_filtered.columns:
            hist_filtered["Year"] = hist_filtered["RaceDate"].dt.year
            yearly = hist_filtered[hist_filtered["Placing"]==1].groupby("Year").size().reset_index(name="Wins").sort_values("Year")
            if not yearly.empty:
                fig = px.line(yearly, x="Year", y="Wins", markers=True, title="Yearly Wins")
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("Sample Records")
        st.dataframe(hist_filtered.head(200))

    st.markdown("""
    ---
    **Disclaimer:** This app is for informational and entertainment purposes only. No guarantee of accuracy is provided.
    """)





