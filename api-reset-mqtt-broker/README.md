# Meraki Camera Sense MQTT Broker Updater

This Flask application provides a simple web interface to update the MQTT broker settings for a specified list of Meraki cameras. By clicking a button on the web page, you can automatically update the MQTT broker to a predefined value, ensuring consistent settings across your camera network.

## Features

- **Single-Click Update:** A button on the web interface triggers the update process for selected Meraki cameras, setting their MQTT broker to a predefined value.
- **Status Summary:** After running the update, the application provides a summary of the current settings for each camera, indicating which cameras were updated successfully.

## Prerequisites

- Python 3.x
- Meraki Dashboard API Key
- Flask
- Meraki Python SDK

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/meraki-camera-sense-updater.git
   cd meraki-camera-sense-updater
   ```

2. **Install required dependencies:**
   ```bash
   pip install flask meraki
   ```

3. **Set your Meraki API Key:**
   - Set your Meraki API key directly in the script or as an environment variable named `MERAKI_API_KEY`.

4. **Configure the Application:**
   - Update the `organization_id`, `network_id`, and `mqtt_broker_id` variables in the script to match your Meraki setup.
   - Ensure the list of `mac_addresses_to_update` contains the MAC addresses of the cameras you wish to update.

## Usage

1. **Start the Flask Application:**
   ```bash
   python app.py
   ```

2. **Access the Web Interface:**
   - Open your browser and navigate to `http://localhost:5000` to view the interface.

3. **Run the Update Script:**
   - Click the "Update Cameras" button on the web interface to set the MQTT broker for the specified cameras. The results will display a summary of the current settings and update status for each camera.

## How It Works

1. **Initialization:**
   - The application initializes a Meraki Dashboard API client using the provided API key.

2. **Script Execution:**
   - When the `/run-script` endpoint is triggered via the web interface, the app:
     - Retrieves all devices in the specified network.
     - Filters devices that are cameras (`MV` models).
     - Checks the current Sense settings for each camera.
     - Updates cameras in the predefined list with the specified MQTT broker if their current broker does not match.
     - Returns a summary of the update process for each camera.

3. **Data Persistence:**
   - The application does not persist data; it displays real-time information and updates settings directly on the Meraki Dashboard.

## Troubleshooting

- **Connection Issues:** Ensure that your network allows outbound connections to the Meraki Dashboard API.
- **Permission Errors:** Verify that your API key has sufficient permissions to access and modify the camera settings in the specified organization and network.
