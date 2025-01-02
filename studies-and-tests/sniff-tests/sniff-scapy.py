# Scapy sniffer test

# This code implements a network TCP packet counter using the Scapy sniffer,
# with the intention to measure the library performance handling live traffic on a Raspberry Pi.

# Scapy website: https://scapy.net/

from scapy.all import *
import psutil
from resource import *

p = psutil.Process()
p.cpu_percent(interval=None) # The documentation instructs to ignore the first call for
                             # this function, as the result from it is computed by comparing
                             # the current CPU time with the one in the previous call

# Realizing the capture
counter = 0 # Count how many packets were processed
counter_tcp = 0 # How many of them were using TCP

def callback(pkt):
    global counter
    global counter_tcp
    counter += 1
    if pkt.haslayer(TCP):
        counter_tcp += 1

print("Starting capture")
#sniff(iface="lo", prn=callback, store=0, timeout=50) # Loopback
sniff(iface="eth0", prn=callback, store=0, timeout=50) # Ethernet

print("Total packets processed:", counter)
print("Total of TCP packets:", counter_tcp)
print()

# Metrics
print("Use of CPU: ", p.cpu_percent(interval=None), "%", sep='')
print("Memory peak: ", getrusage(RUSAGE_SELF).ru_maxrss, "KB", sep='')
