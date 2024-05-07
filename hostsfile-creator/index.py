import socket
if __name__ == "__main__":
   private_ip = socket.gethostbyname(socket.gethostname())
   print("ipaddress", private_ip)