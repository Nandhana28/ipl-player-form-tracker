import sys

for line in sys.stdin:
    line = line.strip()
    
    if line.startswith("ID"):
        continue
    
    fields = line.split(",")
    
    try:
        batter = fields[4]
        batsman_run = fields[8]
        is_wicket = fields[12]
        
        print("%s\t%s\t%s" % (batter, batsman_run, is_wicket))
    
    except IndexError:
        continue