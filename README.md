# Meraki API Automation Scripts

This repository contains a collection of Python scripts designed to automate various tasks using the Meraki Dashboard API. The scripts are organized to retrieve key information, manage devices, and automate settings configurations.

## Table of Contents
- [Introduction](#introduction)
- [Requirements](#requirements)
- [Setup](#setup)
- [Scripts Overview](#scripts-overview)
  - [Get Meraki Organization and Network IDs](#get-meraki-organization-and-network-ids)
  - [Get Network Devices](#get-network-devices)
  - [Meraki MQTT Camera Broker Reset](#meraki-mqtt-camera-broker-reset)
- [Example Usage](#example-usage-meraki-mqtt-camera-broker-reset)

## Introduction
This repository aims to streamline common operations within the Meraki Dashboard, including:
- Retrieving organization and network IDs
- Fetching network devices categorized by type
- Updating the MQTT broker settings for Meraki MV cameras

## Requirements
- Python 3.x
- Meraki Python SDK (`meraki`)
- Other dependencies listed in `requirements.txt` (if applicable)

## Setup
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd meraki-scripts
   ```
2. Install required Python packages:
   ```bash
   pip install meraki
   ```
3. Set up your environment variables or update the scripts with your Meraki API key:
   - Set your API key as an environment variable:
     ```bash
     export MERAKI_API_KEY=your_api_key
     ```
     
## Scripts Overview

### Get Meraki Organization and Network IDs
- **File:** `get_meraki_org_and_network_ids.py`
- **Description:** Retrieves the organization ID and network IDs associated with your Meraki account. This is useful for obtaining necessary IDs for other API calls.
- **Usage:** Run the script and follow the prompts to obtain the details.

### Get Network Devices
- **File:** `get_network_devices.py`
- **Description:** Fetches all devices in a given network and categorizes them by device type (e.g., access points, cameras, switches). Outputs the devices in a structured and readable format.
- **Usage:** Run the script and provide the network ID when prompted.

### Meraki MQTT Camera Broker Reset
- **File:** `meraki-mqtt-camera-broker-reset.py`
- **Description:** Automates the process of updating the MQTT broker settings for a list of Meraki cameras. It ensures all specified cameras have the correct broker configuration and provides a summary of the updates.
- **Usage:** Customize the script with your list of camera MAC addresses and run it to perform the updates.

## Example Usage: Meraki MQTT Camera Broker Reset
The script automates the entire process, updating the MQTT broker settings for the specified cameras and providing a summary of the results.

### Pre-requisites:

Before running the script, ensure you have the following information:

1. **Meraki API Key**:  
   You need a Meraki API key for authentication.  
   - You can generate or obtain your API key from the Meraki dashboard under **Account > API access**.

2. **Organization ID**:  
   The organization ID is required to interact with your Meraki account.  
   - Run the script `get_meraki_org_and_network_ids.py` to obtain the organization ID.

   ```bash
   python3 get_meraki_org_and_network_ids.py
   ```
   **Example output**:
   ```python
   Organization ID: 123456 - Name: Your Organization
   ```
3. **Network ID**:
   The network ID is required to specify which network your devices belong to.
   - The same script, get_meraki_org_and_network_ids.py, also provides the network IDs associated with your organization.
   **Example output**:
   ```python
   Network ID: L_123456789012345678 - Name: Your Network
   ```
4. **Camera MAC Addresses**:
   You’ll need the MAC addresses of the cameras that need their MQTT broker settings updated.
   - Run the script get_network_devices.py to get a list of all devices in your network, including cameras.
     ```bash
     python3 get_network_devices.py
     ```
     **Example output**:
     ```python
     Device Name: Camera 1 - MAC: 00:11:22:33:44:55
     Device Name: Camera 2 - MAC: 66:77:88:99:AA:BB
     ```
5. **Running the Meraki MQTT Camera Broker Reset Script**:
   Once you have the required information, customize the meraki-mqtt-camera-broker-reset.py script with:
   - The correct API key (or set it as an environment variable).
   - The organization ID.
   - The network ID.
   - The list of camera MAC addresses you want to update.
   Run the script:
   ```bash
   python3 meraki-mqtt-camera-broker-reset.py
   ```
