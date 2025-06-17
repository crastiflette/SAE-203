import sys
import yaml
from fabric import Connection, config 
import ipaddress as ip
import validation as val 
import config as cfg
from dhcp import *


def main():

    MAC_duplicate = []
    IP_duplicate = []

    if len(sys.argv) < 3 :

        config = cfg.load_config('/etc/supervisor.yaml', False)

        if len(sys.argv) == 2:

            ip = sys.argv[1]

            if len(ip.split('/')) == 2:
                ip = ip.split('/')[0]

            if not val.IsIPValid(ip):
                print(f"ERROR: {ip} n'est pas une adresse IP valide.")
                return
            
            dhcp_servers = list(cfg.get_dhcp_server(ip, config).keys())
            if not dhcp_servers:
                print(f"ERROR: Unable to identify DHCP server for {ip}.")
                return
            else:
                dhcp_server = dhcp_servers[0]
                list_servers = [dhcp_server]
        else:
            list_servers = list(config['dhcp-servers'].keys())

        # Vérification de la configuration des serveurs DHCP
        for dhcp_server in list_servers:
            correspondences = dhcp_list(dhcp_server, config)

            mac_addresses = []
            ip_addresses = []
            for correspondance in correspondences:
                mac_addresses.append(list(correspondance.values())[0])
                ip_addresses.append(list(correspondance.values())[1])
                
            for i in range (len(mac_addresses)):
                mac = mac_addresses[i]
                ip_address = ip_addresses[i]

                # Si il y a des doublons s'adresse MAC
                if mac_addresses.count(mac) > 1:
                    # On ajoute la correspondance à la liste des doublons
                    MAC_duplicate.append([dhcp_server, mac, ip_address])

                # Si il y a des doublons s'adresse IP
                if ip_addresses.count(ip_address) > 1:
                    # On ajoute la correspondance à la liste des doublons
                    IP_duplicate.append([dhcp_server, mac, ip_address])

        if MAC_duplicate:
            print("MAC addresses duplicates:")
            for m in MAC_duplicate:
                print(f"Server: {m[0]}, MAC: {m[1]}, IP: {m[2]}")
        else:
            print("No MAC addresses duplicates found.")

        if IP_duplicate:
            print("IP addresses duplicates:")
            for i in IP_duplicate:
                print(f"Server: {i[0]}, MAC: {i[1]}, IP: {i[2]}")
        else:
            print("No IP addresses duplicates found.")

    else:
        print("Error: incorrect number of arguments.")
        return
    

if __name__ == "__main__":
    main()