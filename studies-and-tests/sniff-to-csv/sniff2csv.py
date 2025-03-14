# Script to generate CSV files directly from packets sniffed on the network
#
# This code uses pypcap to sniff packets on the network and then the scripts of the
# CIC-IoT-2023 dataset supplementary material to save the data to CSV files.
# These scripts use the dpkt library to dissect the packets.
#
# Privileges are required by pypcap to sniff the network.
#
# pypcap repository: https://github.com/pynetwork/pypcap
# CIC-IoT-2023 dataset: https://www.unb.ca/cic/datasets/iotdataset-2023.html
# dpkt repository: https://github.com/kbandla/dpkt

import argparse
import psutil
from resource import *
import time
import threading

import pcap
from scripts_dataset_cic.Feature_extraction_WOPCAP import Feature_extraction

def parse_args():
    '''
        Argument parsing
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('interface', help='Interface to be captured by the sniffer')
    parser.add_argument('-d', '--duration', action='store', default=30,
                        help='Duration of the packet capture in seconds')
    parser.add_argument('-o', '--output', action='store', default='output',
                        help='Name of the CSV output file')
    parser.add_argument('-w', '--window', action='store', default=10,
                        help='CSV packets window size to be sent to the worker thread')
    parser.add_argument('-b', '--buffer', action='store', default=5000,
                        help='Buffer size to hold packets being processed by the worker thread')
    args = parser.parse_args()
    return args

class thread_args():
    '''
        Class to hold the arguments to be shared with the thread
        Permits to work with more than one thread in the future
    '''
    def __init__(self, buf_size):
        self.buf_size = buf_size
        self.buf = [[]] * self.buf_size # Circular buffer that will hold the groups of 10 packets to be processed
        self.front = 0
        self.rear = 0
        self.sem_empty = threading.Semaphore(self.buf_size)
        self.sem_full = threading.Semaphore(0)
        self.stop = threading.Event()
        self.file_name = ''

def main(interface, duration, file_name, window_size, buffer_size):
    '''
        Sniffs the network interface @interface for @duration seconds using pypcap
        and generates a CSV file name @file_name.csv directly from the data captured
    '''
    p = psutil.Process()
    p.cpu_percent(interval=None) # The documentation instructs to ignore the first call for
                                 # this function, as the result from it is computed by comparing
                                 # the current CPU time with the one in the previous call
    io_read_start = psutil.disk_io_counters(perdisk=True)['mmcblk0'][2] # Field read_bytes
    io_write_start = psutil.disk_io_counters(perdisk=True)['mmcblk0'][3] # Field write_bytes

    sniffer = pcap.pcap(name=interface, immediate=True)

    fe = Feature_extraction()
    pkt_buffer = []

    ta = thread_args(buffer_size)
    ta.file_name = file_name
    thread = threading.Thread(target=fe.pcap_evaluation_caller, args=[ta]) # While this code makes the sniff,
    thread.start()                                                         # the thread will process the packets

    print('Starting capture')
    start_time = time.time()

    for ts, buf in sniffer:
        if time.time() - start_time > duration:
            break

        pkt_buffer.append((ts, buf))

        if len(pkt_buffer) >= window_size:
            ta.sem_empty.acquire()
            ta.buf[ta.rear] = pkt_buffer.copy()
            ta.rear = (ta.rear + 1) % ta.buf_size
            ta.sem_full.release()

            pkt_buffer = []

    if len(pkt_buffer) > 0:
        ta.sem_empty.acquire()
        ta.buf[ta.rear] = pkt_buffer.copy()
        ta.rear = (ta.rear + 1) % ta.buf_size
        ta.sem_full.release()

    print("Stopping capture")
    sniffer.close()

    ta.stop.set()
    thread.join()

    end_time = time.time()
    io_read_end = psutil.disk_io_counters(perdisk=True)['mmcblk0'][2] # Field read_bytes
    io_write_end = psutil.disk_io_counters(perdisk=True)['mmcblk0'][3] # Field write_bytes

    print("\nUse of CPU: ", p.cpu_percent(interval=None), "%", sep='')
    print("Memory peak: ", getrusage(RUSAGE_SELF).ru_maxrss, "KB", sep='')
    print("Bytes read from disk:", (io_read_end - io_read_start)/(end_time - start_time), "bytes/s")
    print("Bytes wrote on disk:", (io_write_end - io_write_start)/(end_time - start_time), "bytes/s")

if __name__ == '__main__':
    args = parse_args()
    main(args.interface, int(args.duration), args.output, int(args.window), int(args.buffer))
