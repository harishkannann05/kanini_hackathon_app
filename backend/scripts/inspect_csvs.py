
import pandas as pd
import os
import glob
import json

dataset_dir = r"d:\college-projects\kanini-hackathon\dataset2"
csv_files = glob.glob(os.path.join(dataset_dir, "*.csv"))

headers = {}
for f in csv_files:
    try:
        df = pd.read_csv(f, nrows=0) # Only read header
        headers[os.path.basename(f)] = list(df.columns)
    except Exception as e:
        headers[os.path.basename(f)] = str(e)

with open(r"d:\college-projects\kanini-hackathon\backend\scripts\dataset_headers.json", "w") as f:
    json.dump(headers, f, indent=4)
