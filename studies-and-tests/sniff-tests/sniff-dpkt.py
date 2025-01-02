# pypcap + dpkt sniffer test

# This code implements a network TCP packet counter using the pypcap sniffer and dpkt to process the packets,
# with the intention to measure the library performance handling live traffic on a Raspberry Pi.

# pypcap repository: https://github.com/pynetwork/pypcap
# dpkt repository: https://github.com/kbandla/dpkt

import pcap
import dpkt
import psutil
from resource import *
import time

p = psutil.Process()
p.cpu_percent(interval=None) # The documentation instructs to ignore the first call for
                             # this function, as the result from it is computed by comparing
                             # the current CPU time with the one in the previous call

# Realizing the capture
counter = 0 # Count how many packets were processed
counter_tcp = 0 # How many of them were using TCP

#sniffer = pcap.pcap(name='lo', immediate=True) # Loopback
sniffer = pcap.pcap(name='eth0', immediate=True) # Ethernet

print('Starting capture')
start_time = time.time()
for ts, pkt in sniffer:
    if time.time() - start_time > 50:
        break

    counter += 1
    eth = dpkt.ethernet.Ethernet(pkt)
    if(isinstance(eth.data, dpkt.ip.IP) and eth.data.p == dpkt.ip.IP_PROTO_TCP):
        counter_tcp += 1

sniffer.close()

print("Total packets processed:", counter)
print("Total of TCP packets:", counter_tcp)
print()

# Metrics
print("Use of CPU: ", p.cpu_percent(interval=None), "%", sep='')
print("Memory peak: ", getrusage(RUSAGE_SELF).ru_maxrss, "KB", sep='')
