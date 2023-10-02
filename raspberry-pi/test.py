import subprocess
import re

#command = "arp -a | grep 'on wlan0' | awk '{print $2}' | tr -d '()'"
#result = subprocess.run(command, shell=True, capture_output=True, text=True)
#ip_addresses = []
#for line in result.split('\n'):
#    ip_address = match.group(1)
#    ip_addresses.append(ip_address)
#print(ip_addresses)


def get_connected_hosts():
    try:
        output = subprocess.check_output(["arp", "-a"], universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute arp -a command: {e}")
        return []
    
    # A typical line of arp -a output looks like this:
    # ? (192.168.1.1) at 00:1c:42:2e:60:4a [ether] on wlan0
    pattern = re.compile(r"\(([\d\.]+)\) at ([\w:]+) \[ether\] on wlan0")

    ip_addresses = []
    for line in output.split('\n'):
        match = pattern.search(line)
        if match:
            ip_address = match.group(1)
            ip_addresses.append(ip_address)

    return ip_addresses

print(get_connected_hosts())