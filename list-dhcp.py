from config import *
from dhcp import *
from fabric import Connection
import sys
import yaml
import validation

filename = '/amuhome/s24006511/Documents/SAE203-Partie-2/dhcp_host_conf.yaml'


def main():
    """
    Permet de listser els associations adresse mac/ip 
    définies sur un ou plusieurs serveurs DHCP.
    """

    args = sys.argv
    config = load_config(filename, False)

    if len(args) == 1:
    
        dhcp_servers = list(config['dhcp-servers'].keys())

    elif len(args) == 2:

        ip_address = args[1]

        if len(ip_address.split('/')) == 2:
            ip_address = ip_address.split('/')[0]

        if not validation.IsIPValid(ip_address):
            print(f"Error: invalid IP address '{ip_address}'.")
            return
        
        try:
            dhcp_server = list(get_dhcp_server(ip_address, config).keys())
        except Exception:
            print(f"Error: le serveur cherché n'est pas dans la configuration.")
            return
        if not dhcp_server:
            print(f"Error: no DHCP server found for IP address '{ip_address}'.")
            return
        else:
            dhcp_servers = [dhcp_server[0]]

    
    for dhcp_server in dhcp_servers:

        matching = dhcp_list(dhcp_server, config)
        

        if matching:
            print(f"\n{dhcp_server}:")
            for match in matching:
                print(match["mac"] + 10* " " + match["ip"])
    





if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nCommand aborted.")
