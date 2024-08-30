### **Report on `mqtt_to_dataset` Service**

#### **Purpose and Overview**

The `mqtt_to_dataset` service is designed to capture and process data from Meraki cameras via MQTT messages, storing snapshots and corresponding annotations in a dataset format suitable for future machine learning training, particularly in computer vision applications. This service plays a crucial role in automating the collection and organization of labeled image data, which can be used to train models for object detection, classification, and other vision tasks.

#### **Functionality**

The service subscribes to specific MQTT topics associated with various Meraki cameras deployed in different locations. These topics provide real-time data on detected objects, including their coordinates and classes, as captured by the cameras. The service processes this data and performs the following actions:

1. **Subscribing to MQTT Topics:**
   - Upon startup, the service connects to the MQTT broker and subscribes to designated topics corresponding to each camera. This allows it to receive messages containing object detection data in real-time.

2. **Processing Incoming Messages:**
   - The service listens for MQTT messages that include object detection data from the cameras. Each message is parsed to extract relevant information, such as object classes, coordinates, and timestamps.

3. **Snapshot Capture:**
   - For each valid message that meets predefined criteria (e.g., containing two or more detected objects), the service triggers a request to the Meraki API to capture a snapshot from the camera at the corresponding timestamp.

4. **Data Storage:**
   - The captured snapshots are saved locally in a structured directory on NFS storage, with filenames including the camera name and timestamp for easy referencing.
   - The service also generates and saves annotation files in multiple formats:
     - **YOLO Format:** Text files containing normalized object coordinates and class labels.
     - **COCO Format:** JSON files formatted for use with the COCO dataset standard, including image metadata and bounding box annotations.
     - **Pascal VOC Format:** XML files formatted for use with the Pascal VOC dataset standard, including bounding box coordinates and class names.

5. **Time Interval Management:**
   - To avoid redundant data storage, the service enforces a configurable interval between stored messages for each camera. This ensures that only distinct or significant detections are recorded, optimizing storage and processing efficiency.

#### **Technical Details**

- **Language and Dependencies:** The service is implemented in Python, utilizing the Paho MQTT library for handling MQTT communications, the Meraki Dashboard API for snapshot capture, and standard libraries for JSON, XML, and file I/O operations.
- **Service Management:** The service is managed as a systemd service, ensuring it starts automatically on boot and restarts on failure, providing robustness and reliability in operation.
- **Environment Considerations:** The service relies on NFS storage for dataset persistence, making it crucial to ensure that NFS is available and mounted before the service starts. This is managed through dependencies in the systemd service file.

#### **Use Case and Value**

The primary use case for this service is to support the development of machine learning models by automating the collection and annotation of real-world image data. By continuously gathering labeled data from deployed cameras, the service significantly reduces the manual effort required in dataset preparation, a typically labor-intensive process in machine learning workflows.

This automation allows for the rapid iteration and improvement of models, as new data can be seamlessly integrated into the training pipeline. The ability to store annotations in multiple standard formats (YOLO, COCO, Pascal VOC) ensures compatibility with various tools and frameworks commonly used in computer vision research and development.

Overall, the `mqtt_to_dataset` service provides a scalable, automated solution for dataset generation, supporting ongoing machine learning initiatives and enhancing the ability to develop, train, and deploy advanced computer vision models.
