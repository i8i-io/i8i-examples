import random
import signal
import time
import os
import dask
from dask.distributed import Client, SSHCluster, LocalCluster
import dask.dataframe as dd
import json
import pandas as pd
import glob
import socket
import fcntl
import multiprocessing

#################### FS ops 
AWS_BATCH_EXIT_CODE_FILE="/tmp/batch-exit-code"

def append_to_hostsfile(hostsfile):
   ip_address = socket.gethostbyname(socket.gethostname())
   print("ipaddress", ip_address)
   lockfile = hostsfile + ".lock"
   if not os.path.exists(hostsfile):
       with open(hostsfile, "w") as f:
           pass
   if not os.path.exists(lockfile):
       with open(lockfile, "w") as f:
           pass
   
   # Acquire advisory lock
   with open(lockfile, "w") as f:
       fcntl.flock(f, fcntl.LOCK_EX)
       
       # Append IP address to hostsfile
       with open(hostsfile, "a") as hosts:
           hosts.write(ip_address + "\n")
       
       # Release lock
       fcntl.flock(f, fcntl.LOCK_UN)
       
def count_lines(file_path):
    try:
        with open(file_path, 'r') as file:
            line_count = sum(1 for _ in file)
        return line_count
    except FileNotFoundError:
        print("Error: File not found.")
        return 0
     
def read_lines(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = [line.strip() for line in file.readlines()]
        return lines
    except FileNotFoundError:
        print("Error: File not found.")
        return []

def set_exit_code(code):
    file = open(AWS_BATCH_EXIT_CODE_FILE, "w")  
    file.write(code)
    
##############################
#ARRAY_SIZE = int(os.environ.get('AWS_BATCH_JOB_ARRAY_SIZE', "5"))
#ARRAY_INDEX = int(os.environ.get('AWS_BATCH_JOB_ARRAY_INDEX',"0"))
JOB_INDEX = int(os.environ.get('AWS_BATCH_JOB_NODE_INDEX',"0"))
NUM_NODES = int(os.environ.get('AWS_BATCH_JOB_NUM_NODES',"1"))
MAIN_NODE_INDEX = int(os.environ.get('AWS_BATCH_JOB_MAIN_NODE_INDEX',"0"))
def normalize_csv_file(file):
    data = json.load(open(file))
    data = data["playlists"]
    df = pd.json_normalize(data, 'tracks', [ "pid", ], 
                    record_prefix='track_')
    r1 = random.randint(0, 100000)
    return df
    df.to_csv(f'./exports/{r1}-export.csv')

def calculate_average_duration_per_album(data):
    # Create a DataFrame from the data
    df  = data
    
    # Convert duration to minutes
    df['duration_minutes'] = df['track_duration_ms'] / (60 * 1000)
    
    # Group by 'album' and calculate the mean duration for each album
    average_duration_per_album = df.groupby('track_album_name')['duration_minutes'].mean().reset_index()
    
    return average_duration_per_album

def artist_album_usage(file, artist_name):
    start = time.time()
    print("artist_name: ", file, artist_name)
    data = pd.read_csv(file)
    #calculate_average_duration_per_album(data)
    artist_tracks = data[data['track_artist_name'] == artist_name]
    print("tracks ", artist_tracks)
    stop = time()
    dask.distributed.get_worker().log_event("runtimes", {"start": start, "stop": stop})
    if len(artist_tracks == 0):
        return []
    # Group by album name and count occurrences in playlists
    album_usage = artist_tracks.groupby(['track_album_name']).size().reset_index(name='usage_count')

    # Convert the result to a list of dictionaries
    result = album_usage.to_dict(orient='records')

    return result

def sum_usage_count_by_album(data):
    # Concatenate all lists of dictionaries into a single list
    flattened_data = [item for sublist in data for item in sublist]
    
    # Create a DataFrame from the flattened data
    df = pd.DataFrame(flattened_data)
    if len(df) == 0:
        return "No album found"
    # Group by 'track_album_name' and sum the 'usage_count' for each album
    summed_data = df.groupby('track_album_name')['usage_count'].sum().reset_index()
    
    return summed_data

def processData(client):
    print("processing data")
    start_time = time.time()
    normalized_export_dir = '/input/Data normalize'
    normalized_files = glob.glob(os.path.join(normalized_export_dir, '*.csv'))
    results = client.map(artist_album_usage, normalized_files, "Kendrick Lamar")
    results = client.gather(results)  
    logs = client.get_events("runtimes")
    print("logs: ", logs)
    print("Processing finished after %s seconds ---" % (time.time() - start_time))    
    return sum_usage_count_by_album(results)
    
if __name__ == "__main__":
    cpu_count = multiprocessing.cpu_count()
    print("cpu_count: ", cpu_count)
    start_time = time.time()
    hostsfile = "/input/mpi/hostsfile"
    nodes_joined = count_lines(hostsfile)
    print("nodes_joined", nodes_joined)
    if JOB_INDEX == MAIN_NODE_INDEX:
        while nodes_joined < NUM_NODES-1:
            nodes_joined = count_lines(hostsfile)
            print("nodes joined: ", nodes_joined)
            time.sleep(3)
        print("all nodes joined.")
        ip_addresses = read_lines(hostsfile)
        print("ip_addresses:", ip_addresses)
        supervisord_pid = read_lines("/tmp/supervisord.pid")
        print("supervisord_pid:", supervisord_pid)
        # Set up SSHCluster with provided IP addresses
        cluster = SSHCluster(ip_addresses, connect_options={"known_hosts": None}, worker_options={"nthreads": cpu_count, "n_workers": NUM_NODES-1})
    
        # Connect a Dask client to the cluster
        client = Client(cluster)
        cluster.scale(NUM_NODES-1) 
        
        print("cluster info: ", client)
        result = processData(client)
        print("result: ", result)
        set_exit_code("0")
        os.kill(int(supervisord_pid[0]), signal.SIGTERM)
        exit(1)
    else:
        print("reporting to master")
        append_to_hostsfile(hostsfile)
        
        
"""
if __name__ == "__main__":
    cluster = LocalCluster()
    # Connect a Dask client to the cluster
    client = Client(cluster )
    #cluster.scale(5)
    print(client)
    start_time = time.time()
    directory = '/Users/onuracikelli/Desktop/spotify_million_playlist_dataset/data/'
    normalized_export_dir = './exports'

    #json_files = glob.glob(os.path.join(directory, '*.json'))
    #json_files = json_files[:1]
    #print(len(json_files))

   
    
    #results = client.map(normalize_csv_file, json_files)
    #results = client.gather(results)  
    #print("results: ", results)
    print("--- %s seconds ---" % (time.time() - start_time))    


    #print(df.describe())
    #latmax, lonmax = dask.compute(df.track_duration_ms.mean(), df.loc[df["track_duration_ms"].idxmax(), df.groupby("pid",).mean()])
    #print(latmax, lonmax.track_duration_ms  == 2172761)
    normalized_files = glob.glob(os.path.join(normalized_export_dir, '*.csv'))
    results = client.map(kendrick_lamar_album_usage, normalized_files, "s")
    results = client.gather(results)  
    print("results ", sum_usage_count_by_album(results))

    #me = df.groupby("track_album_name")["track_duration_ms"].mean()
    #count = kendrick_lamar_album_usage(df)
    print("--- %s seconds ---" % (time.time() - start_time))    
"""
