# IPL Player Form Tracker

A big data pipeline project that processes IPL ball-by-ball data (2008-2022) using Apache Hadoop MapReduce inside Docker, and visualizes results through an interactive Streamlit web app.

## Project Summary

For a detailed breakdown of every command, every error faced, and how the project works end to end, refer to the full project summary document:

[IPL Project Summary (docx)](./IPL_Project_Summary.docx)

## Tech Stack

- Apache Hadoop 3.3.6 (via Docker)
- Hadoop MapReduce Streaming (Python)
- Streamlit
- Plotly
- Pandas
- Docker

## Dataset

IPL Ball by Ball data from 2008 to 2022 — 225,954 rows, 20MB raw CSV processed through HDFS and MapReduce.

## Project Flow

1. Raw CSV uploaded to HDFS using `hdfs dfs -put`
2. MapReduce job runs mapper.py and reducer.py to aggregate player stats
3. Output of 605 player records written to part-00000
4. Streamlit app reads Hadoop output and renders 15 interactive plots

## Features

- Player Lookup with autocomplete search
- Player vs Player Comparison
- Best XI Picker for batting first or chasing
- Season-wise Player Performance filter
- Venue Performance — stats against each team
- 15 analysis plots covering batting, bowling, team, and season trends

## 15 Analysis Plots

### Batting Analysis

| Plot | Chart Type | What It Shows | Why This Chart |
|------|-----------|---------------|----------------|
| Top 10 Run Scorers | Horizontal Bar | Ranked total runs per player across all IPL seasons | Player names fit cleanly on y-axis, easy rank comparison |
| Player Form Curve | Area Chart | Last 10 innings scores with color fill | Filled area shows volume of performance, continuity across innings |
| Strike Rate vs Average | Bubble Chart | Three variables at once — strike rate, average, and matches as bubble size | Only chart that shows 3 dimensions simultaneously |
| Score Distribution | Violin Plot | Full spread of a player's innings scores — consistency vs erratic | Shows actual shape of data, box plot hides distribution |
| Sixes vs Fours | Grouped Bar | Side by side sixes and fours count per top player | Separate bars allow direct comparison of two related metrics |

### Bowling Analysis

| Plot | Chart Type | What It Shows | Why This Chart |
|------|-----------|---------------|----------------|
| Top Wicket Takers | Lollipop Chart | Ranked wickets per bowler with dot marking exact value | Cleaner than bar chart for many players, less visual clutter |
| Economy vs Wickets | Scatter Plot | Four quadrants — cheap effective, expensive effective, etc. | Two continuous metrics need two axes to reveal quadrant patterns |
| Dot Ball Pressure | Treemap | Relative dot ball contribution per bowler, bigger box means more | Space efficient for many bowlers, size encodes value immediately |
| Wicket Types | Sunburst Chart | Two level hierarchy — wicket type outer, bowler inner | Handles hierarchy that pie cannot, shows both breakdown and contributor |

### Team Analysis

| Plot | Chart Type | What It Shows | Why This Chart |
|------|-----------|---------------|----------------|
| Team Wins by Season | Heatmap | Teams vs seasons grid, color intensity equals wins | Two axis comparison across 10 teams and 15 seasons |
| Team Profile | Radar Chart | Multiple stats per team on spokes simultaneously | Shows overall team shape across all metrics at once |
| Powerplay Run Buildup | Waterfall Chart | Cumulative run buildup over overs 1 to 6 per team | Shows each over's individual contribution to the running total |

### Match and Season Trends

| Plot | Chart Type | What It Shows | Why This Chart |
|------|-----------|---------------|----------------|
| IPL Scoring Trend | Animated Bubble | Teams evolving season by season, bubble size is total runs | Animation adds the time dimension, static chart cannot show evolution |
| Highest Scoring Matches | Funnel Chart | Top matches ranked from highest to lowest total score | Narrowing shape reinforces drop off, memorable for ranked data |
| Toss Decision Impact | Donut Chart | Proportion of bat first vs field first decisions and win rates | Only two categories, center hole displays total matches count |

## How to Run
```bash
# activate virtual environment
venv\Scripts\activate

# run the app
streamlit run app/app.py
```

## Author

Nandhana — Big Data Project 2026