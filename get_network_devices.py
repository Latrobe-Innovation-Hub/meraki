import meraki
from datetime import datetime

# Your Meraki API key
API_KEY = 'your_api_key_here'

# Initialize the Meraki Dashboard API client
dashboard = meraki.DashboardAPI(API_KEY)

# Function to get devices and categorize them by type
def get_devices_by_type(network_id):
    try:
        devices = dashboard.networks.getNetworkDevices(network_id)
        categorized_devices = {
            "Access Points": [],
            "Cameras": [],
            "Switches": [],
            "Firewalls": [],
            "Unknown Devices": [],
        }

        for device in devices:
            device_info = {
                "name": device.get("name", "None"),
                "serial": device["serial"],
                "mac": device["mac"],
                "model": device["model"],
            }

            if device["model"].startswith("MR"):
                categorized_devices["Access Points"].append(device_info)
            elif device["model"].startswith("MV"):
                categorized_devices["Cameras"].append(device_info)
            elif device["model"].startswith("MS"):
                categorized_devices["Switches"].append(device_info)
            elif device["model"].startswith("MX"):
                categorized_devices["Firewalls"].append(device_info)
            else:
                categorized_devices["Unknown Devices"].append(device_info)

        return categorized_devices
    except Exception as e:
        print(f"Failed to retrieve network devices: {str(e)}")
        return None

# Function to pretty print the categorized devices
def pretty_print_devices(categorized_devices):
    print(f"\n{'='*40} Device List by Type {'='*40}\n")
    for category, devices in categorized_devices.items():
        print(f"{category} ({len(devices)} devices):")
        if devices:
            for device in devices:
                print(f"  - Name: {device['name']}")
                print(f"    Serial: {device['serial']}")
                print(f"    MAC: {device['mac']}")
                print(f"    Model: {device['model']}\n")
        else:
            print(f"  No devices found in this category.\n")
    print(f"\n{'='*40} End of Device List {'='*40}\n")

if __name__ == "__main__":
    print(f"[{datetime.now()}] Fetching network devices categorized by type...\n")
    network_id = input("Enter your network ID: ").strip()
    categorized_devices = get_devices_by_type(network_id)
    if categorized_devices:
        pretty_print_devices(categorized_devices)
