#!/usr/bin/env python3
import requests
import socket
import time
import ipaddress
import argparse
from concurrent.futures import ThreadPoolExecutor

ROKU_APP_YOUTUBE_ID = '837'
NAVIGATION_SEQUENCE_TO_SEARCH = ['Left', 'Up', 'Right', 'Right']
NAVIGATION_SEQUENCE_TO_VIDEO = ['Right', 'Left', 'Down', 'Down', 'Down', 'Down', 'Right', 'Right', 'Select', 'Down', 'Right', 'Select']

def send_remote_control_command(roku_ip, remote_button):
    url = f"http://{roku_ip}:8060/keypress/{remote_button}"
    try:
        response = requests.post(url, timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

def launch_app_on_roku(roku_ip, app_id):
    url = f"http://{roku_ip}:8060/launch/{app_id}"
    try:
        response = requests.post(url, timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

def search_on_youtube(roku_ip, search_query):
    try:
        print(f"Turning on Roku at {roku_ip}...")
        if not send_remote_control_command(roku_ip, 'PowerOn'):
            print("Failed to turn on the TV.")
            return False

        time.sleep(5)

        print("Launching YouTube app...")
        if not launch_app_on_roku(roku_ip, ROKU_APP_YOUTUBE_ID):
            print("Failed to launch YouTube app.")
            return False

        time.sleep(5)

        print("Navigating to the search bar...")
        for remote_button in NAVIGATION_SEQUENCE_TO_SEARCH:
            if not send_remote_control_command(roku_ip, remote_button):
                return False
            time.sleep(0.5)

        print(f"Entering search query: {search_query}")
        for character in search_query:
            if not send_remote_control_command(roku_ip, f'Lit_{character}'):
                return False
            time.sleep(0.2)

        print("Selecting the video...")
        for remote_button in NAVIGATION_SEQUENCE_TO_VIDEO:
            if not send_remote_control_command(roku_ip, remote_button):
                return False
            time.sleep(0.5)

        print(f"Search completed successfully for Roku at {roku_ip}.")
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def check_port_open(ip_address, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((ip_address, port))
    sock.close()
    return result == 0

def detect_network():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    subnet = ipaddress.IPv4Interface(local_ip + '/24').network
    return subnet

def roku_ip_scan(search_query, network=None):
    if not network:
        network = detect_network()

    print(f"Scanning network: {network}")
    with ThreadPoolExecutor(max_workers=10) as executor:
        for ip_address in network:
            executor.submit(scan_and_search, str(ip_address), search_query)

def scan_and_search(ip_address, search_query):
    print(f"Scanning IP: {ip_address}", end='\r')
    if check_port_open(ip_address, 8060):
        print(f"Found Roku device at {ip_address}")
        if not search_on_youtube(ip_address, search_query):
            print(f"Search failed for {ip_address}")
    else:
        print(f"No Roku at {ip_address}", end='\r')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control Roku and perform YouTube searches.")
    parser.add_argument("-q", "--query", type=str, required=True, help="YouTube search query")
    parser.add_argument("-n", "--network", type=str, help="Network range in CIDR format (e.g., 192.168.1.0/24)")

    args = parser.parse_args()
    search_query = args.query.strip()
    network = ipaddress.ip_network(args.network, strict=False) if args.network else None

    if not search_query:
        print("Please provide a valid YouTube search query.")
    else:
        roku_ip_scan(search_query, network)
