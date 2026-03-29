import sys

current_player = None
total_runs = 0
total_balls = 0
total_wickets = 0
innings_runs = []
current_innings = []

for line in sys.stdin:
    line = line.strip()
    
    try:
        parts = line.split("\t")
        batter = parts[0]
        runs = int(parts[1])
        wicket = int(parts[2])
    except:
        continue
    
    if current_player == batter:
        total_runs += runs
        total_balls += 1
        current_innings.append(runs)
        if wicket == 1:
            innings_runs.append(sum(current_innings))
            current_innings = []
        total_wickets += wicket
    
    else:
        if current_player:
            if total_wickets > 0:
                average = round(float(total_runs) / total_wickets, 2)
            else:
                average = float(total_runs)
            if total_balls > 0:
                strike_rate = round((float(total_runs) / total_balls) * 100, 2)
            else:
                strike_rate = 0
            last_10 = innings_runs[-10:] if len(innings_runs) >= 10 else innings_runs
            print("%s\t%s\t%s\t%s\t%s\t%s" % (current_player, total_runs, total_balls, average, strike_rate, last_10))
        
        current_player = batter
        total_runs = runs
        total_balls = 1
        current_innings = [runs]
        total_wickets = wicket
        innings_runs = []

if current_player:
    if total_wickets > 0:
        average = round(float(total_runs) / total_wickets, 2)
    else:
        average = float(total_runs)
    if total_balls > 0:
        strike_rate = round((float(total_runs) / total_balls) * 100, 2)
    else:
        strike_rate = 0
    last_10 = innings_runs[-10:] if len(innings_runs) >= 10 else innings_runs
    print("%s\t%s\t%s\t%s\t%s\t%s" % (current_player, total_runs, total_balls, average, strike_rate, last_10))