#!/bin/bash

value=""
change=""
while read -r line; do
  sym=$(echo "$line" | sed 's/^MarketData{symbol="//;s/"}.*//')
  if [ "$sym" = "ddd" ]; then
    key=$(echo "$line" | sed 's/.*key = "//;s/".*//')
    if [ "$key" = "Value" ]; then
      value=$(echo "$line" | sed 's/.* //')
    elif [ "$key" = "change" ]; then
      change=$(echo "$line" | sed 's/.* //')
    fi
  fi
done < file.txt

echo "value = $value, change = $change"
