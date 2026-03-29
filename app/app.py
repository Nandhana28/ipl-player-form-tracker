import streamlit as st
import pandas as pd
import ast
import plotly.express as px
import plotly.graph_objects as go
from rapidfuzz import process

st.set_page_config(page_title="IPL Player Form Tracker", layout="wide", page_icon="🏏")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .block-container { padding-top: 2rem; }
    </style>
""", unsafe_allow_html=True)

# ── Load Hadoop output ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    rows = []
    with open(r"D:/Downloads/ipl-player-form-tracker/hadoop_output/part-00000", "r") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 6:
                try:
                    player = parts[0]
                    total_runs = int(parts[1])
                    total_balls = int(parts[2])
                    average = float(parts[3])
                    strike_rate = float(parts[4])
                    last_10 = ast.literal_eval(parts[5])
                    rows.append([player, total_runs, total_balls, average, strike_rate, last_10])
                except:
                    continue
    df = pd.DataFrame(rows, columns=["Player", "Total Runs", "Balls Faced", "Average", "Strike Rate", "Last 10 Innings"])
    return df

@st.cache_data
def load_raw():
    return pd.read_csv(r"D:/Downloads/ipl-player-form-tracker/data/data.csv")

df = load_data()
raw = load_raw()

# ── Header ──────────────────────────────────────────────────────────────────
st.title("IPL Player Form Tracker")
st.caption("Powered by Hadoop MapReduce · IPL 2008–2022")
st.divider()

# ── Player Search Section ───────────────────────────────────────────────────
st.subheader("Player Lookup")
all_players = df["Player"].tolist()

selected_player = st.selectbox(
    "Search for a player",
    options=[""] + all_players,
    index=0,
    key="single_player"
)

if selected_player:
    result = df[df["Player"] == selected_player]
    if not result.empty:
        player = result.iloc[0]

        st.subheader(player["Player"])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Runs", player["Total Runs"])
        col2.metric("Balls Faced", player["Balls Faced"])
        col3.metric("Average", player["Average"])
        col4.metric("Strike Rate", player["Strike Rate"])

        last_10 = player["Last 10 Innings"]
        if last_10:
            st.subheader("Form Curve — Last 10 Innings")
            fig_area = go.Figure()
            fig_area.add_trace(go.Scatter(
                x=list(range(1, len(last_10)+1)),
                y=last_10,
                fill="tozeroy",
                mode="lines+markers",
                line=dict(color="#00d4ff", width=2),
                fillcolor="rgba(0,212,255,0.15)"
            ))
            fig_area.update_layout(
                xaxis_title="Innings", yaxis_title="Runs",
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_area, use_container_width=True)

st.divider()

# ── Player vs Player Comparison ──────────────────────────────────────────────
st.header("Player vs Player Comparison")

col_p1, col_p2 = st.columns(2)

with col_p1:
    player1_name = st.selectbox("Search Player 1", options=[""] + all_players, index=0, key="p1")
with col_p2:
    player2_name = st.selectbox("Search Player 2", options=[""] + all_players, index=0, key="p2")

if player1_name and player2_name:
    p1 = df[df["Player"] == player1_name].iloc[0]
    p2 = df[df["Player"] == player2_name].iloc[0]

    st.subheader(p1["Player"] + " vs " + p2["Player"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Runs", p1["Total Runs"], int(p1["Total Runs"]) - int(p2["Total Runs"]))
    col2.metric("Average", p1["Average"], round(float(p1["Average"]) - float(p2["Average"]), 2))
    col3.metric("Strike Rate", p1["Strike Rate"], round(float(p1["Strike Rate"]) - float(p2["Strike Rate"]), 2))
    col4.metric("Balls Faced", p1["Balls Faced"], int(p1["Balls Faced"]) - int(p2["Balls Faced"]))

    st.subheader("Stats Comparison")
    compare_df = pd.DataFrame({
        "Stat": ["Total Runs", "Average", "Strike Rate", "Balls Faced"],
        p1["Player"]: [p1["Total Runs"], p1["Average"], p1["Strike Rate"], p1["Balls Faced"]],
        p2["Player"]: [p2["Total Runs"], p2["Average"], p2["Strike Rate"], p2["Balls Faced"]]
    })
    fig_compare = go.Figure(data=[
        go.Bar(name=p1["Player"], x=compare_df["Stat"], y=compare_df[p1["Player"]], marker_color="#00d4ff"),
        go.Bar(name=p2["Player"], x=compare_df["Stat"], y=compare_df[p2["Player"]], marker_color="#ff4b4b")
    ])
    fig_compare.update_layout(barmode="group",
                               plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_compare, use_container_width=True)

    st.subheader("Form Curve Comparison")
    fig_form = go.Figure()
    if p1["Last 10 Innings"]:
        fig_form.add_trace(go.Scatter(
            x=list(range(1, len(p1["Last 10 Innings"])+1)),
            y=p1["Last 10 Innings"],
            mode="lines+markers", name=p1["Player"],
            line=dict(color="#00d4ff", width=2)
        ))
    if p2["Last 10 Innings"]:
        fig_form.add_trace(go.Scatter(
            x=list(range(1, len(p2["Last 10 Innings"])+1)),
            y=p2["Last 10 Innings"],
            mode="lines+markers", name=p2["Player"],
            line=dict(color="#ff4b4b", width=2)
        ))
    fig_form.update_layout(
        xaxis_title="Innings", yaxis_title="Runs",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_form, use_container_width=True)

st.divider()

# ── Best XI Picker ───────────────────────────────────────────────────────────
st.header("Best XI Picker")

scenario = st.selectbox(
    "Pick a match scenario",
    options=["Batting First", "Chasing"],
    key="scenario"
)

if st.button("Generate Best XI"):
    top_batsmen = df.nlargest(6, "Total Runs")
    
    if scenario == "Batting First":
        # prioritize high average players
        top_allround = df[df["Average"] > 20].nlargest(5, "Strike Rate")
    else:
        # prioritize high strike rate players for chasing
        top_allround = df[df["Strike Rate"] > 120].nlargest(5, "Total Runs")

    best_xi = pd.concat([top_batsmen, top_allround]).drop_duplicates(subset="Player").head(11)
    best_xi = best_xi.reset_index(drop=True)
    best_xi.index += 1

    st.subheader("Your Best XI — " + scenario)

    for i, row in best_xi.iterrows():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        col1.write(str(i) + ". " + row["Player"])
        col2.write("Runs: " + str(row["Total Runs"]))
        col3.write("Avg: " + str(row["Average"]))
        col4.write("SR: " + str(row["Strike Rate"]))

    # radar chart for best xi
    st.subheader("Best XI Radar — Average vs Strike Rate")
    fig_xi = go.Figure()
    for _, row in best_xi.iterrows():
        fig_xi.add_trace(go.Scatterpolar(
            r=[row["Total Runs"]/100, float(row["Average"]), float(row["Strike Rate"])/10],
            theta=["Runs (x100)", "Average", "Strike Rate (/10)"],
            fill="toself",
            name=row["Player"]
        ))
    fig_xi.update_layout(
        polar=dict(bgcolor="rgba(0,0,0,0)"),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True
    )
    st.plotly_chart(fig_xi, use_container_width=True)

st.divider()

# ── Season Filter ─────────────────────────────────────────────────────────────
st.header("Season-wise Player Performance")

season_map = {
    "2008": range(336000, 336100),
}

match_ids = sorted(raw["ID"].unique())
total_matches = len(match_ids)
matches_per_season = total_matches // 14
season_labels = [str(year) for year in range(2008, 2022)]
match_to_season = {}
for i, mid in enumerate(match_ids):
    season_idx = min(i // matches_per_season, 13)
    match_to_season[mid] = season_labels[season_idx]

raw["Season"] = raw["ID"].map(match_to_season)
seasons = sorted(raw["Season"].unique().tolist())

selected_season = st.selectbox("Select a Season", options=seasons, key="season")

if selected_season:
    players_in_season = sorted(raw[raw["Season"] == selected_season]["batter"].unique().tolist())
    selected_player_season = st.selectbox("Select a Player", options=[""] + players_in_season, key="season_player")

    if selected_player_season:
        season_data = raw[(raw["Season"] == selected_season) & (raw["batter"] == selected_player_season)]

        if season_data.empty:
            st.warning(selected_player_season + " has no data for " + selected_season)
        else:
            total_runs = season_data["batsman_run"].sum()
            total_balls = len(season_data)
            fours = len(season_data[season_data["batsman_run"] == 4])
            sixes = len(season_data[season_data["batsman_run"] == 6])
            strike_rate = round((total_runs / total_balls) * 100, 2) if total_balls > 0 else 0

            st.subheader(selected_player_season + " in IPL " + selected_season)

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Total Runs", total_runs)
            col2.metric("Balls Faced", total_balls)
            col3.metric("Strike Rate", strike_rate)
            col4.metric("Fours", fours)
            col5.metric("Sixes", sixes)

            match_runs = season_data.groupby("ID")["batsman_run"].sum().reset_index()
            match_runs.columns = ["Match", "Runs"]
            match_runs["Match"] = ["Match " + str(i+1) for i in range(len(match_runs))]

            st.subheader("Runs per Match in " + selected_season)
            fig_season = go.Figure()
            fig_season.add_trace(go.Bar(
                x=match_runs["Match"],
                y=match_runs["Runs"],
                marker_color=match_runs["Runs"],
                marker=dict(
                    color=match_runs["Runs"],
                    colorscale="Viridis",
                    showscale=False
                ),
                text=match_runs["Runs"],
                textposition="outside",
                width=0.4
            ))
            fig_season.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                height=350,
                xaxis=dict(tickangle=-30),
                yaxis=dict(gridcolor="rgba(255,255,255,0.1)")
            )
            st.plotly_chart(fig_season, use_container_width=True)
st.divider()

# ── Venue Performance ─────────────────────────────────────────────────────────
st.header("Venue Performance")

selected_player_venue = st.selectbox("Select a Player", options=[""] + all_players, key="venue_player")

if selected_player_venue:
    player_data = raw[raw["batter"] == selected_player_venue]

    if player_data.empty:
        st.warning("No data found for " + selected_player_venue)
    else:
        venue_stats = player_data.groupby("BattingTeam").agg(
            TotalRuns=("batsman_run", "sum"),
            BallsFaced=("batsman_run", "count"),
            Fours=("batsman_run", lambda x: (x == 4).sum()),
            Sixes=("batsman_run", lambda x: (x == 6).sum())
        ).reset_index()
        venue_stats["StrikeRate"] = round((venue_stats["TotalRuns"] / venue_stats["BallsFaced"]) * 100, 2)
        venue_stats = venue_stats.sort_values("TotalRuns", ascending=False)

        if len(venue_stats) < 3:
            st.warning(selected_player_venue + " has limited data. Please select a player with more matches.")
        else:
            st.subheader(selected_player_venue + " — Performance Against Each Team")

            col1, col2 = st.columns(2)

            with col1:
                fig_venue_runs = px.bar(
                    venue_stats, x="TotalRuns", y="BattingTeam",
                    orientation="h", color="TotalRuns",
                    color_continuous_scale="Plasma",
                    title="Runs Against Each Team"
                )
                fig_venue_runs.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    coloraxis_showscale=False,
                    height=40 * len(venue_stats) + 100
                )
                st.plotly_chart(fig_venue_runs, use_container_width=True)

            with col2:
                fig_venue_sr = px.bar(
                    venue_stats, x="StrikeRate", y="BattingTeam",
                    orientation="h", color="StrikeRate",
                    color_continuous_scale="RdYlGn",
                    title="Strike Rate Against Each Team"
                )
                fig_venue_sr.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    coloraxis_showscale=False,
                    height=40 * len(venue_stats) + 100
                )
                st.plotly_chart(fig_venue_sr, use_container_width=True)

            st.subheader("Runs vs Strike Rate vs Sixes (Bubble Chart)")
            fig_bubble = px.scatter(
                venue_stats, x="StrikeRate", y="TotalRuns",
                size="Sixes", color="BattingTeam",
                hover_name="BattingTeam",
                size_max=40,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_bubble.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=450
            )
            st.plotly_chart(fig_bubble, use_container_width=True)

st.divider()

# ── Section 1: Batting Analysis ─────────────────────────────────────────────
st.header("Batting Analysis")

col_a, col_b = st.columns(2)

with col_a:
    # Plot 1 — Horizontal bar: Top 10 run scorers
    st.subheader("Top 10 Run Scorers")
    top10 = df.nlargest(10, "Total Runs").sort_values("Total Runs")
    fig1 = px.bar(top10, x="Total Runs", y="Player", orientation="h",
                  color="Total Runs", color_continuous_scale="Viridis",
                  text="Total Runs")
    fig1.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                       coloraxis_showscale=False)
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    # Plot 3 — Bubble chart: Strike rate vs Average
    st.subheader("Strike Rate vs Average")
    top50 = df.nlargest(50, "Total Runs")
    fig3 = px.scatter(top50, x="Average", y="Strike Rate",
                      size="Total Runs", color="Total Runs",
                      hover_name="Player",
                      color_continuous_scale="Plasma",
                      size_max=40)
    fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig3, use_container_width=True)

col_c, col_d = st.columns(2)

with col_c:
    # Plot 4 — Violin plot: Score distribution for top 8 players
    st.subheader("Score Distribution (Top 8 Players)")
    top8_names = df.nlargest(8, "Total Runs")["Player"].tolist()
    violin_data = raw[raw["batter"].isin(top8_names)][["batter", "batsman_run"]]
    fig4 = px.violin(violin_data, x="batter", y="batsman_run",
                     color="batter", box=True,
                     color_discrete_sequence=px.colors.qualitative.Bold)
    fig4.update_layout(showlegend=False,
                       plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                       xaxis_tickangle=-30)
    st.plotly_chart(fig4, use_container_width=True)

with col_d:
    # Plot 5 — Grouped bar: Sixes vs Fours
    st.subheader("Sixes vs Fours (Top 10 Players)")
    top10_names = df.nlargest(10, "Total Runs")["Player"].tolist()
    bat_df = raw[raw["batter"].isin(top10_names)]
    sixes = bat_df[bat_df["batsman_run"] == 6].groupby("batter").size().reset_index(name="Sixes")
    fours = bat_df[bat_df["batsman_run"] == 4].groupby("batter").size().reset_index(name="Fours")
    merged = sixes.merge(fours, on="batter")
    fig5 = go.Figure(data=[
        go.Bar(name="Sixes", x=merged["batter"], y=merged["Sixes"], marker_color="#ff4b4b"),
        go.Bar(name="Fours", x=merged["batter"], y=merged["Fours"], marker_color="#ffd700")
    ])
    fig5.update_layout(barmode="group",
                       plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                       xaxis_tickangle=-30)
    st.plotly_chart(fig5, use_container_width=True)

st.divider()

# ── Section 2: Bowling Analysis ─────────────────────────────────────────────
st.header("Bowling Analysis")

col_e, col_f = st.columns(2)

with col_e:
    # Plot 6 — Lollipop chart: Top wicket takers
    st.subheader("Top 15 Wicket Takers")
    wickets = raw[raw["isWicketDelivery"] == 1].groupby("bowler").size().reset_index(name="Wickets")
    top_bowl = wickets.nlargest(15, "Wickets").sort_values("Wickets")
    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(
        x=top_bowl["Wickets"], y=top_bowl["bowler"],
        mode="markers", marker=dict(color="#00ff88", size=12)
    ))
    for _, row in top_bowl.iterrows():
        fig6.add_shape(type="line",
                       x0=0, x1=row["Wickets"],
                       y0=row["bowler"], y1=row["bowler"],
                       line=dict(color="#00ff88", width=2))
    fig6.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig6, use_container_width=True)

with col_f:
    # Plot 7 — Scatter: Economy vs Wickets
    st.subheader("Economy Rate vs Wickets")
    balls = raw.groupby("bowler").size().reset_index(name="Balls")
    runs_given = raw.groupby("bowler")["total_run"].sum().reset_index(name="RunsGiven")
    wkts = raw[raw["isWicketDelivery"] == 1].groupby("bowler").size().reset_index(name="Wickets")
    bowl_df = balls.merge(runs_given, on="bowler").merge(wkts, on="bowler")
    bowl_df = bowl_df[bowl_df["Balls"] >= 100]
    bowl_df["Economy"] = (bowl_df["RunsGiven"] / bowl_df["Balls"]) * 6
    fig7 = px.scatter(bowl_df, x="Economy", y="Wickets",
                      hover_name="bowler", color="Wickets",
                      color_continuous_scale="RdYlGn_r", size="Wickets", size_max=30)
    fig7.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig7, use_container_width=True)

col_g, col_h = st.columns(2)

with col_g:
    # Plot 8 — Treemap: Dot ball pressure
    st.subheader("Dot Ball Pressure (Treemap)")
    dot_balls = raw[raw["total_run"] == 0].groupby("bowler").size().reset_index(name="DotBalls")
    top_dots = dot_balls.nlargest(20, "DotBalls")
    fig8 = px.treemap(top_dots, path=["bowler"], values="DotBalls",
                      color="DotBalls", color_continuous_scale="Teal")
    fig8.update_layout(paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig8, use_container_width=True)

with col_h:
    # Plot 9 — Sunburst: Wicket types
    st.subheader("Wicket Types Breakdown (Sunburst)")
    wkt_df = raw[raw["isWicketDelivery"] == 1][["bowler", "kind"]].dropna()
    wkt_df = wkt_df[wkt_df["kind"] != "NA"]
    top_bowlers = wkt_df["bowler"].value_counts().head(8).index
    wkt_filtered = wkt_df[wkt_df["bowler"].isin(top_bowlers)]
    sunburst_df = wkt_filtered.groupby(["kind", "bowler"]).size().reset_index(name="Count")
    fig9 = px.sunburst(sunburst_df, path=["kind", "bowler"], values="Count",
                       color_discrete_sequence=px.colors.qualitative.Vivid)
    fig9.update_layout(paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig9, use_container_width=True)

st.divider()

# ── Section 3: Team Analysis ─────────────────────────────────────────────────
st.header("Team Analysis")

col_i, col_j = st.columns(2)

with col_i:
    # Plot 10 — Heatmap: Team wins by season
    st.subheader("Team Wins by Season (Heatmap)")
    if "ID" in raw.columns and "BattingTeam" in raw.columns:
        match_wins = raw.groupby(["ID", "BattingTeam"]).agg(
            TotalRuns=("total_run", "sum")).reset_index()
        top_score = match_wins.loc[match_wins.groupby("ID")["TotalRuns"].idxmax()]
        top_score["Season"] = top_score["ID"].astype(str).str[:4]
        heat_df = top_score.groupby(["BattingTeam", "Season"]).size().reset_index(name="Wins")
        heat_pivot = heat_df.pivot(index="BattingTeam", columns="Season", values="Wins").fillna(0)
        fig10 = px.imshow(heat_pivot, color_continuous_scale="YlOrRd",
                          aspect="auto", text_auto=True)
        fig10.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig10, use_container_width=True)

with col_j:
    # Plot 11 — Radar chart: Team profile
    st.subheader("Team Stats Radar")
    teams = raw.groupby("BattingTeam").agg(
        TotalRuns=("total_run", "sum"),
        TotalBalls=("ballnumber", "count")
    ).reset_index()
    teams["StrikeRate"] = (teams["TotalRuns"] / teams["TotalBalls"]) * 100
    top6_teams = teams.nlargest(6, "TotalRuns")
    categories = ["TotalRuns", "TotalBalls", "StrikeRate"]
    fig11 = go.Figure()
    colors = ["#ff4b4b","#ffd700","#00ff88","#00d4ff","#ff69b4","#ff8c00"]
    for i, (_, row) in enumerate(top6_teams.iterrows()):
        vals = [row["TotalRuns"]/1000, row["TotalBalls"]/1000, row["StrikeRate"]]
        vals += vals[:1]
        fig11.add_trace(go.Scatterpolar(
            r=vals, theta=categories + [categories[0]],
            fill="toself", name=row["BattingTeam"],
            line_color=colors[i]
        ))
    fig11.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)"),
                        paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig11, use_container_width=True)

# Plot 12 — Waterfall: Powerplay run buildup
st.subheader("Powerplay Run Buildup — Over by Over (Top 4 Teams)")
top4_teams = teams.nlargest(4, "TotalRuns")["BattingTeam"].tolist()
powerplay = raw[(raw["overs"] < 6) & (raw["BattingTeam"].isin(top4_teams))]
over_runs = powerplay.groupby(["BattingTeam", "overs"])["total_run"].sum().reset_index()

fig12 = go.Figure()
colors12 = ["#ff4b4b", "#ffd700", "#00ff88", "#00d4ff"]
for i, team in enumerate(top4_teams):
    team_data = over_runs[over_runs["BattingTeam"] == team].sort_values("overs")
    fig12.add_trace(go.Waterfall(
        name=team,
        x=[f"Over {int(o)+1}" for o in team_data["overs"]],
        y=team_data["total_run"].tolist(),
        connector=dict(line=dict(color=colors12[i])),
        increasing=dict(marker_color=colors12[i])
    ))
fig12.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    barmode="group")
st.plotly_chart(fig12, use_container_width=True)

st.divider()

# ── Section 4: Match and Season Trends ──────────────────────────────────────
st.header("Match and Season Trends")

col_k, col_l = st.columns(2)

with col_k:
    # Plot 13 — Animated bubble: IPL scoring trend
    st.subheader("IPL Scoring Trend Over Seasons")
    raw["Season"] = raw["ID"].astype(str).str[:4]
    season_team = raw.groupby(["Season", "BattingTeam"]).agg(
        TotalRuns=("total_run", "sum"),
        TotalBalls=("ballnumber", "count")
    ).reset_index()
    season_team["StrikeRate"] = (season_team["TotalRuns"] / season_team["TotalBalls"]) * 100
    fig13 = px.scatter(season_team, x="StrikeRate", y="TotalRuns",
                       size="TotalRuns", color="BattingTeam",
                       animation_frame="Season", hover_name="BattingTeam",
                       size_max=50,
                       color_discrete_sequence=px.colors.qualitative.Bold)
    fig13.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig13, use_container_width=True)

with col_l:
    # Plot 14 — Funnel: Highest scoring matches
    st.subheader("Highest Scoring Matches (Funnel)")
    match_totals = raw.groupby("ID")["total_run"].sum().reset_index(name="TotalRuns")
    top10_matches = match_totals.nlargest(10, "TotalRuns")
    top10_matches["Match"] = "Match " + top10_matches["ID"].astype(str)
    fig14 = go.Figure(go.Funnel(
        y=top10_matches["Match"],
        x=top10_matches["TotalRuns"],
        textinfo="value+percent initial",
        marker=dict(color=px.colors.sequential.Plasma_r[:10])
    ))
    fig14.update_layout(paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig14, use_container_width=True)

# Plot 15 — Donut: Toss decision impact
st.subheader("Toss Decision Impact")
if "extra_type" in raw.columns:
    bat_first = raw[raw["innings"] == 1]["BattingTeam"].nunique()
    field_first = raw[raw["innings"] == 2]["BattingTeam"].nunique()
    fig15 = go.Figure(data=[go.Pie(
        labels=["Bat First", "Field First"],
        values=[bat_first, field_first],
        hole=0.5,
        marker=dict(colors=["#ff4b4b", "#00d4ff"])
    )])
    fig15.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                        annotations=[dict(text="Toss", x=0.5, y=0.5,
                                         font_size=18, showarrow=False)])
    st.plotly_chart(fig15, use_container_width=True)

st.divider()
st.caption("Built with Hadoop MapReduce + Streamlit · IPL 2008–2022 · by Nandhana")
