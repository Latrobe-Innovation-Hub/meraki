import meraki
from datetime import datetime
import time

# Your Meraki API key
API_KEY = 'your api key'

# Initialize the Meraki Dashboard API client
dashboard = meraki.DashboardAPI(API_KEY)

# Define your organization and network IDs
organization_id = '1202153' # ltu
network_id = 'L_833165931063549202' # dih jenny graves level2

# Define the Camera Sense MQTT broker ID
mqtt_broker_id = '833165931063541914' # andrew-test

# List of MAC addresses for cameras that should be updated
mac_addresses_to_update = [
    '0c:7b:c8:da:a6:52',  # CollaborationHub201C
    '0c:7b:c8:da:a4:3f',  # CoWorkSpace216
    '0c:7b:c8:da:a5:ec',  # Kitchen
    '0c:7b:c8:da:a5:62',  # MakerLab205
    '0c:7b:c8:da:a4:de',  # MakerLab207
    '0c:7b:c8:da:a6:40',  # MakerSpace204A
    'c4:8b:a3:60:2c:2d',  # MV12-EntryDoor
    '0c:7b:c8:da:a2:b3',  # PitchSpace213
    '0c:7b:c8:da:a2:9e',  # PresentationEntry200
    '0c:7b:c8:da:a6:ac',  # CoWorkLounge201B
]

# Function to get the current camera sense settings
def get_camera_sense_settings(camera_serial):
    try:
        settings = dashboard.camera.getDeviceCameraSense(camera_serial)
        return settings
    except Exception as e:
        print(f"Failed to retrieve sense settings for camera {camera_serial}: {str(e)}")
        return None

# Function to update camera sense settings, including MQTT broker configuration
def update_camera_sense(camera_serial, mqtt_broker_id):
    try:
        response = dashboard.camera.updateDeviceCameraSense(
            serial=camera_serial,
            senseEnabled=True,
            mqttBrokerId=mqtt_broker_id,
            audioDetection={"enabled": False}
        )
        return response
    except Exception as e:
        print(f'Failed to update camera {camera_serial}: {str(e)}')
        return None

# Get the list of devices in your network
devices = dashboard.networks.getNetworkDevices(network_id)

# Keep track of status for all cameras
camera_status_summary = []

# Iterate through each device and update the MQTT broker if it's a camera
print(f"\n[{datetime.now()}] Starting the MQTT broker update process...\n")

for device in devices:
    if device['model'].startswith('MV'):
        # Retrieve current settings to check for the correct MQTT broker ID
        current_settings = get_camera_sense_settings(device['serial'])
        if current_settings:
            camera_info = {
                "name": device['name'],
                "serial": device['serial'],
                "mac": device['mac'],
                "updated": False,
                "mqtt_broker_id": current_settings.get("mqttBrokerId", "Not Set"),
                "topics": current_settings.get("mqttTopics", []),
            }
            print(f"[{datetime.now()}] Processing camera: {device['name']} (Serial: {device['serial']}, MAC: {device['mac']})")

            if device['mac'] in mac_addresses_to_update:
                if current_settings.get('mqttBrokerId') != mqtt_broker_id:
                    print(f"[{datetime.now()}] Updating MQTT broker for {device['name']} to broker ID {mqtt_broker_id}...")
                    update_camera_sense(device['serial'], mqtt_broker_id)

                    # Verify update after a short delay
                    time.sleep(5)
                    updated_settings = get_camera_sense_settings(device['serial'])
                    if updated_settings.get('mqttBrokerId') == mqtt_broker_id:
                        print(f"[{datetime.now()}] Successfully updated MQTT broker for camera: {device['serial']}")
                        camera_info["updated"] = True
                        # Refresh the camera info with updated settings
                        camera_info["mqtt_broker_id"] = updated_settings.get("mqttBrokerId", "Not Set")
                        camera_info["topics"] = updated_settings.get("mqttTopics", [])
                    else:
                        print(f"[{datetime.now()}] WARNING: MQTT broker update did not apply correctly for {device['name']}. Retrying...")
                        update_camera_sense(device['serial'], mqtt_broker_id)
                else:
                    print(f"[{datetime.now()}] MQTT broker already set correctly for {device['name']}.")
            else:
                print(f"[{datetime.now()}] Camera {device['name']} is not in the update list, skipping update.")

            camera_status_summary.append(camera_info)
        else:
            print(f"[{datetime.now()}] Failed to retrieve settings for {device['name']}, skipping.")

# Final summary of camera statuses
print(f"\n[{datetime.now()}] MQTT broker update process completed.\n")
print(f"{'='*40} Camera Status Summary {'='*40}\n")

for status in camera_status_summary:
    print(f"Camera Name: {status['name']}")
    print(f"  Serial: {status['serial']}")
    print(f"  MAC: {status['mac']}")
    print(f"  MQTT Broker ID: {status['mqtt_broker_id']}")
    print(f"  Topics: {', '.join(status['topics'])}")
    print(f"  Updated: {'Yes' if status['updated'] else 'No'}")
    print(f"{'-'*90}")

print("\nSummary completed.\n")
