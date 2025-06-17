from fabric import Connection, config 
from paramiko.ssh_exception import SSHException, NoValidConnectionsError
import config 
import yaml
import getpass



def ip_other_mac_exists(cnx, ip, mac, cfg):
    """Vérifie si l'adresse IP et l'adresse MAC existent déjà dans la configuration."""
    
    for host_cfg in cfg.get('hosts', []):
        if host_cfg.get('ip') == ip and host_cfg.get('mac') != mac:
            return True
    return False


def mac_exists(cnx, mac, cfg):
    """Check if mac address is already present in the dhcp configuration."""

    for host_cfg in cfg.get('hosts', []):
        if host_cfg.get('mac') == mac:
            return True
    return False

def dhcp_add(ip, mac, server, cfg):
    """Add an ip/mac address correspondence in the dnsmasq configuration file of server"""

    
    try:
        dhcp_config_file = cfg['dhcp_hosts_cfg']
        passphrase = getpass.getpass('Passphrase: ')
        
        with Connection(server, user='sae203', connect_kwargs={'passphrase': passphrase}) as link:
            try:
                if not ip_other_mac_exists(link, ip, mac, cfg):
                    if not mac_exists(link, mac, cfg):
                        mac = mac.lower()
                        #Ajout de la nouvelle ligne d'hote
                        link.sudo(f"sed -i -e '$a dhcp-host={mac},{ip}' {dhcp_config_file}")
                    else:
                        #Récupération de l'ancienne adresse IP pour
                        line_mac = link.run(f"grep -i '{mac}' {dhcp_config_file}", warn=True, hide=True).tail("stdout").strip()
                        ancienne_ip = ''.join(line_mac.split(",")[1])

                        #Remplacement de l'ancienne adresse IP par la nouvelle
                        link.sudo(f"sed -i -e 's/{ancienne_ip}/{ip}/g' {dhcp_config_file}")
                else:
                    print(f"ERROR: {ip} already exist.")
            except SSHException as e:
                print(f"ERROR: An error occurred while attempting to connect via SSH: {e}")
            except PermissionError as pe:
                print(f"ERROR: permission error: {pe}")
            except Exception as e:
                print(f"ERROR: An unexpected error occurred: {e}")
        return True
    except Exception as e:
        print(f"ERROR: An error occurred while processing the DHCP configuration: {e}")
        return False



def dhcp_remove(mac, server, cfg):
    """Remove an ip/mac address correspondence in the dnsmasq configuration file of server"""

    try:
        dhcp_config_file = cfg['dhcp_hosts_cfg']
        with Connection(server, user='sae203', connect_kwargs={"password": "sae203"}) as link:
            try:
                #On vérifie que l'adresse MAC existe deja dans le fichier de configuration
                if mac_exists(link, mac, cfg):
                    #Suppréssion des lignes contenant l'adresse MAC
                    link.sudo(f"sed -i -e '/{mac}/d' {dhcp_config_file}")
                else:
                    print(f"ERROR: {mac} does not exist.")
            except SSHException as e:
                print(f"ERROR: An error occurred while attempting to connect via SSH: {e}")
            except PermissionError as pe:
                print(f"ERROR: permission error: {pe}")
            except Exception as e:
                print(f"ERROR: An unexpected error occurred: {e}")
        return True
    except Exception as e:
        print(f"ERROR: An error occurred while processing the DHCP configuration: {e}")
        return False


def dhcp_list(server, cfg):
    """
    Liste tout les adresses IP et MAC dans le fichier de configuration dnsmasq
    ELLE MARCHE PAS TOUCHER !!!!
    
    """

    dhcp_config_addr = []
    if cfg:
        dhcp_config_file = cfg['dhcp_hosts_cfg']
        dhcp_user = cfg['user']
    else:
        return 'ERROR: No configuration file found.'
        
    
    with Connection(server, user=dhcp_user, connect_kwargs={"password": "sae203"}, connect_timeout=5) as link:

        
        try:
            #Récupération de la liste des adresses IP et MAC
            results = link.run(f"grep -i 'dhcp-host' {dhcp_config_file}", hide=True).tail("stdout").strip()
            lignes = results.split('\n')
            if results:
                for line in lignes:
                    #On récupére l'adresse IP et l'adresse MAC
                    line_mac = line.split(',')
                    mac = line_mac[0].split('=')[1].strip()
                    ip = line_mac[1].strip()
                    result = {
                        'mac': mac,
                        'ip': ip
                    }
                    dhcp_config_addr.append(result)
            else:
                print("INFORMATION: The config file is empty.")
        except SSHException as e:
            print(f"ERROR: An error occurred while attempting to connect via SSH: {e}")
        except PermissionError as pe:
            print(f"ERROR: permission error: {pe}")
        except Exception as e:
            print(f"ERROR: An unexpected error occurred: {e}")
    return dhcp_config_addr
          

def dhcp_restart(server):
    
    restarted_service = False
    # Saisie de la phrase de passe associée à la clé d'authentification propagée sur les serveurs DHCP.
    passphrase = getpass.getpass('Passphrase: ')
    # Etablissement de la connexion SSH au serveur DHCP. Se ferme automatiquement à la fin du bloc with.
    with Connection(server, connect_kwargs={'passphrase': passphrase}) as link:
        try:
            link.sudo("systemctl restart dnsmasq.service")
            restarted_service = True
        except ValueError:
            print("Error: a passphrase must be given.")
        except NoValidConnectionsError:
            print(f"Error: no valid connection to {server}.")
        except SSHException as e:
            print(f"Error (SSH): {e}")
    if restarted_service:
        print(f"Information: {server} DHCP service is restarting.")
    else:
        print(f"Error: {server} DHCP service didn't restart.")




        
def main():
    filename = '/amuhome/s24006511/Documents/SAE203-Partie-2/dhcp_host_conf.yaml'
    cfg = config.load_config(filename, False)
    
    #print(dhcp_add("192.168.1.20", "00:00:00:00:00:00", "192.168.122.101", cfg))
    print(dhcp_list("192.168.122.101", cfg))


if __name__ == "__main__":
    main()
