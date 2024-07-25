import time
import os
import socket
import fcntl
import multiprocessing

def append_to_hostsfile(hostsfile, max_retries=5, retry_delay=1):
    ip_address = f'Reporting from {socket.gethostbyname(socket.gethostname())}, I have {multiprocessing.cpu_count()} CPUs'
    lockfile = hostsfile + ".lock"
    
    if not os.path.exists(hostsfile):
        with open(hostsfile, "w") as f:
            pass
    if not os.path.exists(lockfile):
        with open(lockfile, "w") as f:
            pass
    
    retries = 0
    while retries < max_retries:
        try:
            # Attempt to acquire advisory lock
            with open(lockfile, "w") as f:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                
                # Append IP address to hostsfile
                with open(hostsfile, "a") as hosts:
                    hosts.write(ip_address + "\n")
                
                # Release lock
                fcntl.flock(f, fcntl.LOCK_UN)
            
            print("Successfully appended IP address to hostsfile")
            return True
        except IOError:
            print(f"Lock acquisition failed. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retries += 1
    
    print(f"Failed to acquire lock after {max_retries} attempts")
    return False

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

JOB_INDEX = int(os.environ.get('AWS_BATCH_JOB_NODE_INDEX',"0"))
NUM_NODES = int(os.environ.get('AWS_BATCH_JOB_NUM_NODES',"1"))
MAIN_NODE_INDEX = int(os.environ.get('AWS_BATCH_JOB_MAIN_NODE_INDEX',"0"))

if __name__ == "__main__":
    hostsfile = "/input/shared/mpi/hostsfile"
    nodes_joined = count_lines(hostsfile)
    if JOB_INDEX == MAIN_NODE_INDEX:
        while nodes_joined < NUM_NODES-1:
            nodes_joined = count_lines(hostsfile)
            print("Total nodes joined: ", nodes_joined)
            time.sleep(3)
        print("All nodes joined.")
    else:
        print("Reporting to master.")
        append_to_hostsfile(hostsfile)
        
        

