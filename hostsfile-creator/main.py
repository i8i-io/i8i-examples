import socket
import fcntl
import os
def append_to_hostsfile():
   ip_address = socket.gethostbyname(socket.gethostname())
   print("ipaddress", ip_address)
   hostsfile = "/input/hostsfile"
   lockfile = "/input/hostsfile.lock"
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
if __name__ == "__main__":
   append_to_hostsfile()