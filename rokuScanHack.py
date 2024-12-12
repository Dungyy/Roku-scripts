#!/usr/bin/env python3
import requests
import socket
import time
import ipaddress

ROKU_APP_YOUTUBE_ID = '837'
NAVIGATION_SEQUENCE_TO_SEARCH = ['Left', 'Up', 'Right', 'Right']
NAVIGATION_SEQUENCE_TO_VIDEO = ['Right', 'Left', 'Down', 'Down', 'Down', 'Down', 'Right', 'Right', 'Select', 'Down', 'Right', 'Select']

def send_remote_control_command(roku_ip, remote_button):
    url = f"http://{roku_ip}:8060/keypress/{remote_button}"
    print(f"Sending command: {remote_button}")
    response = requests.post(url)
    return response.status_code == 200

def launch_app_on_roku(roku_ip, app_id):
    url = f"http://{roku_ip}:8060/launch/{app_id}"
    print(f"Launching app: {app_id}")
    response = requests.post(url)
    return response.status_code == 200

def search_on_youtube(roku_ip, search_query):
    try:
        # Turn on the TV
        print("Turning on the TV...")
        if not send_remote_control_command(roku_ip, 'PowerOn'):
            print("Failed to turn on the TV.")
            return False

        time.sleep(5)  # Wait for the TV to turn on

        # Launch YouTube app
        print("Launching YouTube app...")
        if not launch_app_on_roku(roku_ip, ROKU_APP_YOUTUBE_ID):
            print("Failed to launch YouTube app.")
            return False

        time.sleep(5)  # Wait for the app to load

        # Navigate to the search bar
        print("Navigating to the search bar...")
        for remote_button in NAVIGATION_SEQUENCE_TO_SEARCH:
            if not send_remote_control_command(roku_ip, remote_button):
                print(f"Failed to navigate to {remote_button}.")
                return False
            time.sleep(0.5)

        # Input search text
        print(f"Searching YouTube for '{search_query}'...")
        for character in search_query:
            if not send_remote_control_command(roku_ip, f'Lit_{character}'):
                print(f"Failed to input '{character}' in the search bar.")
                return False
            time.sleep(0.2)

        # Navigate to the video and select it
        print("Selecting the video...")
        for remote_button in NAVIGATION_SEQUENCE_TO_VIDEO:
            if not send_remote_control_command(roku_ip, remote_button):
                print(f"Failed to navigate to {remote_button}.")
                return False
            time.sleep(0.5)

        print("YouTube search completed successfully.")
        return True
    except requests.RequestException as e:
        print("An error occurred while communicating with the Roku device.")
        return False
    except KeyboardInterrupt:
        print("Search interrupted by the user.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

def check_port_open(ip_address, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)  # Timeout for the connection attempt (1 second)
    result = sock.connect_ex((ip_address, port))
    sock.close()
    return result == 0

def roku_ip_scan():
    network = ipaddress.IPv4Network("192.168.0.0/24", strict=False)
    print("Starting IP range scan...")
    for ip_address in network:
        ip_str = str(ip_address)
        print(f"Scanning IP: {ip_str}", end='\r')
        if check_port_open(ip_str, 8060):
            print(f"Found Roku device at {ip_str}. Running YouTube search...")
            if search_on_youtube(ip_str, youtube_search_query):
                print("YouTube search completed for Roku device at", ip_str)
            else:
                print("YouTube search encountered an error for Roku device at", ip_str)
        time.sleep(0.5)  # Just to simulate scanning delay, you can adjust as needed.
    print("IP range scan completed.")

if __name__ == "__main__":
    youtube_search_query = input("Enter YouTube search query: ").strip()

    if not youtube_search_query:
        print("Invalid input. Please provide a valid YouTube search query.")
    else:
        roku_ip_scan()
