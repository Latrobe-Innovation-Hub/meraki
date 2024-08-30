import os
import time
import json
import meraki
import requests
import paho.mqtt.client as mqtt
from datetime import datetime
from threading import Thread, Lock

# Replace with your actual API key
API_KEY = 'c974a5739df9626a4dc8e5d1ea5eabdab9ced3e3'

BASE_DIR = '/data/dih/meraki'

# Define camera details
CAMERA_DETAILS = {
    'CollaborationHub201C': {
        'serial': 'Q2PV-XPVZ-6QSV',
        'mqtt_topic': '/merakimv/Q2PV-XPVZ-6QSV/raw_detections'
    },
    'CoWorkSpace216': {
        'serial': 'Q2PV-W8RK-DDVX',
        'mqtt_topic': '/merakimv/Q2PV-W8RK-DDVX/custom_analytics'
    },
    'Kitchen': {
        'serial': 'Q2PV-DZXG-F3GV',
        'mqtt_topic': '/merakimv/Q2PV-DZXG-F3GV/raw_detections'
    },
    'MakerLab205': {
        'serial': 'Q2PV-4ZNH-NJSD',
        'mqtt_topic': '/merakimv/Q2PV-4ZNH-NJSD/raw_detections'
    },
    'MakerLab207': {
        'serial': 'Q2PV-9TA8-VFMG',
        'mqtt_topic': '/merakimv/Q2PV-9TA8-VFMG/raw_detections'
    },
    'MakerSpace204A': {
        'serial': 'Q2PV-DAS8-UX6P',
        'mqtt_topic': '/merakimv/Q2PV-DAS8-UX6P/raw_detections'
    },
    'MV12-EntryDoor': {
        'serial': 'Q2FV-BY6K-RKDN',
        'mqtt_topic': '/merakimv/Q2FV-BY6K-RKDN/raw_detections'
    },
    'PitchSpace213': {
        'serial': 'Q2PV-E88G-SSVY',
        'mqtt_topic': '/merakimv/Q2PV-E88G-SSVY/raw_detections'
    },
    'PresentationEntry200': {
        'serial': 'Q2PV-PQVS-ABKL',
        'mqtt_topic': '/merakimv/Q2PV-PQVS-ABKL/raw_detections'
    },
}

# Initialize the Meraki Dashboard API client
dashboard = meraki.DashboardAPI(API_KEY)
snapshot_lock = Lock()

# Dictionary to store the latest message for each camera
latest_messages = {}

def download_snapshot_image(url, camera_name, timestamp):
    """
    Downloads a snapshot image from the URL and saves it locally.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()

        directory = f"{BASE_DIR}/dataset/images/{camera_name}"
        os.makedirs(directory, exist_ok=True)
        filename = f"{directory}/snapshot_{camera_name}_{timestamp.replace(':', '').replace('-', '').replace('.', '')}.jpg"

        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"Snapshot saved to {filename}")
        return filename
    except requests.exceptions.RequestException as e:
        print(f"Failed to download snapshot: {e}")
        return None

def save_labels_yolo(camera_name, timestamp, objects, label_type):
    """
    Saves label data in YOLO format to the corresponding label file.
    """
    directory = f"{BASE_DIR}/dataset/labels_yolo/{camera_name}"
    os.makedirs(directory, exist_ok=True)
    filename = f"{directory}/labels_{camera_name}_{timestamp.replace(':', '').replace('-', '').replace('.', '')}.txt"

    labels_written = False  # Track if labels were written
    with open(filename, 'w') as file:
        for obj in objects:
            if label_type == 'raw':
                # Raw detections format
                x0, y0, x1, y1 = obj.get('x0'), obj.get('y0'), obj.get('x1'), obj.get('y1')
                class_label = obj.get('type', 0)  # Replace with actual class index mapping
            elif label_type == 'custom_analytics':
                # Custom analytics format
                x0, y0, x1, y1 = obj['location']
                class_label = obj['class']

            # Check if coordinates are valid
            if None not in [x0, y0, x1, y1]:
                center_x = (x0 + x1) / 2
                center_y = (y0 + y1) / 2
                width = abs(x1 - x0)
                height = abs(y1 - y0)
                file.write(f"{class_label} {center_x} {center_y} {width} {height}\n")
                labels_written = True  # Mark as written

    if labels_written:
        print(f"Labels saved to {filename}")
    else:
        # If no valid labels were written, delete the empty file to avoid confusion
        os.remove(filename)
        print(f"No valid data to save, removed empty file: {filename}")

def save_labels_old(camera_name, timestamp, objects, label_type):
    """
    Saves label data in YOLO format to the corresponding label file.
    """
    directory = f"{BASE_DIR}/dataset/labels/{camera_name}"
    os.makedirs(directory, exist_ok=True)
    filename = f"{directory}/labels_{camera_name}_{timestamp.replace(':', '').replace('-', '').replace('.', '')}.txt"

    with open(filename, 'w') as file:
        for obj in objects:
            if label_type == 'raw':
                # Raw detections format
                x0, y0, x1, y1 = obj.get('x0'), obj.get('y0'), obj.get('x1'), obj.get('y1')
                class_label = obj.get('type', 0)  # Replace with actual class index mapping
            elif label_type == 'custom_analytics':
                # Custom analytics format
                x0, y0, x1, y1 = obj['location']
                class_label = obj['class']
            # Normalize coordinates to YOLO format
            if None not in [x0, y0, x1, y1]:
                center_x = (x0 + x1) / 2
                center_y = (y0 + y1) / 2
                width = abs(x1 - x0)
                height = abs(y1 - y0)
                file.write(f"{class_label} {center_x} {center_y} {width} {height}\n")
    print(f"Labels saved to {filename}")

import json

def save_labels_coco(camera_name, timestamp, objects, label_type):
    """
    Saves label data in COCO format to a JSON file.
    """
    coco_output = {
        "images": [],
        "annotations": [],
        "categories": []
    }

    # Add categories if not already in the COCO output
    categories = [{"id": i, "name": f"class_{i}"} for i in range(1, 101)]  # Adjust class mapping as needed
    coco_output['categories'].extend(categories)

    # Define the image entry
    image_entry = {
        "id": timestamp,
        "file_name": f"snapshot_{camera_name}_{timestamp}.jpg",
        "height": 1080,  # Adjust as per your image resolution
        "width": 1920   # Adjust as per your image resolution
    }
    coco_output['images'].append(image_entry)

    # Define annotation entries
    for obj in objects:
        if label_type == 'raw':
            x0, y0, x1, y1 = obj.get('x0'), obj.get('y0'), obj.get('x1'), obj.get('y1')
            class_id = obj.get('type', 0)  # Adjust mapping if needed
        elif label_type == 'custom_analytics':
            x0, y0, x1, y1 = obj['location']
            class_id = obj['class']

        if None not in [x0, y0, x1, y1]:
            annotation = {
                "id": len(coco_output['annotations']) + 1,
                "image_id": timestamp,
                "category_id": class_id,
                "bbox": [x0, y0, x1 - x0, y1 - y0],
                "area": (x1 - x0) * (y1 - y0),
                "iscrowd": 0
            }
            coco_output['annotations'].append(annotation)

    # Save COCO JSON
    directory = f"{BASE_DIR}/dataset/labels_coco/{camera_name}"
    os.makedirs(directory, exist_ok=True)
    filename = f"{directory}/coco_annotations_{camera_name}_{timestamp.replace(':', '').replace('-', '').replace('.', '')}.json"
    with open(filename, 'w') as file:
        json.dump(coco_output, file)
    print(f"COCO labels saved to {filename}")


import xml.etree.ElementTree as ET

def save_labels_pascal_voc(camera_name, timestamp, objects, label_type):
    """
    Saves label data in Pascal VOC format to an XML file.
    """
    annotation = ET.Element("annotation")
    folder = ET.SubElement(annotation, "folder").text = "images"
    filename = ET.SubElement(annotation, "filename").text = f"snapshot_{camera_name}_{timestamp}.jpg"
    path = ET.SubElement(annotation, "path").text = f"./dataset/images/{camera_name}/snapshot_{camera_name}_{timestamp}.jpg"

    source = ET.SubElement(annotation, "source")
    database = ET.SubElement(source, "database").text = "Unknown"

    size = ET.SubElement(annotation, "size")
    width = ET.SubElement(size, "width").text = "1920"  # Adjust according to your image size
    height = ET.SubElement(size, "height").text = "1080"
    depth = ET.SubElement(size, "depth").text = "3"

    segmented = ET.SubElement(annotation, "segmented").text = "0"

    for obj in objects:
        if label_type == 'raw':
            x0, y0, x1, y1 = obj.get('x0'), obj.get('y0'), obj.get('x1'), obj.get('y1')
            class_name = obj.get('type', 'unknown')  # Replace with actual class mapping
        elif label_type == 'custom_analytics':
            x0, y0, x1, y1 = obj['location']
            class_name = f"class_{obj['class']}"  # Replace with actual class names

        if None not in [x0, y0, x1, y1]:
            obj_entry = ET.SubElement(annotation, "object")
            name = ET.SubElement(obj_entry, "name").text = class_name
            pose = ET.SubElement(obj_entry, "pose").text = "Unspecified"
            truncated = ET.SubElement(obj_entry, "truncated").text = "0"
            difficult = ET.SubElement(obj_entry, "difficult").text = "0"

            bndbox = ET.SubElement(obj_entry, "bndbox")
            ET.SubElement(bndbox, "xmin").text = str(int(x0 * 1920))  # Adjust coordinates scaling
            ET.SubElement(bndbox, "ymin").text = str(int(y0 * 1080))
            ET.SubElement(bndbox, "xmax").text = str(int(x1 * 1920))
            ET.SubElement(bndbox, "ymax").text = str(int(y1 * 1080))

    directory = f"{BASE_DIR}/dataset/labels_voc/{camera_name}"
    os.makedirs(directory, exist_ok=True)
    filename = f"{directory}/pascal_voc_{camera_name}_{timestamp.replace(':', '').replace('-', '').replace('.', '')}.xml"
    tree = ET.ElementTree(annotation)
    tree.write(filename)
    print(f"Pascal VOC labels saved to {filename}")


def process_snapshot(camera_name, timestamp, objects, label_type):
    """
    Process a snapshot for a given camera and timestamp, retrying if necessary.
    """
    # Wait 2 minute before processing to allow for video availability
    time.sleep(120)

    retries = 5  # Number of retries
    retry_wait = 30  # Wait time between retries in seconds

    for attempt in range(retries):
        try:
            with snapshot_lock:
                response = dashboard.camera.generateDeviceCameraSnapshot(
                    CAMERA_DETAILS[camera_name]['serial'],
                    timestamp=timestamp
                )
                snapshot_url = response.get('url')
                if snapshot_url:
                    time.sleep(15)  # Small delay before downloading
                    image_path = download_snapshot_image(snapshot_url, camera_name, timestamp)
                    if image_path:
                        save_labels_yolo(camera_name, timestamp, objects, label_type)   # YOLO format
                        save_labels_coco(camera_name, timestamp, objects, label_type)   # COCO format
                        save_labels_pascal_voc(camera_name, timestamp, objects, label_type)  # Pascal VOC format
                    return  # Exit the function if successful

        except meraki.exceptions.APIError as e:
            if "No video for the specified timestamp" in str(e):
                print(f"Specific timestamp not available for {camera_name}, retrying in {retry_wait} seconds...")
                time.sleep(retry_wait)
            else:
                print(f"API Error while retrieving snapshot for {camera_name}: {e}")
                break

        except Exception as e:
            print(f"An error occurred while retrieving snapshot for {camera_name}: {e}")
            break

    print(f"Failed to retrieve snapshot for {camera_name} after {retries} attempts.")

def extract_timestamp(message):
    """
    Extracts the timestamp from the MQTT message.
    """
    return message.get('timestamp') or message.get('ts')

def on_message(client, userdata, msg):
    """
    MQTT message handler to process incoming messages.
    """
    try:
        message = json.loads(msg.payload.decode('utf-8'))

        # Check if 'outputs' or 'objects' exist and contain 2 or more items
        if 'outputs' in message and len(message['outputs']) >= 2:
            objects = message['outputs']
            label_type = 'custom_analytics'
        elif 'objects' in message and len(message['objects']) >= 2:
            objects = message['objects']
            label_type = 'raw'
        else:
            #print(f"Ignored message from {msg.topic} due to insufficient objects or outputs.")
            return

        timestamp = extract_timestamp(message)
        if timestamp is not None:
            timestamp_dt = datetime.utcfromtimestamp(timestamp / 1000.0).isoformat() + 'Z'
            camera_name = next((name for name, details in CAMERA_DETAILS.items() if msg.topic == details['mqtt_topic']), None)
            if camera_name:
                with snapshot_lock:
                    # set interval 6 mins between mqtt message capture/storing
                    if camera_name not in latest_messages or \
                            (datetime.utcnow() - latest_messages[camera_name]['received_time']).total_seconds() >= 360:
                        latest_messages[camera_name] = {
                            'timestamp': timestamp_dt,
                            'received_time': datetime.utcnow()
                        }
                        print(f"Stored timestamp {timestamp_dt} for {camera_name}")
                        # Start snapshot processing in a separate thread
                        Thread(target=process_snapshot, args=(camera_name, timestamp_dt, objects, label_type)).start()
                    #else:
                    #    print(f"Skipped processing for {camera_name} due to recent activity.")
    except json.JSONDecodeError:
        print("Failed to decode MQTT message.")
    except Exception as e:
        print(f"Unexpected error in on_message: {e}")

def on_message_old(client, userdata, msg):
    """
    MQTT message handler to process incoming messages.
    """
    try:
        message = json.loads(msg.payload.decode('utf-8'))

        # Check if 'outputs' or 'objects' exist and contain 2 or more items
        if ('outputs' in message and len(message['outputs']) >= 2):
            objects = message['outputs']
            label_type = 'custom_analytics'
        elif ('objects' in message and len(message['objects']) >= 2):
            objects = message['objects']
            label_type = 'raw'
        else:
            return

        timestamp = extract_timestamp(message)
        if timestamp is not None:
            timestamp_dt = datetime.utcfromtimestamp(timestamp / 1000.0).isoformat() + 'Z'
            camera_name = next((name for name, details in CAMERA_DETAILS.items() if msg.topic == details['mqtt_topic']), None)
            if camera_name:
                with snapshot_lock:
                    if camera_name not in latest_messages or \
                            (datetime.utcnow() - latest_messages[camera_name]['received_time']).total_seconds() >= 60:
                        latest_messages[camera_name] = {
                            'timestamp': timestamp_dt,
                            'received_time': datetime.utcnow()
                        }
                        print(f"Stored timestamp {timestamp_dt} for {camera_name}")
                        # Start snapshot processing in a separate thread
                        Thread(target=process_snapshot, args=(camera_name, timestamp_dt, objects, label_type)).start()

    except json.JSONDecodeError:
        print("Failed to decode MQTT message.")

def main():
    # Start the MQTT client
    client = mqtt.Client()
    client.on_message = on_message
    client.connect('127.0.0.1', 1883, 60)

    # Subscribe to all camera topics
    for camera_name, details in CAMERA_DETAILS.items():
        client.subscribe(details['mqtt_topic'])
        print(f"Subscribed to MQTT topic {details['mqtt_topic']} for camera {camera_name}")

    client.loop_forever()

if __name__ == '__main__':
    main()
