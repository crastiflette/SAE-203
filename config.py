from os.path import exists, isfile, isdir
import os
import sys
from yaml import safe_load, dump, YAMLError
import yaml
from ipaddress import IPv4Address, IPv4Network



def check_file(path:str):
    """
    Fonction vérifiant que le chemin passé en paramètre existe et correspond à celui d'un fichier.
    """
    valid = False
    if type(path) is str:
        # Vérifie que le chemin existe et correspond bien à un fichier.
        if exists(path) and isfile(path):
            valid = True
    return valid


def load_config(filename, create):
    
    config = None
    # Vérification des types des arguments.
    if isinstance(filename, str):
        # Vérifie si l'accès au fichier est spécifié par un chemin absolu.
        if filename.startswith("/"):
            try:
                with open(filename, 'r', encoding='utf8') as superv_conf:
                    config = yaml.safe_load(superv_conf)
            except FileNotFoundError:
                if create:
                    # Vérification de l'existence du répertoire parent spécifié dans le chemin absolu du fichier.
                    parent_dir = "/".join(filename.split('/')[:-1])
                    if exists(parent_dir) and isdir(parent_dir):
                        # Ecriture de la configuration minimale.
                        with open(filename, 'w', encoding='utf8') as superv_conf:
                            superv_conf.writelines(["dhcp_hosts_cfg: /etc/dnsmasq.d/hosts.conf", "\nuser: gatekeeper"])
                        # Récupération de la configuration minimale.
                        with open(filename, 'r', encoding='utf8') as superv_conf:
                            config = yaml.safe_load(superv_conf)
                    else:
                        print(f"Error: parent directory '{parent_dir}' does not exist.")
                else:
                    print(f"Error: couldn't open configuration file '{filename}'.")
            except YAMLError:
                print("Error: syntax failure in configuration file.")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Error: non-absolute configuration file path provided.")
    else:
        print("Error: incorrect datatype for filename input.")
    return config


def get_dhcp_server(ip, cfg):
    """Look in a configuration object for a dhcp servr configuratio matching the ip address."""
    found = None
    dhcp_servers = list(cfg['dhcp-servers'].keys())
    n = 0
    while (not found) and (n < len(dhcp_servers)):
        dhcp_server = dhcp_servers[n]
        vlan = IPv4Network(cfg['dhcp-servers'][dhcp_server])

        if IPv4Address(ip) in list(vlan.hosts()):
            found = {dhcp_server:cfg['dhcp-servers'][dhcp_server]}

        n += 1
    return found



