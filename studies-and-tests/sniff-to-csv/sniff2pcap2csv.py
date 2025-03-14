# Script to generate a CSV file from packets sniffed on the network saved in a PCAP file
#
# This code uses pyshark (a python wrapper for tshark) to sniff packets on the network
# and save them in a PCAP file. Then, the scripts of the CIC-IoT-2023 dataset supplementary
# material are used to convert the data to CSV files. Theses scripts use the dpkt library
# to dissect the packets.
# 
# Doesn't need to be executed with privileges, but the user must be on the 'wireshark' group.
#
# pyshark repository: https://github.com/KimiNewt/pyshark
# CIC-IoT-2023 dataset: https://www.unb.ca/cic/datasets/iotdataset-2023.html
# dpkt repository: https://github.com/kbandla/dpkt

import argparse
import time
import psutil
from resource import *

import pyshark
from scripts_dataset_cic.Generating_dataset import main as pcap2csv

def parse_args():
    '''
        Argument parsing
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('interface', help='Interface to be captured by the sniffer')
    parser.add_argument('-d', '--duration', action='store', default=30,
                        help='Duration of the packet capture in seconds')
    parser.add_argument('-o', '--output', action='store', default='output',
                        help='Name of the PCAP and CSV output files (without extension)')
    args = parser.parse_args()
    return args

def main(interface, duration, file_name):
    '''
        Sniffs the network interface @interface for @duration seconds using Pyshark
        and generates a PCAP file named @file_name.pcap. After that, converts it
        to a CSV file named @file_name.pcap.csv.
    '''
    p = psutil.Process()
    p.cpu_percent(interval=None) # The documentation instructs to ignore the first call for
                                 # this function, as the result from it is computed by comparing
                                 # the current CPU time with the one in the previous call
    io_read_start = psutil.disk_io_counters(perdisk=True)['mmcblk0'][2] # Field read_bytes
    io_write_start = psutil.disk_io_counters(perdisk=True)['mmcblk0'][3] # Field write_bytes

    capture = pyshark.LiveCapture(interface=interface, output_file=file_name+'.pcap')
    print("Starting capture")
    start_time = time.time()
    capture.sniff(timeout=duration)
    print("Stopping capture")

    print("Starting the conversion PCAP -> CSV")
    pcap2csv([file_name+'.pcap'], 3) # Using at most 3/4 CPU threads

    end_time = time.time()
    io_read_end = psutil.disk_io_counters(perdisk=True)['mmcblk0'][2] # Field read_bytes
    io_write_end = psutil.disk_io_counters(perdisk=True)['mmcblk0'][3] # Field write_bytes

    print("\nUse of CPU: ", p.cpu_percent(interval=None), "%", sep='')
    print("Memory peak: ", getrusage(RUSAGE_SELF).ru_maxrss, "KB", sep='')
    print("Bytes read from disk:", (io_read_end - io_read_start)/(end_time - start_time), "bytes/s")
    print("Bytes wrote on disk:", (io_write_end - io_write_start)/(end_time - start_time), "bytes/s")

if __name__ == '__main__':
    args = parse_args()
    main(args.interface, int(args.duration), args.output)

