# IPL Player Form Tracker

A big data pipeline project that processes IPL ball-by-ball data (2008-2022) using Apache Hadoop MapReduce inside Docker, and visualizes results through an interactive Streamlit web app.

## Project Summary

For a detailed breakdown of every command, every error faced, and how the project works end to end, refer to the full project summary document:

[IPL Project Summary (pdf)](./IPL_Project_summary.pdf)

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
## Hadoop Setup

You can set up Hadoop either by downloading it directly or by using Docker. This project uses Docker.

---

### Option 1 — Using Docker (Recommended, what this project uses)

**Step 1 — Pull the base Hadoop image**
```bash
docker pull apache/hadoop:3
```

**Step 2 — Build the custom image with your files**

Make sure your `Dockerfile` is in the project root, then run:
```bash
docker build -t hadoop-python3 .
```

**Step 3 — Start the container as root**
```bash
docker run -it --user root hadoop-python3 bash
```

**Step 4 — Inside the container, set environment variables**
```bash
export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.212.b04-0.el7_6.x86_64/jre
export HDFS_NAMENODE_USER=root
export HDFS_DATANODE_USER=root
export HDFS_SECONDARYNAMENODE_USER=root
export YARN_RESOURCEMANAGER_USER=root
export YARN_NODEMANAGER_USER=root
```

**Step 5 — Persist JAVA_HOME in Hadoop config**
```bash
echo "export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.212.b04-0.el7_6.x86_64/jre" >> /opt/hadoop/etc/hadoop/hadoop-env.sh
```

**Step 6 — Configure HDFS**
```bash
cat > /opt/hadoop/etc/hadoop/core-site.xml << 'EOF'
<?xml version="1.0"?>
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://localhost:9000</value>
  </property>
</configuration>
EOF
```
```bash
cat > /opt/hadoop/etc/hadoop/hdfs-site.xml << 'EOF'
<?xml version="1.0"?>
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>1</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>/tmp/hadoop-root/dfs/name</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>/tmp/hadoop-root/dfs/data</value>
  </property>
</configuration>
EOF
```

**Step 7 — Format namenode and start services**
```bash
/opt/hadoop/bin/hdfs namenode -format -force
/opt/hadoop/bin/hdfs namenode &
/opt/hadoop/bin/hdfs datanode &
```

**Step 8 — Upload dataset and run MapReduce**
```bash
/opt/hadoop/bin/hdfs dfs -mkdir -p /ipl/input
/opt/hadoop/bin/hdfs dfs -put /opt/data.csv /ipl/input/
/opt/hadoop/bin/hadoop jar /opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    -input /ipl/input/data.csv \
    -output /ipl/output \
    -mapper "python /opt/mapper.py" \
    -reducer "python /opt/reducer.py"
```

**Step 9 — Copy output to local machine**

Run this from your local terminal, not inside the container:
```bash
docker cp <container_id>:/opt/part-00000 hadoop_output/part-00000
```

---

### Option 2 — Direct Download (without Docker)

**Step 1 — Download Hadoop**

Go to https://hadoop.apache.org/releases.html and download Hadoop 3.3.6 for your OS.

**Step 2 — Set environment variables (add to your .bashrc or .zshrc)**
```bash
export HADOOP_HOME=/path/to/hadoop-3.3.6
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
export JAVA_HOME=/path/to/your/java
```

**Step 3 — Configure core-site.xml and hdfs-site.xml**

Same XML config as shown in Option 1 above, located at `$HADOOP_HOME/etc/hadoop/`.

**Step 4 — Format and start**
```bash
hdfs namenode -format -force
start-dfs.sh
```

**Step 5 — Run MapReduce**
```bash
hdfs dfs -mkdir -p /ipl/input
hdfs dfs -put data/data.csv /ipl/input/
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    -input /ipl/input/data.csv \
    -output /ipl/output \
    -mapper "python3 hadoop/mapper.py" \
    -reducer "python3 hadoop/reducer.py"
hdfs dfs -get /ipl/output/part-00000 hadoop_output/part-00000
```

---

> Note: This project was built and tested using Option 1 (Docker). Option 2 requires Java 8 or above installed on your machine.

```bash
# activate virtual environment
venv\Scripts\activate

# run the app
streamlit run app/app.py
```
