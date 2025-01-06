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

  # TCP
  iperf3 -c $3 --time 10 --verbose

  # UDP with bitrate limit (set it to 0 for unlimited)
  #iperf3 -c $3 --time 10 --verbose --udp --bitrate 1M

  # UDP with number of packets and length defined
  #iperf3 -c $3 --verbose --udp --bitarate 2M --blockcount 1000 --length 148 &
  #sleep 10

  sleep 32
  ping $3 -c 1 > /dev/null # Just to break the pypcap loop, since it
                           # doesn't have its own timeout mechanism

  wait $pid 2> /dev/null # Ensure the Python process has ended

  printf "\n\n"
done

