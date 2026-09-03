import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="🏏 Cricket Dream Team Selector",
    page_icon="🏏",
    layout="wide"
)

# ── Load data — try multiple path options ──────────────
@st.cache_data
def load_data():
    # Try different possible paths
    paths = [
        ("fact_bating_summary.csv", "fact_bowling_summary.csv", "dim_match_summary.csv", "dim_players_no_images.csv"),
        ("data/fact_bating_summary.csv", "data/fact_bowling_summary.csv", "data/dim_match_summary.csv", "data/dim_players_no_images.csv"),
    ]
    for bat_p, bowl_p, match_p, player_p in paths:
        try:
            batting  = pd.read_csv(bat_p)
            bowling  = pd.read_csv(bowl_p)
            matches  = pd.read_csv(match_p)
            players  = pd.read_csv(player_p)
            return batting, bowling, matches, players
        except:
            continue
    raise FileNotFoundError("Could not find data files. Please ensure CSV files are in the repo root or data/ folder.")

batting, bowling, matches, players = load_data()

# ── Compute batting KPIs ───────────────────────────────
bat_agg = batting.groupby(["batsmanName","teamInnings"]).agg(
    innings    = ("runs", "count"),
    total_runs = ("runs", "sum"),
    total_balls= ("balls","sum"),
    fours      = ("4s",  "sum"),
    sixes      = ("6s",  "sum"),
).reset_index()

bat_agg["avg"]          = (bat_agg["total_runs"] / bat_agg["innings"]).round(2)
bat_agg["strike_rate"]  = ((bat_agg["total_runs"] / bat_agg["total_balls"].replace(0,1)) * 100).round(2)
bat_agg["boundary_pct"] = ((bat_agg["fours"]*4 + bat_agg["sixes"]*6) / bat_agg["total_runs"].replace(0,1) * 100).round(2)
bat_agg.rename(columns={"teamInnings":"team"}, inplace=True)

# ── Compute bowling KPIs ───────────────────────────────
bowl_agg = bowling.groupby(["bowlerName","bowlingTeam"]).agg(
    matches    = ("match",   "count"),
    wickets    = ("wickets", "sum"),
    runs_given = ("runs",    "sum"),
    dot_balls  = ("0s",      "sum"),
    overs_bowl = ("overs",   "sum"),
).reset_index()

bowl_agg["economy"]  = (bowl_agg["runs_given"] / bowl_agg["overs_bowl"].replace(0,1)).round(2)
bowl_agg["dot_pct"]  = (bowl_agg["dot_balls"]  / (bowl_agg["overs_bowl"].replace(0,1)*6) * 100).round(2)
bowl_agg["bowl_sr"]  = (bowl_agg["overs_bowl"]*6 / bowl_agg["wickets"].replace(0,1)).round(2)
bowl_agg.rename(columns={"bowlingTeam":"team"}, inplace=True)

# ══════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════
st.title("🏏 Cricket Dream Team Selector")
st.markdown("### ICC Men's T20 World Cup 2022-23")
st.markdown("*Data-driven player selection — pure performance analytics. Built by Nandan Chandrashekar & Himanshu Ravishankar*")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Matches", len(matches))
col2.metric("Batters Tracked", bat_agg["batsmanName"].nunique())
col3.metric("Bowlers Tracked", bowl_agg["bowlerName"].nunique())
col4.metric("Teams", matches["team1"].nunique() + 2)

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["🏏 Batting", "🎳 Bowling", "📊 Match Results", "⭐ Dream XII"])

# ── TAB 1 — BATTING ───────────────────────────────────
with tab1:
    st.subheader("Batting Performance Analysis")
    c1, c2, c3, c4 = st.columns(4)
    min_inn  = c1.slider("Min innings", 1, 8, 3)
    min_avg  = c2.slider("Min average", 0, 60, 15)
    min_sr   = c3.slider("Min strike rate", 0, 200, 110)
    teams_b  = ["All"] + sorted(bat_agg["team"].dropna().unique().tolist())
    sel_team = c4.selectbox("Team", teams_b, key="b_team")

    fb = bat_agg[(bat_agg["innings"] >= min_inn) & (bat_agg["avg"] >= min_avg) & (bat_agg["strike_rate"] >= min_sr)]
    if sel_team != "All":
        fb = fb[fb["team"] == sel_team]
    fb = fb.sort_values("avg", ascending=False).reset_index(drop=True)
    fb.index += 1

    st.dataframe(
        fb[["batsmanName","team","innings","total_runs","avg","strike_rate","boundary_pct","fours","sixes"]].rename(columns={
            "batsmanName":"Player","team":"Team","innings":"Inn","total_runs":"Runs",
            "avg":"Avg","strike_rate":"SR","boundary_pct":"Boundary%","fours":"4s","sixes":"6s"
        }),
        use_container_width=True
    )

    c1b, c2b = st.columns(2)
    with c1b:
        st.markdown("**Top 10 Run Scorers**")
        st.bar_chart(bat_agg.nlargest(10,"total_runs").set_index("batsmanName")["total_runs"])
    with c2b:
        st.markdown("**Top 10 Strike Rates (min 3 innings)**")
        st.bar_chart(bat_agg[bat_agg["innings"]>=3].nlargest(10,"strike_rate").set_index("batsmanName")["strike_rate"])

# ── TAB 2 — BOWLING ───────────────────────────────────
with tab2:
    st.subheader("Bowling Performance Analysis")
    c1, c2, c3, c4 = st.columns(4)
    min_wkts  = c1.slider("Min wickets", 0, 15, 3)
    max_econ  = c2.slider("Max economy", 4.0, 15.0, 9.0)
    min_dot   = c3.slider("Min dot ball %", 0, 80, 25)
    teams_bw  = ["All"] + sorted(bowl_agg["team"].dropna().unique().tolist())
    sel_team2 = c4.selectbox("Team", teams_bw, key="bw_team")

    fb2 = bowl_agg[(bowl_agg["wickets"] >= min_wkts) & (bowl_agg["economy"] <= max_econ) & (bowl_agg["dot_pct"] >= min_dot)]
    if sel_team2 != "All":
        fb2 = fb2[fb2["team"] == sel_team2]
    fb2 = fb2.sort_values("wickets", ascending=False).reset_index(drop=True)
    fb2.index += 1

    st.dataframe(
        fb2[["bowlerName","team","matches","wickets","economy","bowl_sr","dot_pct"]].rename(columns={
            "bowlerName":"Player","team":"Team","matches":"Matches","wickets":"Wkts",
            "economy":"Economy","bowl_sr":"Bowl SR","dot_pct":"Dot%"
        }),
        use_container_width=True
    )

    c1b, c2b = st.columns(2)
    with c1b:
        st.markdown("**Top 10 Wicket Takers**")
        st.bar_chart(bowl_agg.nlargest(10,"wickets").set_index("bowlerName")["wickets"])
    with c2b:
        st.markdown("**Best Economy (min 3 matches)**")
        st.bar_chart(bowl_agg[bowl_agg["matches"]>=3].nsmallest(10,"economy").set_index("bowlerName")["economy"])

# ── TAB 3 — MATCHES ───────────────────────────────────
with tab3:
    st.subheader("Match Results")
    st.dataframe(
        matches[["matchDate","team1","team2","winner","margin","ground"]].rename(columns={
            "matchDate":"Date","team1":"Team 1","team2":"Team 2",
            "winner":"Winner","margin":"Margin","ground":"Ground"
        }),
        use_container_width=True
    )
    st.markdown("**Wins by Team**")
    st.bar_chart(matches["winner"].value_counts())

# ── TAB 4 — DREAM XII ─────────────────────────────────
with tab4:
    st.subheader("⭐ Build Your Dream XII")

    st.markdown("#### 🏏 Suggested Openers (Avg > 25, SR > 130)")
    openers = bat_agg[(bat_agg["innings"]>=3) & (bat_agg["avg"]>=25) & (bat_agg["strike_rate"]>=130)].nlargest(5,"avg")
    st.dataframe(openers[["batsmanName","team","avg","strike_rate","total_runs"]].rename(columns={
        "batsmanName":"Player","team":"Team","avg":"Avg","strike_rate":"SR","total_runs":"Runs"
    }), use_container_width=True)

    st.markdown("#### 💥 Suggested Power Hitters (SR > 150)")
    power = bat_agg[(bat_agg["innings"]>=2) & (bat_agg["strike_rate"]>=150)].nlargest(5,"strike_rate")
    st.dataframe(power[["batsmanName","team","strike_rate","avg","sixes"]].rename(columns={
        "batsmanName":"Player","team":"Team","strike_rate":"SR","avg":"Avg","sixes":"6s"
    }), use_container_width=True)

    st.markdown("#### 🎳 Suggested Bowlers (Wickets ≥ 5, Economy ≤ 8)")
    bowlers = bowl_agg[(bowl_agg["wickets"]>=5) & (bowl_agg["economy"]<=8)].nlargest(5,"wickets")
    st.dataframe(bowlers[["bowlerName","team","wickets","economy","dot_pct"]].rename(columns={
        "bowlerName":"Player","team":"Team","wickets":"Wkts","economy":"Econ","dot_pct":"Dot%"
    }), use_container_width=True)

    st.divider()
    st.markdown("### 🎯 Pick Your Own Dream XII")
    all_players = sorted(bat_agg["batsmanName"].dropna().unique().tolist())
    selected = st.multiselect("Select up to 12 players:", all_players, max_selections=12)
    if selected:
        st.success(f"Your Dream Team — {len(selected)}/12 selected")
        cols = st.columns(3)
        for i, p in enumerate(selected):
            cols[i % 3].markdown(f"**{i+1}.** {p}")
    elif len(selected) == 0:
        st.info("Select players above to build your Dream XII!")
