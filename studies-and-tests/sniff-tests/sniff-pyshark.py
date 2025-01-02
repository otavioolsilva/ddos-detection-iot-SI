# pyshark sniffer test

# This code implements a network TCP packet counter using the pyshark sniffer,
# with the intention to measure the library performance handling live traffic on a Raspberry Pi.

# pyshark repository: https://github.com/KimiNewt/pyshark

import pyshark
import psutil
from resource import *
import concurrent

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
    if hasattr(pkt, "tcp"):
        counter_tcp += 1

#capture = pyshark.LiveCapture(interface='lo') # Loopback
capture = pyshark.LiveCapture(interface='eth0') # Ethernet

print("Starting capture")
try:
    capture.apply_on_packets(callback, timeout=50)
except concurrent.futures._base.TimeoutError as e:
    pass # Timeout hit

print("Total packets processed:", counter)
print("Total of TCP packets:", counter_tcp)
print()

# Metrics
print("Use of CPU: ", p.cpu_percent(interval=None), "%", sep='')
print("Memory peak: ", getrusage(RUSAGE_SELF).ru_maxrss, "KB", sep='')
