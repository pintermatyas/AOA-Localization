#!/bin/bash

file="/home/pi/Downloads/AOA-Localization/raspberry-pi/measurements/accuracy.csv"

threshold=$1

less_than_one_count=0
more_than_one_count=0

while IFS=, read -r col1 _; do
  if [[ $col1 =~ ^[0-9]+([.][0-9]+)?$ ]]; then
    if (( $(awk 'BEGIN {print ("'$col1'" < '$threshold')}') )); then
      ((less_than_one_count++))
    elif (( $(awk 'BEGIN {print ("'$col1'" > '$threshold')}') )); then
      ((more_than_one_count++))
    fi
  fi
done < "$file"

# Print the results
echo "Accuracy values less than $threshold: $less_than_one_count"
echo "Accuracy values more than $threshold: $more_than_one_count"
