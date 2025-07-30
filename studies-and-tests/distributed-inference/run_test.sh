#!/bin/bash

# Experiment to perform the inference and training of a model on different machines.
# This script must be executed on the training machine. The model parameters will
# be shared through an ssh connection.
# Necessary to configure the user and IP of the inference machine below.

if [ $# -ne 6 ]; then
  printf "$0: arguments mismatch\n"
  printf "Parameters:\n\
  1. Python path in training machine;\n\
  2. Training script path;\n\
  3. Model parameters path in training machine;\n\
  4. Python path in inference machine;\n\
  5. Inference script path;\n\
  6. Model parameters path in the inference machine.\n"
  exit 1
fi

for i in {1..5} # Five iterations
do
  printf "============================== Test case $i ==============================\n"
  printf "[!] Start: "
  date +"%F %T.%N"
  printf "\n\n"

  printf "[!] Training\n\n"
  time $1 $2 $3

  printf "\n[!] Transfering the parameters to the inference machine\n\n"
  scp $3 user@ip:$6

  printf "\n[!] Performing inference\n\n"
  ssh user@ip "time $4 $5 $6"

  printf "\n[!] End: "
  date +"%F %T.%N"
  printf "\n\n"
done

