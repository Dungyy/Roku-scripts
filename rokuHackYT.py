#!/usr/bin/env python3
import requests
import time

def send_remote_control_command(roku_ip, remote_button):
    print(f"Sending command: {remote_button}")
    url = f"http://{roku_ip}:8060/keypress/{remote_button}"
    requests.post(url)

def launch_app_on_roku(roku_ip, app_id):
    print(f"Launching app: {app_id}")
    url = f"http://{roku_ip}:8060/launch/{app_id}"
    requests.post(url)

def search_on_youtube(roku_ip, search_query):
    launch_app_on_roku(roku_ip, '837')  # Launch YouTube
    time.sleep(5)  # Wait for the app to load

    # Define sequence to navigate to the search bar
    navigation_sequence_to_search = ['Left', 'Up', 'Right', 'Right']
    for remote_button in navigation_sequence_to_search:
        send_remote_control_command(roku_ip, remote_button)
        time.sleep(1)  # Wait for UI to respond

    # Input search text
    for character in search_query:
        send_remote_control_command(roku_ip, f'Lit_{character}')
        time.sleep(0.5)  # Wait for UI to respond

    # Define sequence to navigate to the video and select it
    navigation_sequence_to_video = ['Right', 'Left', 'Down', 'Down', 'Down', 'Down', 'Right', 'Right', 'Select', 'Down', 'Select']
    for remote_button in navigation_sequence_to_video:
        send_remote_control_command(roku_ip, remote_button)
        time.sleep(1)  # Wait for UI to respond

roku_device_ip_address = input("Enter the IP address of the Roku device: ")
youtube_search_query = input("Enter the search query for YouTube: ")

search_on_youtube(roku_device_ip_address, youtube_search_query)
