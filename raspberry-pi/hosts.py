import subprocess
import re

# Function to get the IP address of devices connected to the Raspberry Pi's Access Point (wlan0 interface)
def get_connected_hosts():
    try:
        # We execute the command "arp -a to get all hosts"
        output = subprocess.check_output(["arp", "-a"], universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute arp -a command: {e}")
        return []
    
    # We filter it down to hosts connected to wlan0
    pattern = re.compile(r"\(([\d\.]+)\) at ([\w:]+) \[ether\] on wlan0")

    ip_addresses = []
    for line in output.split('\n'):
        match = pattern.search(line)
        if match:
            ip_address = match.group(1)
            ip_addresses.append(ip_address)

    return ip_addresses