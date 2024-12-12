#!/usr/bin/env python3
import requests
import socket
import time
import ipaddress
from concurrent.futures import ThreadPoolExecutor
from pywebostv.connection import WebOSClient
from pywebostv.controls import MediaControl
import websocket
import json
from datetime import datetime

ROKU_APP_YOUTUBE_ID = '837'
ROKU_PORT = 8060
SAMSUNG_PORT = 8001
LG_PORT = 3000

NAVIGATION_SEQUENCE_TO_SEARCH = ['Left', 'Up', 'Right', 'Right']
NAVIGATION_SEQUENCE_TO_VIDEO = ['Right', 'Left', 'Down', 'Down', 'Down', 'Down', 'Right', 'Right', 'Select', 'Down', 'Right', 'Select']

def log(message):
    """Log messages with timestamps in a user-friendly format."""
    timestamp = datetime.now().strftime('%I:%M:%S %p')  # 12-hour format
    print(f"[{timestamp}] {message}")

def detect_network():
    """Detect the local subnet."""
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    subnet = ipaddress.IPv4Interface(local_ip + '/24').network
    return subnet

def check_port_open(ip_address, port):
    """Check if a port is open on the given IP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((ip_address, port))
    sock.close()
    return result == 0

def send_roku_command(roku_ip, command):
    """Send a command to a Roku device."""
    try:
        url = f"http://{roku_ip}:{ROKU_PORT}/keypress/{command}"
        response = requests.post(url, timeout=2)
        if response.status_code == 200:
            log(f"Command '{command}' executed successfully on Roku at {roku_ip}")
            return True
        else:
            log(f"Command '{command}' failed on Roku at {roku_ip}. Status code: {response.status_code}, Response: {response.text}")
            return False
    except requests.RequestException as e:
        log(f"Error sending command '{command}' to Roku at {roku_ip}: {e}")
        return False

def roku_search(roku_ip, search_query):
    """Perform a YouTube search on a Roku device."""
    log(f"Starting search on Roku at {roku_ip}")

    # Power on the Roku device
    if not send_roku_command(roku_ip, 'PowerOn'):
        log("Failed to power on the Roku.")
        return False
    time.sleep(5)

    # Launch the YouTube app
    log(f"Attempting to launch YouTube app on Roku at {roku_ip}")
    youtube_launch_url = f"http://{roku_ip}:{ROKU_PORT}/launch/{ROKU_APP_YOUTUBE_ID}"
    try:
        response = requests.post(youtube_launch_url, timeout=10)
        if response.status_code == 200:
            log(f"YouTube app launched successfully on Roku at {roku_ip}")
        else:
            log(f"Failed to launch YouTube app on Roku at {roku_ip}. Status code: {response.status_code}, Response: {response.text}")
            return False
    except requests.RequestException as e:
        log(f"Error while launching YouTube app on Roku at {roku_ip}: {e}")
        return False

    time.sleep(5)  # Allow the app to load

    # Navigate to the search bar
    log("Navigating to the search bar on YouTube...")
    for remote_button in NAVIGATION_SEQUENCE_TO_SEARCH:
        if not send_roku_command(roku_ip, remote_button):
            return False
        time.sleep(0.5)

    # Enter the search query
    log(f"Entering search query '{search_query}' on Roku at {roku_ip}")
    for character in search_query:
        if not send_roku_command(roku_ip, f'Lit_{character}'):
            return False
        time.sleep(0.2)

    # Navigate to the video and select it
    log("Navigating to the video...")
    for remote_button in NAVIGATION_SEQUENCE_TO_VIDEO:
        if not send_roku_command(roku_ip, remote_button):
            return False
        time.sleep(0.5)

    log(f"Search completed successfully on Roku at {roku_ip}")
    return True
    
def send_samsung_command(samsung_ip, command):
    """Send a WebSocket command to a Samsung TV."""
    try:
        url = f"ws://{samsung_ip}:{SAMSUNG_PORT}/api/v2/channels/samsung.remote.control"
        ws = websocket.create_connection(url, timeout=5)
        payload = {
            "method": "ms.remote.control",
            "params": {
                "Cmd": "Click",
                "DataOfCmd": command,
                "Option": "false",
                "TypeOfRemote": "SendRemoteKey"
            }
        }
        ws.send(json.dumps(payload))
        ws.close()
        log(f"Sent command {command} to Samsung TV at {samsung_ip}")
        return True
    except Exception as e:
        log(f"Failed to send command to Samsung TV at {samsung_ip}: {e}")
        return False

def lg_control(lg_ip, search_query):
    """Perform a YouTube search on an LG TV."""
    try:
        client = WebOSClient(lg_ip)
        client.connect()
        media = MediaControl(client)
        log(f"Searching YouTube on LG TV at {lg_ip}")
        media.play_youtube_video(search_query)
        return True
    except Exception as e:
        log(f"Failed to control LG TV at {lg_ip}: {e}")
        return False

def identify_device(ip_address):
    """Identify the type of device on the network."""
    if check_port_open(ip_address, ROKU_PORT):
        return "Roku"
    if check_port_open(ip_address, SAMSUNG_PORT):
        return "Samsung"
    if check_port_open(ip_address, LG_PORT):
        return "LG"
    return None

def scan_and_control(ip_address, search_query):
    """Scan and control devices in the network."""
    log(f"Scanning IP: {ip_address}")
    device_type = identify_device(ip_address)
    if device_type == "Roku":
        roku_search(ip_address, search_query)
    elif device_type == "Samsung":
        log(f"Samsung TV found at {ip_address}. Sending test command.")
        send_samsung_command(ip_address, "KEY_HOME")
    elif device_type == "LG":
        lg_control(ip_address, search_query)
    else:
        log(f"No compatible device found at {ip_address}")

def multi_tv_scan(search_query, network=None):
    """Scan a network and control detected TVs."""
    if not network:
        network = detect_network()

    log(f"Scanning network: {network}")
    with ThreadPoolExecutor(max_workers=10) as executor:
        for ip_address in network:
            executor.submit(scan_and_control, str(ip_address), search_query)

if __name__ == "__main__":
    search_query = input("Enter YouTube search query: ").strip()
    network_input = input("Enter network range (e.g., 192.168.1.0/24 or press Enter to auto-detect): ").strip()

    network = ipaddress.ip_network(network_input, strict=False) if network_input else None

    if not search_query:
        log("Please provide a valid YouTube search query.")
    else:
        multi_tv_scan(search_query, network)
