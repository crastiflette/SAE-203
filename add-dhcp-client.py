"""La commande add-dhcp-client ajoute une association MAC/IP 
dans la configuration dnsmasq d'un serveur DHCP."""

import sys
import validation as val 
import config as cfg
from dhcp import dhcp_add, dhcp_restart




def main():
    """Programme princial"""

    changement = 0

    #Récupération des arguments de la ligne de commande dans une liste.
    args = sys.argv

    # Vérification du nombre d'arguments
    if len(args) != 3:
        print("ERROR: USE:  add-dhcp-client.py <mac_address> <ip_address>")
        return
    
    # Test de la validité des arguments
    mac_address = args[1]
    ip_address = args[2]
    if not val.IsMac(mac_address):
        print(f"ERROR: {mac_address} n'est pas une adresse MAC valide.")
        return
    if not val.IsIPValid(ip_address):
        print(f"ERROR: {ip_address} n'est pas une adresse IP valide.")
        return
    
    config = cfg.load_config('/etc/supervisor.yaml', False)
    server = list(cfg.get_dhcp_server(ip_address, config).keys())
    if not server:
        print(f"ERROR: Unable to identify DHCP server.")
        return
    else:
        dhcp_server = server[0]
    
    changement = dhcp_add(ip_address, mac_address, dhcp_server, config)

    if changement != 0:
        dhcp_restart(dhcp_server)

    
if __name__ == "__main__":
    main()