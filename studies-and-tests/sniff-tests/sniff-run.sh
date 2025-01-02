#!/bin/bash

if [ $# -ne 3 ]; then
  echo "Usage: '$0 [Python interpreter path] [Python script path] [server IP]'"
  exit 1
fi

for i in {1..5} # Five iterations
do
  printf "Test case $i ==============================\n"

  time $1 $2 & # Running the Python sniffer script in background
  pid=$!

  sleep 10

  #iperf3 -c $3 --time 10 --verbose # TCP
  #iperf3 -c $3 --time 10 --verbose --udp --bitrate 1M # UDP with bitrate limit (set it to 0 for unlimited)
  iperf3 -c $3 --time 10 --verbose --udp --bitrate 5M --length 1168 # UDP with bitrate limit and packet length defined (in bytes)

  sleep 32
  ping $3 -c 1 > /dev/null # Just to break the pypcap loop, since it
                           # doesn't have its own timeout mechanism

  wait $pid 2> /dev/null # Ensure the Python process has ended

  printf "\n\n"
done

