import sys
import yaml
from fabric import Connection, config 
import ipaddress as ip
import validation as val 
import config as cfg
from dhcp import dhcp_add, dhcp_remove, dhcp_restart

def main():

    args = sys.argv

    # Vérification du nombre d'arguments
    if len(args) != 2:
        print("ERROR: USE:  add-dhcp-client.py <mac_address> <ip_address>")
        return
    

    # Test de la validité des arguments
    mac_address = args[1]
    if not val.IsMac(mac_address):
        print(f"ERROR: {mac_address} n'est pas une adresse MAC valide.")
        return
    
    config = cfg.load_config('/etc/supervisor.yaml', False)
    dhcp_servers = list(config['dhcp-servers'].keys())
    dhcp_server = 0
    changement = False
    while not changement and dhcp_server < len(dhcp_servers):
        
        # Appel de la fonction de suppression de toutes les correspondances
        changement = dhcp_remove(mac_address, dhcp_servers[dhcp_server], config)

        dhcp_server += 1

    if changement:
        dhcp_restart(dhcp_servers[dhcp_server])
    else:
        print(f"ERROR: {mac_address} does not exist in the DHCP configuration.")

if __name__ == "__main__":
    main()