from flask import Flask, jsonify, render_template
import meraki
from datetime import datetime
import time

app = Flask(__name__)

# Set your Meraki API key here or via an environment variable
API_KEY = ''

# Initialize the Meraki Dashboard API client
dashboard = meraki.DashboardAPI(API_KEY)

# Define your organization and network IDs
organization_id = '1202153'  # ltu
network_id = 'L_833165931063549202'  # dih jenny graves level2

# Define the Camera Sense MQTT broker ID
mqtt_broker_id = '833165931063541914'  # andrew-test

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

def get_camera_sense_settings(camera_serial):
    try:
        settings = dashboard.camera.getDeviceCameraSense(camera_serial)
        return settings
    except Exception as e:
        print(f"Failed to retrieve sense settings for camera {camera_serial}: {str(e)}")
        return None

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-script', methods=['POST'])
def run_script():
    devices = dashboard.networks.getNetworkDevices(network_id)
    camera_status_summary = []

    for device in devices:
        if device['model'].startswith('MV'):
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

                if device['mac'] in mac_addresses_to_update:
                    if current_settings.get('mqttBrokerId') != mqtt_broker_id:
                        update_camera_sense(device['serial'], mqtt_broker_id)
                        time.sleep(5)
                        updated_settings = get_camera_sense_settings(device['serial'])
                        if updated_settings.get('mqttBrokerId') == mqtt_broker_id:
                            camera_info["updated"] = True
                            camera_info["mqtt_broker_id"] = updated_settings.get("mqttBrokerId", "Not Set")
                            camera_info["topics"] = updated_settings.get("mqttTopics", [])

                camera_status_summary.append(camera_info)

    return jsonify({"summary": camera_status_summary})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
