import meraki
from datetime import datetime

# Your Meraki API key
API_KEY = 'your_api_key_here'

# Initialize the Meraki Dashboard API client
dashboard = meraki.DashboardAPI(API_KEY)

# Function to get organization details and networks
def get_organization_and_networks():
    try:
        organizations = dashboard.organizations.getOrganizations()
        org_network_info = []

        for org in organizations:
            networks = dashboard.organizations.getOrganizationNetworks(org['id'])
            org_info = {
                "organization_name": org['name'],
                "organization_id": org['id'],
                "networks": [{"name": network['name'], "id": network['id']} for network in networks]
            }
            org_network_info.append(org_info)

        # Return the collected organization and network information
        return org_network_info
    except Exception as e:
        print(f"Failed to retrieve organization or network details: {str(e)}")
        return None

# Function to pretty print the organization and network info
def pretty_print_info(org_network_info):
    print(f"\n{'='*50} Organization and Network Details {'='*50}\n")
    for org in org_network_info:
        print(f"Organization: {org['organization_name']}")
        print(f"  Organization ID: {org['organization_id']}")
        print("  Networks:")
        for network in org['networks']:
            print(f"    - Network Name: {network['name']}")
            print(f"      Network ID: {network['id']}")
        print("-" * 100)
    print(f"\n{'='*50} End of Details {'='*50}\n")

if __name__ == "__main__":
    print(f"[{datetime.now()}] Fetching organization and network details...\n")
    org_network_info = get_organization_and_networks()
    if org_network_info:
        pretty_print_info(org_network_info)
