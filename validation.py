import ipaddress as ip


def IsMac(S):
    digits = S.split(':')
    if len(digits) != 6:
        return False
    for digit in digits:
        if len(digit) != 2:
            return False
        try:
            int(digit, 16)
        except ValueError:
            return False
    return True

def IsIPValid(ip_address):
    """Vérifie si l'adresse IP est valide, """

    if ip.IPv4Address(ip_address):
        if ip.IPv4Address(ip_address).is_multicast:
            return False
        elif ip.IPv4Address(ip_address).is_unspecified:
            return False
        elif ip.IPv4Address(ip_address).is_reserved:
            return False
        elif ip.IPv4Address(ip_address).is_loopback:
            return False
        elif ip.IPv4Address(ip_address).is_link_local:
            return False
        elif ip.IPv4Address(ip_address).is_private:
            return True
        else :
            return False
    else:
        return False
    
