#!/bin/bash

# Step 1 - create input directory in HDFS
hadoop fs -mkdir -p /ipl/input

# Step 2 - upload dataset to HDFS
hadoop fs -put /home/hadoop/data.csv /ipl/input/

# Step 3 - run the MapReduce job
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    -input /ipl/input/data.csv \
    -output /ipl/output \
    -mapper "python3 mapper.py" \
    -reducer "python3 reducer.py" \
    -file mapper.py \
    -file reducer.py

# Step 4 - get output from HDFS to local
hadoop fs -get /ipl/output/part-r-00000 /home/hadoop/output/part-00000

echo "Done! Output saved."