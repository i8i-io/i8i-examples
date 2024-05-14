import random
import signal
import time
from fsHelper import set_exit_code, append_to_hostsfile, count_lines, read_lines
import os
import dask
from dask.distributed import Client, SSHCluster, LocalCluster
import dask.dataframe as dd
import json
import pandas as pd
import glob

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

def kendrick_lamar_album_usage(file):
    data = pd.read_csv(file)
    #calculate_average_duration_per_album(data)
    # Filter tracks by Kendrick Lamar as artist
    kendrick_tracks = data[data['track_artist_name'] == 'Kendrick Lamar']

    # Group by album name and count occurrences in playlists
    album_usage = kendrick_tracks.groupby(['track_album_name']).size().reset_index(name='usage_count')

    # Convert the result to a list of dictionaries
    result = album_usage.to_dict(orient='records')

    return result

def sum_usage_count_by_album(data):
    # Concatenate all lists of dictionaries into a single list
    flattened_data = [item for sublist in data for item in sublist]
    
    # Create a DataFrame from the flattened data
    df = pd.DataFrame(flattened_data)
    
    # Group by 'track_album_name' and sum the 'usage_count' for each album
    summed_data = df.groupby('track_album_name')['usage_count'].sum().reset_index()
    
    return summed_data

def processData(client):
    print("processing data")
    start_time = time.time()
    normalized_export_dir = './exports'
    normalized_files = glob.glob(os.path.join(normalized_export_dir, '*.csv'))
    results = client.map(kendrick_lamar_album_usage, normalized_files)
    results = client.gather(results)  
    print("results ", sum_usage_count_by_album(results))

    #me = df.groupby("track_album_name")["track_duration_ms"].mean()
    #count = kendrick_lamar_album_usage(df)
    print("Processing finished after %s seconds ---" % (time.time() - start_time))    
    
if __name__ == "__main__":
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
        cluster = SSHCluster(ip_addresses, connect_options={"known_hosts": None})
    
        # Connect a Dask client to the cluster
        client = Client(cluster)
        print("cluster info: ", client)
        processData(client)
        #cluster.scale(NUM_NODES) 
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
    client = Client(cluster)
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
    results = client.map(kendrick_lamar_album_usage, normalized_files)
    results = client.gather(results)  
    print("results ", sum_usage_count_by_album(results))

    #me = df.groupby("track_album_name")["track_duration_ms"].mean()
    #count = kendrick_lamar_album_usage(df)
    print("--- %s seconds ---" % (time.time() - start_time))    
    """   