import socket
import fcntl

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