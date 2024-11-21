#!/bin/bash

if [ $# -ne 3 ]; then
  echo "$0: erro com operadores"
  echo "Formato: '$0 [caminho python] [caminho script] [IP servidor]'"
  exit 1
fi

for i in {1..5}
do
  printf "Test case $i ==============================\n"

  time $1 $2 & # Rodando o sniffer em python em background
  pid=$!

  sleep 10

  iperf3 -c $3 --time 10 --verbose
  #iperf3 -c $3 --time 10 --verbose --udp --bitrate 1M

  sleep 32
  ping $3 -c 1 > /dev/null # Apenas para quebrar o loop do pypcap,
                           # que não possui mecanismo de timeout próprio

  wait $pid 2> /dev/null # Garantir que o processo do python acabou

  printf "\n\n"
done

