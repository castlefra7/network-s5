from network_entities import *
from network_analysis import NetworkAnalysis

global_txt = ""


def get_str():
    global global_txt
    return global_txt


def to_txt(new_str):
    global global_txt
    global_txt += new_str + "\n"


class Device:

    def __init__(self, name, network_connect):
        self.name = name
        self.net_connect = network_connect


class Switch(Device):

    def __init__(self,
                 connected_devices=None,
                 name='Switch Sans nom',
                 number_ports=10):
        super().__init__(name, None)
        if connected_devices is None:
            connected_devices = []
        self.mac_table = []
        self.number_ports = number_ports
        if len(connected_devices) > number_ports:
            raise Exception("{} a seulement {} ports".
                            format(name, number_ports))
        self.connected_devices = connected_devices
        self.current_port = 0

    def send_broadcast_to_other_switches(self, packet):
        switch_src = packet.switch_src
        switch_org_routes = packet.switch_org_routes.copy()
        is_outside = packet.is_outside
        for pc in self.connected_devices:
            packet = ARPRequestPacket(
                src_ip=packet.src_ip,
                src_mac=packet.src_mac,
                dest_ip=packet.dest_ip,
                mask=packet.dest_mask,
                dest_orig_ip=packet.dest_orig_ip,
                src_orig_ip=packet.src_orig_ip)
            packet.switch_org_routes = switch_org_routes.copy()
            packet.switch_org_routes.append(self)
            packet.is_outside = is_outside

            if isinstance(pc, Switch):
                if pc != self and pc != switch_src:
                    packet.switch_src = self
                    pc.listen_incoming_requests(packet)
            if isinstance(pc, Computer):
                if pc.net_connect.net_inter.mac != packet.src_mac:
                    pc.listen_incoming_request(packet)
            if isinstance(pc, Router):
                shall_send = True
                for routing_info in pc.routing_table:
                    if routing_info.mac == packet.src_mac:
                        shall_send = False
                if shall_send:
                    pc.listen_incoming_request(packet)

    def send_broadcast(self, packet):
        switch_src = packet.switch_src
        is_outside = packet.is_outside
        for pc in self.connected_devices:
            new_switch_org_routes = packet.switch_org_routes.copy()
            packet = ARPRequestPacket(
                src_ip=packet.src_ip,
                src_mac=packet.src_mac,
                dest_ip=packet.dest_ip,
                mask=packet.dest_mask,
                dest_orig_ip=packet.dest_orig_ip,
                src_orig_ip=packet.src_orig_ip)
            packet.switch_org_routes = new_switch_org_routes
            packet.is_outside = is_outside

            if isinstance(pc, Switch):
                if pc != self and pc != switch_src:
                    packet.switch_src = self
                    pc.send_broadcast_to_other_switches(packet)
            if isinstance(pc, Computer):
                if pc.net_connect.net_inter.mac != packet.src_mac:
                    pc.listen_incoming_request(packet)
            if isinstance(pc, Router):
                shall_send = True
                for routing_info in pc.routing_table:
                    if routing_info.mac == packet.src_mac:
                        shall_send = False
                if shall_send:
                    pc.listen_incoming_request(packet)

    def get_connected_device(self, mac_address):
        result = None
        for device in self.connected_devices:
            if isinstance(device, Computer):
                if device.net_connect.net_inter.mac == mac_address:
                    result = device
                    break

        return result

    def update_mac_table(self, packet):
        to_txt("{} met à jour sa table d'addresse MAC".format(self.name))
        is_present = False
        for mac_info_iter in range(len(self.mac_table)):
            mac_info = self.mac_table[mac_info_iter]
            if packet.src_mac == mac_info.mac:
                is_present = True
                break
        if not is_present:
            self.current_port += 1
            self.mac_table.append(MACInfo(self.current_port, packet.src_mac))

        for mac_info in self.mac_table:
            to_txt('{} - {}'.format(mac_info.port, mac_info.mac))

    def send_unicast(self, packet):
        for mac_info in self.mac_table:
            if mac_info.mac == packet.dest_mac:
                for pc in self.connected_devices:
                    if isinstance(pc, Computer):
                        if pc.net_connect.net_inter.mac == packet.dest_mac:
                            to_txt("Envoie du packet vers {}\n".
                                   format(packet.dest_mac))
                            device_dest = \
                                self.get_connected_device(packet.dest_mac)
                            device_dest.listen_incoming_request(packet)
                            break
                    if isinstance(pc, Router):
                        desired_ip, desired_mac, desired_mask = \
                            pc.get_correct_ip_mac_mask(packet.src_ip,
                                                       packet.dest_mask)
                        if desired_mac == packet.dest_mac:
                            to_txt("Envoie du packet vers {}\n".
                                   format(desired_mac))
                            pc.listen_incoming_request(packet)
                            break

    def is_device_connected_to_me(self, packet):
        if packet.is_outside:
            return True
        result = False
        for device in self.connected_devices:
            if isinstance(device, Computer):

                if device.net_connect.net_info.ip == packet.dest_ip:
                    result = True
                    break
        return result

    def listen_incoming_requests(self, packet):
        to_txt("{} reçoit un packet".format(self.name))
        if isinstance(packet, ARPRequestPacket):
            packet.switch_org_routes.append(self)

        self.update_mac_table(packet)
        if isinstance(packet, ARPRequestPacket):
            to_txt(
                """{} envoie une requête de diffusion de type ARPRequest\n""".format(
                    self.name))
            is_outside = packet.is_outside
            self.send_broadcast(packet)
        elif isinstance(packet, ARPResponsePacket):
            if self.is_device_connected_to_me(packet):
                to_txt(
                    "{} envoie une réponse Unicast de type ARPResponse".format(
                        self.name))
                self.send_unicast(packet)
            else:
                new_switch_routes = packet.switch_routes[1:]
                next_switch = new_switch_routes[0]
                packet.switch_routes = new_switch_routes
                to_txt("Envoies du packet vers {}".format(next_switch.name))
                next_switch.listen_incoming_requests(packet)
        elif isinstance(packet, Frame):
            if self.is_device_connected_to_me(packet):
                to_txt("{} envoie une Trame Unicast".format(self.name))
                self.send_unicast(packet)
            else:
                new_switch_routes = packet.switch_routes[1:]
                next_switch = new_switch_routes[0]
                packet.switch_routes = new_switch_routes
                to_txt("Envoies du packet vers {}".format(next_switch.name))
                next_switch.listen_incoming_requests(packet)


class Router(Device):

    def __init__(
            self,
            _connected_switch,
            _routing_table,
            name,
            number_interfaces=10):
        super().__init__(name, None)
        self.arp_table = []
        if len(_connected_switch) > number_interfaces:
            raise Exception(
                "{} a seulement {} interfaces".format(
                    name, number_interfaces))
        self.connected_switch = _connected_switch
        self.number_interfaces = number_interfaces
        self.routing_table = _routing_table
        self.switch_routes_table = []

    def update_switch_routes_table(self, mac, routes):
        self.switch_routes_table.append(SwitchRouteTable(mac, routes))

    def update_arp_table(self, packet):
        to_txt("{} met à jour sa table ARP".format(self.name))
        new_ip, new_mac = packet.src_ip, packet.src_mac
        is_there = False
        for arp in self.arp_table:
            if arp.ip == new_ip:
                is_there = True
                break
        if not is_there:
            arp_info = ARPInfo(new_ip, new_mac)
            self.arp_table.append(arp_info)
        for arp_info in self.arp_table:
            to_txt("{} - {}".format(arp_info.ip, arp_info.mac))

    def get_correct_ip_mac_mask(self, ip, mask):
        network_analysis = NetworkAnalysis(ip, mask)
        net_addr = network_analysis.get_network_address()
        correct_ip = ""
        correct_mac = ""
        correct_mask = ""
        for route_info in self.routing_table:
            if route_info.net_addr == net_addr:
                correct_ip = route_info.ip
                correct_mac = route_info.mac
                correct_mask = route_info.mask
                break
        if correct_ip == "" or correct_mac == "":
            raise Exception(
                "{} n'a pas cette interface réseau: {} - {}".format(self.name, net_addr, mask))
        return correct_ip, correct_mac, correct_mask

    def get_correct_switch(self, ip):
        correct_switch = None
        for switch in self.connected_switch:
            for pc in switch.connected_devices:
                if isinstance(pc, Computer):
                    if pc.net_connect.net_info.ip == ip:
                        correct_switch = switch
                        break
                if isinstance(pc, Router):
                    for route_info in pc.routing_table:
                        if route_info.ip == ip:
                            correct_switch = switch
                            break
        return correct_switch

    def generate_arp_response(self, packet):
        desired_ip, desired_mac, desired_mask = self.get_correct_ip_mac_mask(
            packet.src_ip, packet.dest_mask)
        arp_response = ARPResponsePacket(
            src_ip=desired_ip,
            src_mac=desired_mac,
            dest_ip=packet.src_ip,
            dest_mac=packet.src_mac,
            mask=packet.dest_mask,
            src_orig_ip=packet.src_orig_ip)
        arp_response.switch_src = packet.switch_src
        arp_response.switch_org_routes = packet.switch_org_routes
        arp_response.switch_routes = packet.switch_org_routes[::-1]
        arp_response.is_outside = packet.is_outside
        return arp_response

    def send_arp_response(self, packet):
        to_txt("{} envoie une réponse ARPResponse".format(self.name))
        to_txt("")
        desired_switch = self.get_correct_switch(packet.src_ip)
        desired_switch.listen_incoming_requests(
            self.generate_arp_response(packet))

    def is_mac_known(self, ip):
        known = None
        for arp_info in self.arp_table:
            if arp_info.ip == ip:
                known = arp_info
                break
        return known

    def listen_incoming_request(self, packet):
        to_txt("{} reçoit un packet".format(self.name))
        desired_ip, desired_mac, desired_mask = self.get_correct_ip_mac_mask(
            packet.src_ip, packet.dest_mask)

        if isinstance(packet, ARPRequestPacket):
            if packet.dest_ip != desired_ip:
                to_txt("{} ignore un packet\n".format(self.name))
                return
            else:
                self.update_arp_table(packet)
                to_txt("Ce packet est pour moi")
                switch_org_routes = packet.switch_org_routes[::-1]
                self.update_switch_routes_table(
                    packet.src_mac, switch_org_routes)
                self.send_arp_response(packet)
        elif isinstance(packet, ARPResponsePacket):
            self.update_arp_table(packet)
            if packet.dest_mac != desired_mac:
                return
            else:
                if packet.dest_ip != desired_ip:
                    return
                else:
                    to_txt(
                        "{} reçoit un packet de type ARPResponse\n".format(
                            self.name))
                    self.update_switch_routes_table(
                        packet.src_mac, packet.switch_org_routes)
        elif isinstance(packet, Frame):
            self.update_arp_table(packet)

            to_txt(
                "{} doit envoyer le packet vers {}".format(
                    self.name, packet.dest_orig_ip))
            if self.is_local(packet):
                _new_packet = Packet(
                    src_ip=packet.src_ip,
                    src_mac=packet.src_mac,
                    dest_ip=packet.dest_orig_ip,
                    dest_orig_ip=packet.dest_orig_ip,
                    data=packet.data,
                    mask=packet.dest_mask,
                    src_orig_ip=packet.src_orig_ip)
                _new_packet.is_outside = packet.is_outside
                self.send_packet(_new_packet)
            else:
                self.send_to_next_hop(packet)

    def send_to_next_hop(self, packet):
        to_txt("{} doit envoyer ce packet à d'autres routers".format(self.name))
        desired_gateways = []
        for switch in self.connected_switch:
            routers = []
            for device in switch.connected_devices:
                if isinstance(device, Router):
                    routers.append(device)
            for rt in routers:
                if rt != self and rt != packet.last_router:
                    desired_gateways.append(rt)

        if len(desired_gateways) <= 0:
            to_txt("--- Erreur:")
            to_txt(
                "L'addresse de destination de ce packet ne se trouve pas dans le réseau")
        for desired_gateway in desired_gateways:
            desired_ip = ""
            desired_mask = ""
            found = False
            for route_info in desired_gateway.routing_table:
                network_analysis = NetworkAnalysis(
                    route_info.ip, route_info.mask)
                net_addr = network_analysis.get_network_address()
                for r_info in self.routing_table:
                    network_analysis = NetworkAnalysis(r_info.ip, r_info.mask)
                    net_addr_mine = network_analysis.get_network_address()
                    if net_addr_mine == net_addr:
                        desired_ip = route_info.ip
                        desired_mask = route_info.mask
                        found = True
                        break
                if found:
                    break

            if desired_ip == "":
                to_txt("--- Erreur:")
                to_txt(
                    "L'addresse de destination de ce packet ne se trouve pas dans le réseau")

            packet.dest_ip = desired_ip
            packet.dest_mask = desired_mask
            to_txt(
                "{} doit envoyer le packet vers {}".format(
                    self.name, desired_gateway.name))
            self.send_packet(packet)

    def is_local(self, packet):
        is_local = False
        network_analysis = NetworkAnalysis(
            packet.dest_orig_ip, packet.dest_mask)
        net_addr = network_analysis.get_network_address()
        for route_info in self.routing_table:
            if route_info.net_addr == net_addr:
                is_local = True
                break
        return is_local

    def send_packet(self, packet):
        packet.last_router = self
        if self.is_mac_known(packet.dest_ip):
            self.send_frame(packet)
        else:
            self.send_arp_request(packet)
            self.send_frame(packet)

    def send_arp_request(self, packet):
        desired_switch = self.get_correct_switch(packet.dest_ip)
        to_txt(
            "{} envoie une requête ARP à {}\n".format(
                self.name,
                desired_switch.name))
        desired_switch.listen_incoming_requests(
            self.generate_arp_request(packet))

    def generate_arp_request(self, packet):
        desired_ip, desired_mac, desired_mask = self.get_correct_ip_mac_mask(
            packet.dest_ip, packet.dest_mask)
        arp_request = ARPRequestPacket(
            src_ip=desired_ip,
            src_mac=desired_mac,
            dest_ip=packet.dest_ip,
            mask=packet.dest_mask,
            dest_orig_ip=packet.dest_orig_ip,
            src_orig_ip=packet.src_orig_ip)
        arp_request.switch_org_routes = []
        arp_request.is_outside = packet.is_outside
        return arp_request

    def send_frame(self, packet):
        desired_switch = self.get_correct_switch(packet.dest_ip)
        to_txt(
            "{} envoie une Trame à {}\n".format(
                self.name,
                desired_switch.name))
        desired_switch.listen_incoming_requests(self.generate_frame(packet))

    def generate_frame(self, packet):
        known_device = self.is_mac_known(packet.dest_ip)
        dest_mac = known_device.mac
        if dest_mac == "":
            raise Exception("Addresse MAC inconnue {}".format(packet.dest_ip))
        desired_ip, desired_mac, desired_mask = self.get_correct_ip_mac_mask(
            packet.dest_ip, packet.dest_mask)

        frame = Frame(
            src_ip=desired_ip,
            src_mac=desired_mac,
            dest_ip=packet.dest_ip,
            dest_mac=dest_mac,
            data=packet.data,
            mask=packet.dest_mask,
            dest_orig_ip=packet.dest_orig_ip,
            src_orig_ip=packet.src_orig_ip)
        frame.last_router = packet.last_router
        frame.switch_src = packet.switch_src

        for switch_routes in self.switch_routes_table:
            if switch_routes.mac == frame.dest_mac:
                frame.switch_org_routes = switch_routes.routes
                frame.switch_routes = switch_routes.routes

        frame.is_outside = packet.is_outside
        return frame


class Computer(Device):
    def __init__(self, name, network_connect):
        super().__init__(name, network_connect)
        self.arp_table = []
        self.devices = []
        self.switch = None
        self.router = None
        self.switch_routes_table = []

    def is_mac_known(self, ip):
        known = None
        for arp_info in self.arp_table:
            if arp_info.ip == ip:
                known = arp_info
                break
        return known

    def send_frame(self, packet):
        to_txt(
            "{} envoie une Trame à {}\n".format(
                self.name,
                self.switch.name))
        self.switch.listen_incoming_requests(self.generate_frame(packet))

    def send_arp_request(self, packet):
        to_txt(
            "{} envoie une reqête ARP à {}\n".format(
                self.name,
                self.switch.name))
        packet = self.generate_arp_request(packet)
        packet.switch_src = self.switch
        self.switch.listen_incoming_requests(packet)

    def generate_frame(self, packet):
        known_device = self.is_mac_known(packet.dest_ip)
        dest_mac = known_device.mac
        if dest_mac == "":
            raise Exception("Addresse MAC inconnue {}".format(packet.dest_ip))
        frame = Frame(
            src_ip=self.net_connect.net_info.ip,
            src_mac=self.net_connect.net_inter.mac,
            dest_ip=packet.dest_ip,
            dest_mac=dest_mac,
            data=packet.data,
            mask=packet.dest_mask,
            dest_orig_ip=packet.dest_orig_ip,
            src_orig_ip=packet.src_orig_ip)
        frame.switch_src = packet.switch_src

        for switch_routes in self.switch_routes_table:
            if switch_routes.mac == frame.dest_mac:
                frame.switch_org_routes = switch_routes.routes
                frame.switch_routes = switch_routes.routes

        frame.is_outside = packet.is_outside
        return frame

    def generate_arp_request(self, packet):
        arp_request = ARPRequestPacket(
            src_ip=self.net_connect.net_info.ip,
            src_mac=self.net_connect.net_inter.mac,
            dest_ip=packet.dest_ip,
            mask=packet.dest_mask,
            dest_orig_ip=packet.dest_orig_ip,
            src_orig_ip=packet.src_orig_ip)
        arp_request.switch_org_routes = []
        arp_request.is_outside = packet.is_outside
        return arp_request

    def generate_arp_response(self, packet):
        arp_response = ARPResponsePacket(
            src_ip=self.net_connect.net_info.ip,
            src_mac=self.net_connect.net_inter.mac,
            dest_ip=packet.src_ip,
            dest_mac=packet.src_mac,
            mask=packet.dest_mask,
            dest_orig_ip=packet.dest_orig_ip,
            src_orig_ip=packet.src_orig_ip)
        arp_response.switch_src = packet.switch_src
        arp_response.switch_org_routes = packet.switch_org_routes
        arp_response.switch_routes = packet.switch_org_routes[::-1]
        arp_response.is_outside = packet.is_outside
        return arp_response

    def is_local(self, packet):
        network_analysis = NetworkAnalysis(packet.dest_ip, packet.dest_mask)
        dest_net_addr = network_analysis.get_network_address()
        src_net_addr = NetworkAnalysis(
            self.net_connect.net_info.ip,
            self.net_connect.net_info.mask).get_network_address()
        if dest_net_addr != src_net_addr:
            return False
        return True

    def get_default_gateway(self):
        network_analysis = NetworkAnalysis(
            self.net_connect.net_info.ip,
            self.net_connect.net_info.mask)
        net_addr = network_analysis.get_network_address()
        desired_ip = ""
        desired_mask = ""
        for route_info in self.router.routing_table:
            if net_addr == route_info.net_addr:
                desired_ip = route_info.ip
                desired_mask = route_info.mask
                break
        if desired_ip == "":
            raise Exception(
                "Le routeur n'a pas d'interface réseau pour l'addresse : {}".format(net_addr))
        return desired_ip, desired_mask

    def send_packet(self, packet):
        if self.is_local(packet):
            if self.is_mac_known(packet.dest_ip):
                self.send_frame(packet)
            else:
                self.send_arp_request(packet)
                if self.is_mac_known(packet.dest_ip):
                    self.send_frame(packet)
                else:
                    to_txt(
                        "{} n'existe pas dans le réseau\n".format(
                            packet.dest_orig_ip))
        else:
            gateway_ip, gateway_mask = self.get_default_gateway()
            packet.dest_ip = gateway_ip
            packet.dest_mask = gateway_mask
            packet.is_outside = True
            self.send_packet(packet)

    def __str__(self):
        result = '-------------------------------------------------------\n'
        result += ("Informations de: {} - {} - {}\n".format(self.name,
                   self.net_connect.net_info.ip, self.net_connect.net_inter.mac))
        result += "Table ARP\n"
        for e in self.arp_table:
            result += ("{}\t{}\n".format(e.ip, e.mac))
        return result + "-------------------------------------------------------\n"

    def update_arp_table(self, packet):
        to_txt("{} met à jour sa table ARP".format(self.name))
        new_ip, new_mac = packet.src_ip, packet.src_mac
        is_there = False
        for arp in self.arp_table:
            if arp.ip == new_ip:
                is_there = True
                break
        if not is_there:
            arp_info = ARPInfo(new_ip, new_mac)
            self.arp_table.append(arp_info)
        for arp_info in self.arp_table:
            to_txt("{} - {}".format(arp_info.ip, arp_info.mac))

    def send_arp_response(self, packet):
        self.switch.listen_incoming_requests(
            self.generate_arp_response(packet))

    def listen_incoming_request(self, packet):
        to_txt("{} reçoit un packet".format(self.name))
        if isinstance(packet, ARPRequestPacket):
            if packet.dest_ip != self.net_connect.net_info.ip:
                to_txt("{} ignore un packet\n".format(self.name))
            else:
                self.update_arp_table(packet)
                to_txt("Ce packet est pour moi")
                switch_org_routes = packet.switch_org_routes[::-1]
                self.update_switch_routes_table(
                    packet.src_mac, switch_org_routes)
                self.send_arp_response(packet)
        elif isinstance(packet, ARPResponsePacket):
            self.update_arp_table(packet)
            if packet.dest_mac != self.net_connect.net_inter.mac:
                return
            else:
                if packet.dest_ip != self.net_connect.net_info.ip:
                    return
                else:
                    to_txt("Réception de la réponse ARPResponse\n")
                    self.update_switch_routes_table(
                        packet.src_mac, packet.switch_org_routes)
        elif isinstance(packet, Frame):
            self.update_arp_table(packet)
            to_txt("###############################################")
            to_txt("Réception des données par: {} [{}]".format(
                self.name, self.net_connect.net_info.ip))
            to_txt("Source des données: {}".format(packet.src_orig_ip))
            to_txt("Contenu du message: {}".format(packet.data))
            to_txt("###############################################")
            to_txt("\n\n\n\n")

    def update_switch_routes_table(self, mac, routes):
        self.switch_routes_table.append(SwitchRouteTable(mac, routes))
