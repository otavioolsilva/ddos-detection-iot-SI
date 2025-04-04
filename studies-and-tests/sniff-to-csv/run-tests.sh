#!/bin/bash

if [ $# -ne 2 ]; then
  echo "Usage: '$0 [Python interpreter path] [server IP]'"
  exit 1
fi

run() {
  for i in {1..5}; do # Five iterations
    printf "'$1' - Bitrate $3: Test case $i ==============================\n"

    time $1 & # Running the Python sniffer script in background
    pid=$!

    sleep 20 # Waiting 20s before start the network flow, the Python script takes a long time to start

    # iperf UDP
    iperf3 -c $2 --time 10 --verbose --udp --bitrate $3

    sleep 15
    ping $2 -c 1 > /dev/null # Just to break the pypcap loop, since it
                              # doesn't have its own timeout mechanism

    wait $pid 2> /dev/null # Ensure the Python process has ended

    printf "Number of lines in the output file: "
    wc -l *.csv # Count the number of lines in the output file
    sudo rm -f *.csv *.pcap # Remove the output files

    printf "\n\n"
  done
}

for bitrate in 5M 10M 15M 20M 25M; do
  printf "====================== BITRATE $bitrate ======================\n\n"
  
  printf "Running tests on sniff2csv.py with limited window\n\n"
  command="sudo $1 sniff2csv.py eth0 --duration 30 --window 10 --buffer 5000"
  run "$command" $2 $bitrate

  printf "Running tests on sniff2csv.py with unlimited window\n\n"
  command="sudo $1 sniff2csv.py eth0 --duration 30 --window 50000 --buffer 10"
  run "$command" $2 $bitrate
  
  printf "Running tests on sniff2pcap2csv.py\n\n"
  command="$1 sniff2pcap2csv.py eth0 --duration 30"
  run "$command" $2 $bitrate

  printf "\n\n\n"
done
