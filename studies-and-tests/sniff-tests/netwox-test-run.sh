#!/bin/bash

# Script to be executed in the target computer, responsible for triggering the attack and
# running the Python sniffer scripts.

if [ $# -ne 4 ]; then
  echo "Usage: '$0 [Python interpreter path] [Python sniffer script path] [attacker IP] [target IP]'"
  exit 1
fi

for i in {1..5} # Five iterations
do
  printf "Test case $i ===============================\n"

  time $1 $2 & # Running the Python sniffer script in background
  sniffer_pid=$!

  sleep 10

  printf "Starting attack\n"
  timeout 30s netwox 76 -i $4 -p 5201 # netwox in localhost
  #ssh root@$3 "timeout 30s netwox 76 -i $4 -p 5201" # netwox in a remote computer
  printf "Attack ended\n"

  sleep 32

  ping $4 -c 1 > /dev/null # Just to break the pypcap loop, since it
                           # doesn't have its own timeout mechanism

  wait $sniffer_pid 2> /dev/null # Ensure the Python process has ended

  printf "\n\n"
done

