#!/usr/bin/env python3
import requests

def send_command(ip, command):
    print(f"Sending command: {command}")
    url = f"http://{ip}:8060/keypress/{command}"
    requests.post(url)

def repeat_commands(ip, commands):
    print(f"Repeating commands sequence: {commands}")
    for _ in range(100):
        for command in commands:
            send_command(ip, command)

ip_address = input("Enter the IP address: ")

# Start of the script
commands = ["powerOn", "powerOff", "powerOn", "powerOff"]
repeat_commands(ip_address, commands)

send_command(ip_address, "powerOn")
send_command(ip_address, "Home")

commands = ["left", "down"]
repeat_commands(ip_address, commands)

print("Can we still be friends?")
