import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="🏏 Cricket Dream Team Selector",
    page_icon="🏏",
    layout="wide"
)

# ── Load data ──────────────────────────────────────────
@st.cache_data
def load_data():
    batting  = pd.read_csv("data/fact_bating_summary.csv")
    bowling  = pd.read_csv("data/fact_bowling_summary.csv")
    matches  = pd.read_csv("data/dim_match_summary.csv")
    players  = pd.read_csv("data/dim_players_no_images.csv")
    return batting, bowling, matches, players

batting, bowling, matches, players = load_data()

# ── Compute batting KPIs ───────────────────────────────
bat_agg = batting.groupby("batsmanName").agg(
    innings   = ("runs", "count"),
    total_runs= ("runs", "sum"),
    total_balls=("balls","sum"),
    fours     = ("4s",  "sum"),
    sixes     = ("6s",  "sum"),
    team      = ("teamInnings", "first"),
).reset_index()

bat_agg["avg"]         = (bat_agg["total_runs"] / bat_agg["innings"]).round(2)
bat_agg["strike_rate"] = ((bat_agg["total_runs"] / bat_agg["total_balls"]) * 100).round(2)
bat_agg["boundary_pct"]= ((bat_agg["fours"]*4 + bat_agg["sixes"]*6) / bat_agg["total_runs"].replace(0,1) * 100).round(2)

# ── Compute bowling KPIs ───────────────────────────────
bowl_agg = bowling.groupby("bowlerName").agg(
    innings    = ("match",    "count"),
    wickets    = ("wickets",  "sum"),
    runs_given = ("runs",     "sum"),
    dot_balls  = ("0s",       "sum"),
    total_balls= ("overs",    lambda x: round(x.sum() * 6)),
    team       = ("bowlingTeam","first"),
).reset_index()

bowl_agg["economy"]    = (bowl_agg["runs_given"] / bowl_agg["innings"]).round(2)
bowl_agg["bowl_sr"]    = (bowl_agg["total_balls"] / bowl_agg["wickets"].replace(0,1)).round(2)
bowl_agg["dot_pct"]    = (bowl_agg["dot_balls"]  / bowl_agg["total_balls"].replace(0,1) * 100).round(2)

# ── Merge with player info ─────────────────────────────
bat_agg  = bat_agg.merge(players[["name","playingRole"]], left_on="batsmanName",  right_on="name", how="left").drop(columns="name")
bowl_agg = bowl_agg.merge(players[["name","playingRole"]], left_on="bowlerName", right_on="name", how="left").drop(columns="name")

# ══════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════
st.title("🏏 Cricket Dream Team Selector")
st.markdown("### ICC Men's T20 World Cup 2022-23")
st.markdown("*Data-driven player selection — no bias, pure performance analytics*")
st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["🏏 Batting Analysis", "🎳 Bowling Analysis", "📊 Match Results", "⭐ Dream XII"])

# ── TAB 1 — BATTING ───────────────────────────────────
with tab1:
    st.subheader("Batting Performance")

    col1, col2, col3 = st.columns(3)
    with col1:
        min_innings = st.slider("Min innings played", 1, 8, 3)
    with col2:
        min_avg = st.slider("Min batting average", 0, 60, 20)
    with col3:
        min_sr = st.slider("Min strike rate", 0, 200, 120)

    teams = ["All"] + sorted(bat_agg["team"].dropna().unique().tolist())
    selected_team = st.selectbox("Filter by team", teams, key="bat_team")

    filtered = bat_agg[
        (bat_agg["innings"] >= min_innings) &
        (bat_agg["avg"] >= min_avg) &
        (bat_agg["strike_rate"] >= min_sr)
    ]
    if selected_team != "All":
        filtered = filtered[filtered["team"] == selected_team]

    filtered = filtered.sort_values("avg", ascending=False).reset_index(drop=True)
    filtered.index += 1

    st.dataframe(
        filtered[["batsmanName","team","innings","total_runs","avg","strike_rate","boundary_pct","fours","sixes"]].rename(columns={
            "batsmanName":"Player","team":"Team","innings":"Innings",
            "total_runs":"Runs","avg":"Avg","strike_rate":"SR",
            "boundary_pct":"Boundary%","fours":"4s","sixes":"6s"
        }),
        use_container_width=True
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Top 10 by Runs**")
        st.bar_chart(bat_agg.nlargest(10,"total_runs").set_index("batsmanName")["total_runs"])
    with col_b:
        st.markdown("**Top 10 by Strike Rate (min 3 innings)**")
        top_sr = bat_agg[bat_agg["innings"] >= 3].nlargest(10,"strike_rate")
        st.bar_chart(top_sr.set_index("batsmanName")["strike_rate"])

# ── TAB 2 — BOWLING ───────────────────────────────────
with tab2:
    st.subheader("Bowling Performance")

    col1, col2, col3 = st.columns(3)
    with col1:
        min_wkts = st.slider("Min wickets", 0, 15, 3)
    with col2:
        max_econ = st.slider("Max economy", 4.0, 15.0, 9.0)
    with col3:
        min_dot = st.slider("Min dot ball %", 0, 80, 30)

    teams2 = ["All"] + sorted(bowl_agg["team"].dropna().unique().tolist())
    selected_team2 = st.selectbox("Filter by team", teams2, key="bowl_team")

    filtered2 = bowl_agg[
        (bowl_agg["wickets"] >= min_wkts) &
        (bowl_agg["economy"] <= max_econ) &
        (bowl_agg["dot_pct"] >= min_dot)
    ]
    if selected_team2 != "All":
        filtered2 = filtered2[filtered2["team"] == selected_team2]

    filtered2 = filtered2.sort_values("wickets", ascending=False).reset_index(drop=True)
    filtered2.index += 1

    st.dataframe(
        filtered2[["bowlerName","team","innings","wickets","economy","bowl_sr","dot_pct"]].rename(columns={
            "bowlerName":"Player","team":"Team","innings":"Matches",
            "wickets":"Wkts","economy":"Economy","bowl_sr":"Bowl SR","dot_pct":"Dot%"
        }),
        use_container_width=True
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Top 10 Wicket Takers**")
        st.bar_chart(bowl_agg.nlargest(10,"wickets").set_index("bowlerName")["wickets"])
    with col_b:
        st.markdown("**Top 10 Best Economy (min 3 matches)**")
        top_eco = bowl_agg[bowl_agg["innings"] >= 3].nsmallest(10,"economy")
        st.bar_chart(top_eco.set_index("bowlerName")["economy"])

# ── TAB 3 — MATCH RESULTS ─────────────────────────────
with tab3:
    st.subheader("Match Results — T20 World Cup 2022")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Matches", len(matches))
    with col2:
        most_wins = matches["winner"].value_counts().idxmax()
        st.metric("Most Wins", most_wins)

    st.dataframe(
        matches[["matchDate","team1","team2","winner","margin","ground"]].rename(columns={
            "matchDate":"Date","team1":"Team 1","team2":"Team 2",
            "winner":"Winner","margin":"Margin","ground":"Ground"
        }),
        use_container_width=True
    )

    st.markdown("**Wins by Team**")
    wins = matches["winner"].value_counts()
    st.bar_chart(wins)

# ── TAB 4 — DREAM XII ─────────────────────────────────
with tab4:
    st.subheader("⭐ Select Your Dream XII")
    st.markdown("Use the filters in the Batting and Bowling tabs to identify top performers, then build your team here.")

    st.markdown("#### 🏏 Openers (need SR > 140, Avg > 30)")
    openers = bat_agg[
        (bat_agg["innings"] >= 3) &
        (bat_agg["strike_rate"] >= 140) &
        (bat_agg["avg"] >= 30) &
        (bat_agg["battingPos"] if "battingPos" in bat_agg.columns else True)
    ].nlargest(5, "avg")[["batsmanName","team","avg","strike_rate","total_runs"]]
    st.dataframe(openers.rename(columns={"batsmanName":"Player","team":"Team","avg":"Avg","strike_rate":"SR","total_runs":"Runs"}), use_container_width=True)

    st.markdown("#### 💥 Power Hitters (SR > 150)")
    power = bat_agg[
        (bat_agg["innings"] >= 3) &
        (bat_agg["strike_rate"] >= 150)
    ].nlargest(5,"strike_rate")[["batsmanName","team","strike_rate","avg","sixes"]]
    st.dataframe(power.rename(columns={"batsmanName":"Player","team":"Team","strike_rate":"SR","avg":"Avg","sixes":"6s"}), use_container_width=True)

    st.markdown("#### 🎳 Top Bowlers (Economy < 7.5, Wickets > 5)")
    top_bowlers = bowl_agg[
        (bowl_agg["wickets"] >= 5) &
        (bowl_agg["economy"] <= 7.5)
    ].nlargest(5,"wickets")[["bowlerName","team","wickets","economy","dot_pct"]]
    st.dataframe(top_bowlers.rename(columns={"bowlerName":"Player","team":"Team","wickets":"Wkts","economy":"Econ","dot_pct":"Dot%"}), use_container_width=True)

    st.divider()
    st.markdown("**📌 Build your own Dream XII:**")
    all_players = sorted(bat_agg["batsmanName"].dropna().tolist())
    selected = st.multiselect("Select up to 12 players:", all_players, max_selections=12)
    if selected:
        st.success(f"Your Dream Team ({len(selected)}/12 selected):")
        for i, p in enumerate(selected, 1):
            st.markdown(f"**{i}.** {p}")
