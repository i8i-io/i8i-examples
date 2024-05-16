import random
import time
import os
import json
import pandas as pd
import glob 

normalized_export_dir = '/output'

def normalize_csv_file(file):
    data = json.load(open(file))
    data = data["playlists"]
    df = pd.json_normalize(data, 'tracks', [ "pid", ], 
                    record_prefix='track_')
    r1 = random.randint(0, 100000)
    df.to_csv(f'{normalized_export_dir}/{r1}-export.csv')
    return df
    
if __name__ == "__main__":
    start_time = time.time()
    directory = "/input/Data ingestion/data"

    json_files = glob.glob(os.path.join(directory, '*.json'))
    json_files = json_files[:20]
    print("json files: ", json_files)
    for json_file in json_files:
        normalize_csv_file(json_file)
    
    print("--- %s seconds ---" % (time.time() - start_time))    
