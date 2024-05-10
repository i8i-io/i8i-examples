import signal
import socket
import fcntl
import os
from dask.distributed import Client, SSHCluster
import time

#ARRAY_SIZE = int(os.environ.get('AWS_BATCH_JOB_ARRAY_SIZE', "5"))
#ARRAY_INDEX = int(os.environ.get('AWS_BATCH_JOB_ARRAY_INDEX',"0"))
JOB_INDEX = int(os.environ.get('AWS_BATCH_JOB_NODE_INDEX',"0"))
NUM_NODES = int(os.environ.get('AWS_BATCH_JOB_NUM_NODES',"1"))
MAIN_NODE_INDEX = int(os.environ.get('AWS_BATCH_JOB_MAIN_NODE_INDEX',"0"))

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
        return None
     
def read_lines(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = [line.strip() for line in file.readlines()]
        return lines
    except FileNotFoundError:
        print("Error: File not found.")
        return None
     
if __name__ == "__main__":
   hostsfile = "/input/mpi/hostsfile"
   append_to_hostsfile(hostsfile)
   nodes_joined = count_lines(hostsfile)
   nodes_joined = count_lines(hostsfile)
   print("nodes_joined", nodes_joined)

   if JOB_INDEX == MAIN_NODE_INDEX:
      while nodes_joined < NUM_NODES:
         nodes_joined = count_lines(hostsfile)
         print("nodes joined: ", nodes_joined)
         time.sleep(6)
      print("all nodes joined.")
      ip_addresses = read_lines(hostsfile)
      print("ip_addresses:", ip_addresses)
      supervisord_pid = read_lines("/tmp/supervisord.pid")
      print("supervisord_pid:", supervisord_pid)

      # Set up SSHCluster with provided IP addresses
      cluster = SSHCluster(ip_addresses)

      # Connect a Dask client to the cluster
      client = Client(cluster)
      cluster.scale(NUM_NODES)  # scaling to 10 workers
      os.kill(supervisord_pid[0], signal.SIGTERM)
      exit(1)