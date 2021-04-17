from network_analysis import NetworkAnalysis


class Packet:
    last_router = None

    def __init__(self, src_ip=None, src_mac=None, dest_ip=None, dest_mac=None, data=None, mask=None, dest_orig_ip=None,
                 src_orig_ip=None):
        self.src_ip = src_ip
        self.src_mac = src_mac
        if dest_orig_ip is None:
            self.dest_orig_ip = dest_ip
        else:
            self.dest_orig_ip = dest_orig_ip
        if src_orig_ip:
            self.src_orig_ip = src_orig_ip
        else:
            self.src_orig_ip = src_ip
        self.dest_ip = dest_ip
        self.dest_mac = dest_mac
        self.data = data
        self.dest_mask = mask

        if not self.dest_mask:
            raise Exception("Veuillez spécifier un masque réseau")
        if not (self.src_ip and self.dest_ip):
            raise Exception("Veuillez spécifier l'(les) addresse(s) IP")
        if not self.src_mac:
            raise Exception("Veuillez spécifier l'addresse MAC source")


class Frame(Packet):
    def _init__(self, src_ip, src_mac, dest_ip, dest_mac, mask=None, dest_orig_ip=None,
                src_orig_ip=None):
        self.data = None
        super().__init__(src_ip, src_mac, dest_ip, dest_mac, self.data, mask, dest_orig_ip, src_orig_ip)


class ARPResponsePacket(Packet):
    def _init__(self, src_ip, src_mac, dest_ip, dest_mac, mask=None, dest_orig_ip=None,
                src_orig_ip=None):
        self.data = None
        super().__init__(src_ip, src_mac, dest_ip, dest_mac, self.data, mask, dest_orig_ip, src_orig_ip)


class ARPRequestPacket(Packet):
    def _init__(self, src_ip, src_mac, dest_ip, dest_mac, mask=None, dest_orig_ip=None, src_orig_ip=None):
        self.data = None
        super().__init__(src_ip, src_mac, dest_ip, dest_mac, self.data, mask, dest_orig_ip, src_orig_ip)


class MACInfo:
    def __init__(self, port, mac):
        self.port = port
        self.mac = mac


class ARPInfo:
    def __init__(self, ip, mac):
        self.ip = ip
        self.mac = mac


class RouteInfo:
    def __init__(self, mask, ip, mac, net_addr='', port=-1):
        if net_addr == '':
            self.net_addr = NetworkAnalysis(ip, mask).get_network_address()
        else:
            self.net_addr = net_addr
        self.port = port
        self.mask = mask
        self.ip = ip
        self.mac = mac


class NetworkInfo:
    def __init__(self, ip, mask):
        self.ip = ip
        self.mask = mask


class NetworkInter:
    def __init__(self, mac, name=''):
        self.name = name
        self.mac = mac


class NetworkConnectivity:
    def __init__(self, network_info, network_inter):
        self.net_info = network_info
        self.net_inter = network_inter
