import streamlit as st
import pandas as pd
import ast
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="IPL Player Form Tracker", layout="wide", page_icon="🏏")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .block-container { padding-top: 2rem; }
    </style>
""", unsafe_allow_html=True)

transparentBg = dict(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

@st.cache_data
def loadHadoopOutput():
    rows = []
    with open(r"D:/Downloads/ipl-player-form-tracker/hadoop_output/part-00000", "r") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 6:
                try:
                    rows.append([
                        parts[0],
                        int(parts[1]),
                        int(parts[2]),
                        float(parts[3]),
                        float(parts[4]),
                        ast.literal_eval(parts[5])
                    ])
                except:
                    continue
    return pd.DataFrame(rows, columns=["Player", "Total Runs", "Balls Faced", "Average", "Strike Rate", "Last 10 Innings"])

@st.cache_data
def loadRawData():
    return pd.read_csv(r"D:/Downloads/ipl-player-form-tracker/data/data.csv")

playerDf = loadHadoopOutput()
rawDf = loadRawData()
allPlayers = playerDf["Player"].tolist()

st.title("IPL Player Form Tracker")
st.caption("Powered by Hadoop MapReduce · IPL 2008–2022")
st.divider()

# Player Lookup
st.subheader("Player Lookup")

selectedPlayer = st.selectbox("Search for a player", options=[""] + allPlayers, index=0, key="singlePlayer")

if selectedPlayer:
    playerRow = playerDf[playerDf["Player"] == selectedPlayer].iloc[0]

    st.subheader(playerRow["Player"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Runs", playerRow["Total Runs"])
    c2.metric("Balls Faced", playerRow["Balls Faced"])
    c3.metric("Average", playerRow["Average"])
    c4.metric("Strike Rate", playerRow["Strike Rate"])

    recentInnings = playerRow["Last 10 Innings"]
    if recentInnings:
        st.subheader("Form Curve — Last 10 Innings")
        formFig = go.Figure()
        formFig.add_trace(go.Scatter(
            x=list(range(1, len(recentInnings) + 1)),
            y=recentInnings,
            fill="tozeroy",
            mode="lines+markers",
            line=dict(color="#00d4ff", width=2),
            fillcolor="rgba(0,212,255,0.15)"
        ))
        formFig.update_layout(xaxis_title="Innings", yaxis_title="Runs", **transparentBg)
        st.plotly_chart(formFig, use_container_width=True)

st.divider()

# Player vs Player
st.header("Player vs Player Comparison")

leftCol, rightCol = st.columns(2)
with leftCol:
    p1Name = st.selectbox("Search Player 1", options=[""] + allPlayers, index=0, key="p1")
with rightCol:
    p2Name = st.selectbox("Search Player 2", options=[""] + allPlayers, index=0, key="p2")

if p1Name and p2Name:
    p1 = playerDf[playerDf["Player"] == p1Name].iloc[0]
    p2 = playerDf[playerDf["Player"] == p2Name].iloc[0]

    st.subheader(p1["Player"] + " vs " + p2["Player"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Runs", p1["Total Runs"], int(p1["Total Runs"]) - int(p2["Total Runs"]))
    c2.metric("Average", p1["Average"], round(float(p1["Average"]) - float(p2["Average"]), 2))
    c3.metric("Strike Rate", p1["Strike Rate"], round(float(p1["Strike Rate"]) - float(p2["Strike Rate"]), 2))
    c4.metric("Balls Faced", p1["Balls Faced"], int(p1["Balls Faced"]) - int(p2["Balls Faced"]))

    st.subheader("Stats Comparison")
    compareDf = pd.DataFrame({
        "Stat": ["Total Runs", "Average", "Strike Rate", "Balls Faced"],
        p1["Player"]: [p1["Total Runs"], p1["Average"], p1["Strike Rate"], p1["Balls Faced"]],
        p2["Player"]: [p2["Total Runs"], p2["Average"], p2["Strike Rate"], p2["Balls Faced"]]
    })
    compareFig = go.Figure(data=[
        go.Bar(name=p1["Player"], x=compareDf["Stat"], y=compareDf[p1["Player"]], marker_color="#00d4ff"),
        go.Bar(name=p2["Player"], x=compareDf["Stat"], y=compareDf[p2["Player"]], marker_color="#ff4b4b")
    ])
    compareFig.update_layout(barmode="group", **transparentBg)
    st.plotly_chart(compareFig, use_container_width=True)

    st.subheader("Form Curve Comparison")
    formCompareFig = go.Figure()
    if p1["Last 10 Innings"]:
        formCompareFig.add_trace(go.Scatter(
            x=list(range(1, len(p1["Last 10 Innings"]) + 1)),
            y=p1["Last 10 Innings"],
            mode="lines+markers", name=p1["Player"],
            line=dict(color="#00d4ff", width=2)
        ))
    if p2["Last 10 Innings"]:
        formCompareFig.add_trace(go.Scatter(
            x=list(range(1, len(p2["Last 10 Innings"]) + 1)),
            y=p2["Last 10 Innings"],
            mode="lines+markers", name=p2["Player"],
            line=dict(color="#ff4b4b", width=2)
        ))
    formCompareFig.update_layout(xaxis_title="Innings", yaxis_title="Runs", **transparentBg)
    st.plotly_chart(formCompareFig, use_container_width=True)

st.divider()

# Best XI Picker
st.header("Best XI Picker")

matchScenario = st.selectbox("Pick a match scenario", options=["Batting First", "Chasing"], key="scenario")

if st.button("Generate Best XI"):
    topBatsmen = playerDf.nlargest(6, "Total Runs")

    if matchScenario == "Batting First":
        topAllround = playerDf[playerDf["Average"] > 20].nlargest(5, "Strike Rate")
    else:
        topAllround = playerDf[playerDf["Strike Rate"] > 100].nlargest(5, "Total Runs")

    bestXi = pd.concat([topBatsmen, topAllround]).drop_duplicates(subset="Player").head(11)
    bestXi = bestXi.reset_index(drop=True)
    bestXi.index += 1

    st.subheader("Your Best XI — " + matchScenario)
    for i, row in bestXi.iterrows():
        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
        c1.write(str(i) + ". " + row["Player"])
        c2.write("Runs: " + str(row["Total Runs"]))
        c3.write("Avg: " + str(row["Average"]))
        c4.write("SR: " + str(row["Strike Rate"]))

    st.subheader("Best XI Radar — Average vs Strike Rate")
    radarFig = go.Figure()
    for _, row in bestXi.iterrows():
        radarFig.add_trace(go.Scatterpolar(
            r=[row["Total Runs"] / 100, float(row["Average"]), float(row["Strike Rate"]) / 10],
            theta=["Runs (x100)", "Average", "Strike Rate (/10)"],
            fill="toself",
            name=row["Player"]
        ))
    radarFig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)"), paper_bgcolor="rgba(0,0,0,0)", showlegend=True)
    st.plotly_chart(radarFig, use_container_width=True)

st.divider()

# Season Filter
st.header("Season-wise Player Performance")

matchIds = sorted(rawDf["ID"].unique())
matchesPerSeason = len(matchIds) // 14
seasonLabels = [str(y) for y in range(2008, 2022)]
matchToSeason = {}
for i, mid in enumerate(matchIds):
    matchToSeason[mid] = seasonLabels[min(i // matchesPerSeason, 13)]

rawDf["Season"] = rawDf["ID"].map(matchToSeason)
seasons = sorted(rawDf["Season"].unique().tolist())

selectedSeason = st.selectbox("Select a Season", options=seasons, key="season")

if selectedSeason:
    playersInSeason = sorted(rawDf[rawDf["Season"] == selectedSeason]["batter"].unique().tolist())
    selectedSeasonPlayer = st.selectbox("Select a Player", options=[""] + playersInSeason, key="seasonPlayer")

    if selectedSeasonPlayer:
        seasonData = rawDf[(rawDf["Season"] == selectedSeason) & (rawDf["batter"] == selectedSeasonPlayer)]

        if seasonData.empty:
            st.warning(selectedSeasonPlayer + " has no data for " + selectedSeason)
        else:
            totalRuns = seasonData["batsman_run"].sum()
            totalBalls = len(seasonData)
            totalFours = len(seasonData[seasonData["batsman_run"] == 4])
            totalSixes = len(seasonData[seasonData["batsman_run"] == 6])
            sr = round((totalRuns / totalBalls) * 100, 2) if totalBalls > 0 else 0

            st.subheader(selectedSeasonPlayer + " in IPL " + selectedSeason)
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Total Runs", totalRuns)
            c2.metric("Balls Faced", totalBalls)
            c3.metric("Strike Rate", sr)
            c4.metric("Fours", totalFours)
            c5.metric("Sixes", totalSixes)

            matchRuns = seasonData.groupby("ID")["batsman_run"].sum().reset_index()
            matchRuns.columns = ["Match", "Runs"]
            matchRuns["Match"] = ["Match " + str(i + 1) for i in range(len(matchRuns))]

            st.subheader("Runs per Match in " + selectedSeason)
            seasonFig = go.Figure()
            seasonFig.add_trace(go.Bar(
                x=matchRuns["Match"],
                y=matchRuns["Runs"],
                marker=dict(color=matchRuns["Runs"], colorscale="Viridis", showscale=False),
                text=matchRuns["Runs"],
                textposition="outside",
                width=0.4
            ))
            seasonFig.update_layout(
                height=350,
                xaxis=dict(tickangle=-30),
                yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
                **transparentBg
            )
            st.plotly_chart(seasonFig, use_container_width=True)

st.divider()

# Venue Performance
st.header("Venue Performance")

selectedVenuePlayer = st.selectbox("Select a Player", options=[""] + allPlayers, key="venuePlayer")

if selectedVenuePlayer:
    playerVenueData = rawDf[rawDf["batter"] == selectedVenuePlayer]

    if playerVenueData.empty:
        st.warning("No data found for " + selectedVenuePlayer)
    else:
        venueStats = playerVenueData.groupby("BattingTeam").agg(
            TotalRuns=("batsman_run", "sum"),
            BallsFaced=("batsman_run", "count"),
            Fours=("batsman_run", lambda x: (x == 4).sum()),
            Sixes=("batsman_run", lambda x: (x == 6).sum())
        ).reset_index()
        venueStats["StrikeRate"] = round((venueStats["TotalRuns"] / venueStats["BallsFaced"]) * 100, 2)
        venueStats = venueStats.sort_values("TotalRuns", ascending=False)

        if len(venueStats) < 3:
            st.warning(selectedVenuePlayer + " has limited data. Please select a player with more matches.")
        else:
            st.subheader(selectedVenuePlayer + " — Performance Against Each Team")

            c1, c2 = st.columns(2)
            chartHeight = 40 * len(venueStats) + 100

            with c1:
                runsFig = px.bar(venueStats, x="TotalRuns", y="BattingTeam",
                                 orientation="h", color="TotalRuns",
                                 color_continuous_scale="Plasma", title="Runs Against Each Team")
                runsFig.update_layout(coloraxis_showscale=False, height=chartHeight, **transparentBg)
                st.plotly_chart(runsFig, use_container_width=True)

            with c2:
                srFig = px.bar(venueStats, x="StrikeRate", y="BattingTeam",
                               orientation="h", color="StrikeRate",
                               color_continuous_scale="RdYlGn", title="Strike Rate Against Each Team")
                srFig.update_layout(coloraxis_showscale=False, height=chartHeight, **transparentBg)
                st.plotly_chart(srFig, use_container_width=True)

            st.subheader("Runs vs Strike Rate vs Sixes (Bubble Chart)")
            bubbleFig = px.scatter(venueStats, x="StrikeRate", y="TotalRuns",
                                   size="Sixes", color="BattingTeam",
                                   hover_name="BattingTeam", size_max=40,
                                   color_discrete_sequence=px.colors.qualitative.Bold)
            bubbleFig.update_layout(height=450, **transparentBg)
            st.plotly_chart(bubbleFig, use_container_width=True)

st.divider()

# Batting Analysis
st.header("Batting Analysis")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Top 10 Run Scorers")
    top10 = playerDf.nlargest(10, "Total Runs").sort_values("Total Runs")
    topRunsFig = px.bar(top10, x="Total Runs", y="Player", orientation="h",
                        color="Total Runs", color_continuous_scale="Viridis", text="Total Runs")
    topRunsFig.update_layout(coloraxis_showscale=False, **transparentBg)
    st.plotly_chart(topRunsFig, use_container_width=True)

with c2:
    st.subheader("Strike Rate vs Average")
    top50 = playerDf.nlargest(50, "Total Runs")
    bubbleStatFig = px.scatter(top50, x="Average", y="Strike Rate",
                               size="Total Runs", color="Total Runs",
                               hover_name="Player", color_continuous_scale="Plasma", size_max=40)
    bubbleStatFig.update_layout(**transparentBg)
    st.plotly_chart(bubbleStatFig, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    st.subheader("Score Distribution (Top 8 Players)")
    top8Names = playerDf.nlargest(8, "Total Runs")["Player"].tolist()
    violinData = rawDf[rawDf["batter"].isin(top8Names)][["batter", "batsman_run"]]
    violinFig = px.violin(violinData, x="batter", y="batsman_run",
                          color="batter", box=True,
                          color_discrete_sequence=px.colors.qualitative.Bold)
    violinFig.update_layout(showlegend=False, xaxis_tickangle=-30, **transparentBg)
    st.plotly_chart(violinFig, use_container_width=True)

with c4:
    st.subheader("Sixes vs Fours (Top 10 Players)")
    top10Names = playerDf.nlargest(10, "Total Runs")["Player"].tolist()
    batDf = rawDf[rawDf["batter"].isin(top10Names)]
    sixesDf = batDf[batDf["batsman_run"] == 6].groupby("batter").size().reset_index(name="Sixes")
    foursDf = batDf[batDf["batsman_run"] == 4].groupby("batter").size().reset_index(name="Fours")
    sixFourDf = sixesDf.merge(foursDf, on="batter")
    sixFourFig = go.Figure(data=[
        go.Bar(name="Sixes", x=sixFourDf["batter"], y=sixFourDf["Sixes"], marker_color="#ff4b4b"),
        go.Bar(name="Fours", x=sixFourDf["batter"], y=sixFourDf["Fours"], marker_color="#ffd700")
    ])
    sixFourFig.update_layout(barmode="group", xaxis_tickangle=-30, **transparentBg)
    st.plotly_chart(sixFourFig, use_container_width=True)

st.divider()

# Bowling Analysis
st.header("Bowling Analysis")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Top 15 Wicket Takers")
    wicketsDf = rawDf[rawDf["isWicketDelivery"] == 1].groupby("bowler").size().reset_index(name="Wickets")
    topBowlers = wicketsDf.nlargest(15, "Wickets").sort_values("Wickets")
    lollipopFig = go.Figure()
    lollipopFig.add_trace(go.Scatter(
        x=topBowlers["Wickets"], y=topBowlers["bowler"],
        mode="markers", marker=dict(color="#00ff88", size=12)
    ))
    for _, row in topBowlers.iterrows():
        lollipopFig.add_shape(type="line",
                              x0=0, x1=row["Wickets"],
                              y0=row["bowler"], y1=row["bowler"],
                              line=dict(color="#00ff88", width=2))
    lollipopFig.update_layout(**transparentBg)
    st.plotly_chart(lollipopFig, use_container_width=True)

with c2:
    st.subheader("Economy Rate vs Wickets")
    ballsDf = rawDf.groupby("bowler").size().reset_index(name="Balls")
    runsGivenDf = rawDf.groupby("bowler")["total_run"].sum().reset_index(name="RunsGiven")
    wktsDf = rawDf[rawDf["isWicketDelivery"] == 1].groupby("bowler").size().reset_index(name="Wickets")
    bowlDf = ballsDf.merge(runsGivenDf, on="bowler").merge(wktsDf, on="bowler")
    bowlDf = bowlDf[bowlDf["Balls"] >= 100]
    bowlDf["Economy"] = (bowlDf["RunsGiven"] / bowlDf["Balls"]) * 6
    econFig = px.scatter(bowlDf, x="Economy", y="Wickets",
                         hover_name="bowler", color="Wickets",
                         color_continuous_scale="RdYlGn_r", size="Wickets", size_max=30)
    econFig.update_layout(**transparentBg)
    st.plotly_chart(econFig, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    st.subheader("Dot Ball Pressure (Treemap)")
    dotBallsDf = rawDf[rawDf["total_run"] == 0].groupby("bowler").size().reset_index(name="DotBalls")
    topDots = dotBallsDf.nlargest(20, "DotBalls")
    treemapFig = px.treemap(topDots, path=["bowler"], values="DotBalls",
                            color="DotBalls", color_continuous_scale="Teal")
    treemapFig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(treemapFig, use_container_width=True)

with c4:
    st.subheader("Wicket Types Breakdown (Sunburst)")
    wktTypeDf = rawDf[rawDf["isWicketDelivery"] == 1][["bowler", "kind"]].dropna()
    wktTypeDf = wktTypeDf[wktTypeDf["kind"] != "NA"]
    topBowlerNames = wktTypeDf["bowler"].value_counts().head(8).index
    wktFiltered = wktTypeDf[wktTypeDf["bowler"].isin(topBowlerNames)]
    sunburstDf = wktFiltered.groupby(["kind", "bowler"]).size().reset_index(name="Count")
    sunburstFig = px.sunburst(sunburstDf, path=["kind", "bowler"], values="Count",
                              color_discrete_sequence=px.colors.qualitative.Vivid)
    sunburstFig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(sunburstFig, use_container_width=True)

st.divider()

# Team Analysis
st.header("Team Analysis")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Team Wins by Season (Heatmap)")
    if "ID" in rawDf.columns and "BattingTeam" in rawDf.columns:
        matchWins = rawDf.groupby(["ID", "BattingTeam"]).agg(TotalRuns=("total_run", "sum")).reset_index()
        topScore = matchWins.loc[matchWins.groupby("ID")["TotalRuns"].idxmax()]
        topScore["Season"] = topScore["ID"].astype(str).str[:4]
        heatDf = topScore.groupby(["BattingTeam", "Season"]).size().reset_index(name="Wins")
        heatPivot = heatDf.pivot(index="BattingTeam", columns="Season", values="Wins").fillna(0)
        heatFig = px.imshow(heatPivot, color_continuous_scale="YlOrRd", aspect="auto", text_auto=True)
        heatFig.update_layout(**transparentBg)
        st.plotly_chart(heatFig, use_container_width=True)

with c2:
    st.subheader("Team Stats Radar")
    teamsDf = rawDf.groupby("BattingTeam").agg(
        TotalRuns=("total_run", "sum"),
        TotalBalls=("ballnumber", "count")
    ).reset_index()
    teamsDf["StrikeRate"] = (teamsDf["TotalRuns"] / teamsDf["TotalBalls"]) * 100
    top6Teams = teamsDf.nlargest(6, "TotalRuns")
    radarCategories = ["TotalRuns", "TotalBalls", "StrikeRate"]
    teamRadarFig = go.Figure()
    radarColors = ["#ff4b4b", "#ffd700", "#00ff88", "#00d4ff", "#ff69b4", "#ff8c00"]
    for i, (_, row) in enumerate(top6Teams.iterrows()):
        vals = [row["TotalRuns"] / 1000, row["TotalBalls"] / 1000, row["StrikeRate"]]
        vals += vals[:1]
        teamRadarFig.add_trace(go.Scatterpolar(
            r=vals, theta=radarCategories + [radarCategories[0]],
            fill="toself", name=row["BattingTeam"], line_color=radarColors[i]
        ))
    teamRadarFig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)"), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(teamRadarFig, use_container_width=True)

st.subheader("Powerplay Run Buildup — Over by Over (Top 4 Teams)")
top4Teams = teamsDf.nlargest(4, "TotalRuns")["BattingTeam"].tolist()
powerplayDf = rawDf[(rawDf["overs"] < 6) & (rawDf["BattingTeam"].isin(top4Teams))]
overRunsDf = powerplayDf.groupby(["BattingTeam", "overs"])["total_run"].sum().reset_index()

waterfallFig = go.Figure()
waterfallColors = ["#ff4b4b", "#ffd700", "#00ff88", "#00d4ff"]
for i, team in enumerate(top4Teams):
    teamData = overRunsDf[overRunsDf["BattingTeam"] == team].sort_values("overs")
    waterfallFig.add_trace(go.Waterfall(
        name=team,
        x=["Over " + str(int(o) + 1) for o in teamData["overs"]],
        y=teamData["total_run"].tolist(),
        connector=dict(line=dict(color=waterfallColors[i])),
        increasing=dict(marker_color=waterfallColors[i])
    ))
waterfallFig.update_layout(barmode="group", **transparentBg)
st.plotly_chart(waterfallFig, use_container_width=True)

st.divider()

# Match and Season Trends
st.header("Match and Season Trends")

c1, c2 = st.columns(2)

with c1:
    st.subheader("IPL Scoring Trend Over Seasons")
    rawDf["Season"] = rawDf["ID"].astype(str).str[:4]
    seasonTeamDf = rawDf.groupby(["Season", "BattingTeam"]).agg(
        TotalRuns=("total_run", "sum"),
        TotalBalls=("ballnumber", "count")
    ).reset_index()
    seasonTeamDf["StrikeRate"] = (seasonTeamDf["TotalRuns"] / seasonTeamDf["TotalBalls"]) * 100
    animatedFig = px.scatter(seasonTeamDf, x="StrikeRate", y="TotalRuns",
                             size="TotalRuns", color="BattingTeam",
                             animation_frame="Season", hover_name="BattingTeam",
                             size_max=50, color_discrete_sequence=px.colors.qualitative.Bold)
    animatedFig.update_layout(**transparentBg)
    st.plotly_chart(animatedFig, use_container_width=True)

with c2:
    st.subheader("Highest Scoring Matches (Funnel)")
    matchTotals = rawDf.groupby("ID")["total_run"].sum().reset_index(name="TotalRuns")
    top10Matches = matchTotals.nlargest(10, "TotalRuns")
    top10Matches["Match"] = "Match " + top10Matches["ID"].astype(str)
    funnelFig = go.Figure(go.Funnel(
        y=top10Matches["Match"],
        x=top10Matches["TotalRuns"],
        textinfo="value+percent initial",
        marker=dict(color=px.colors.sequential.Plasma_r[:10])
    ))
    funnelFig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(funnelFig, use_container_width=True)

st.subheader("Toss Decision Impact")
if "extra_type" in rawDf.columns:
    batFirst = rawDf[rawDf["innings"] == 1]["BattingTeam"].nunique()
    fieldFirst = rawDf[rawDf["innings"] == 2]["BattingTeam"].nunique()
    donutFig = go.Figure(data=[go.Pie(
        labels=["Bat First", "Field First"],
        values=[batFirst, fieldFirst],
        hole=0.5,
        marker=dict(colors=["#ff4b4b", "#00d4ff"])
    )])
    donutFig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(text="Toss", x=0.5, y=0.5, font_size=18, showarrow=False)]
    )
    st.plotly_chart(donutFig, use_container_width=True)

st.divider()