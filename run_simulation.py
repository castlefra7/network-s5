import tkinter as tk
from network_simulation import *

# NETWORK 1
pc_1 = Computer('pc_1', NetworkConnectivity(NetworkInfo('192.168.0.5', '255.255.255.0'),
                                            NetworkInter('00:1B:44:11:3A:B7')))
pc_2 = Computer('pc_2', NetworkConnectivity(NetworkInfo('192.168.0.6', '255.255.255.0'),
                                            NetworkInter('00:1B:44:11:3A:B8')))
pc_3 = Computer('pc_3', NetworkConnectivity(NetworkInfo('192.168.0.7', '255.255.255.0'),
                                            NetworkInter('00:1B:44:11:3A:B9')))
pc_4 = Computer('pc_4', NetworkConnectivity(NetworkInfo('192.168.0.8', '255.255.255.0'),
                                            NetworkInter('00:1B:44:11:3A:C0')))
devices_1 = [pc_1, pc_2, pc_3, pc_4]
switch_1 = Switch(devices_1, 'Switch 1')

for pc in devices_1:
    pc.switch = switch_1
    pc.devices = devices_1

# NETWORK 2
pc_5 = Computer('pc_5', NetworkConnectivity(NetworkInfo('192.168.1.5', '255.255.255.192'),
                                            NetworkInter('00:1B:44:11:3A:C1')))
pc_6 = Computer('pc_6', NetworkConnectivity(NetworkInfo('192.168.1.6', '255.255.255.192'),
                                            NetworkInter('00:1B:44:11:3A:C2')))
pc_7 = Computer('pc_7', NetworkConnectivity(NetworkInfo('192.168.1.7', '255.255.255.192'),
                                            NetworkInter('00:1B:44:11:3A:C3')))
pc_8 = Computer('pc_8', NetworkConnectivity(NetworkInfo('192.168.1.8', '255.255.255.192'),
                                            NetworkInter('00:1B:44:11:3A:C4')))
devices_2 = [pc_5, pc_6, pc_7, pc_8]
switch_2 = Switch(devices_2, 'Switch 2')

for pc in devices_2:
    pc.switch = switch_2
    pc.devices = devices_2

# NETWORK 3
pc_9 = Computer('pc_9', NetworkConnectivity(NetworkInfo('192.168.2.5', '255.255.255.0'),
                                            NetworkInter('00:1B:44:11:3A:D1')))
pc_10 = Computer('pc_10', NetworkConnectivity(NetworkInfo('192.168.2.6', '255.255.255.0'),
                                              NetworkInter('00:1B:44:11:3A:D2')))
devices_3 = [pc_9, pc_10]
switch_3 = Switch(devices_3, 'Switch 3')

for pc in devices_3:
    pc.switch = switch_3
    pc.devices = devices_3

# NETWORK 4
pc_11 = Computer('pc_11', NetworkConnectivity(NetworkInfo('192.168.3.5', '255.255.255.0'),
                                              NetworkInter('00:1B:44:11:3A:E1')))
devices_4 = [pc_11]
switch_4 = Switch(devices_4, 'Switch 4')

for pc in devices_4:
    pc.switch = switch_4
    pc.devices = devices_4

# NETWORK 5
pc_12 = Computer('pc_11', NetworkConnectivity(NetworkInfo('192.168.3.5', '255.255.255.0'),
                                              NetworkInter('00:1B:44:11:3A:E1')))
devices_5 = [pc_11]
switch_4 = Switch(devices_5, 'Switch 5')

for pc in devices_4:
    pc.switch = switch_4
    pc.devices = devices_4

# Router 1
connected_switch_1 = [switch_1, switch_2]

routing_table_1 = [RouteInfo('255.255.255.192', '192.168.1.62', '01:1B:44:11:3A:C1'),
                   RouteInfo('255.255.255.0', '192.168.0.254', '01:1B:44:11:3A:C2')]

router_1 = Router(connected_switch_1, routing_table_1, 'Router 1')

switch_1.connected_devices.append(router_1)
switch_2.connected_devices.append(router_1)

# Router 2
connected_switch_2 = [switch_3, switch_2]

routing_table_2 = [RouteInfo('255.255.255.192', '192.168.1.60', '01:1B:44:11:3A:D1'),
                   RouteInfo('255.255.255.0', '192.168.2.254', '01:1B:44:11:3A:D2')]

router_2 = Router(connected_switch_2, routing_table_2, 'Router 2')

switch_3.connected_devices.append(router_2)
switch_2.connected_devices.append(router_2)

# Router 3
connected_switch_3 = [switch_4, switch_3]
routing_table_3 = [RouteInfo('255.255.255.0', '192.168.3.254', '01:1B:44:11:3A:E1'),
                   RouteInfo('255.255.255.0', '192.168.2.253', '01:1B:44:11:3A:E2')]
router_3 = Router(connected_switch_3, routing_table_3, 'Router 3')

switch_3.connected_devices.append(router_3)
switch_4.connected_devices.append(router_3)

# Add Router to pcs of Network 1 and 2
pc_1.router = router_1
pc_2.router = router_1
pc_3.router = router_1
pc_4.router = router_1
pc_5.router = router_1
pc_6.router = router_1
pc_7.router = router_1
pc_8.router = router_1

# Add Router to pcs of Network 3
pc_9.router = router_2
pc_10.router = router_2

# Add Router to pcs of Network 4
pc_11.router = router_3

# Sending Packets
sender = pc_1
new_packet = Packet(src_ip=sender.net_connect.net_info.ip, src_mac=sender.net_connect.net_inter.mac,
                    dest_ip='192.168.1.6', mask='255.255.255.192', data='Bonjour ça va?')

# Sending Packet when Every Table are Empty
sender.send_packet(new_packet)

# Sending Packet when Every Table are Filled
sender = pc_11
new_packet = Packet(src_ip=sender.net_connect.net_info.ip, src_mac=sender.net_connect.net_inter.mac,
                    dest_ip='192.168.0.5', mask='255.255.255.0', data='Saluut!')
sender.send_packet(new_packet)

# Sending Packet from Network 2
sender = pc_5
new_packet = Packet(src_ip=sender.net_connect.net_info.ip, src_mac=sender.net_connect.net_inter.mac,
                    dest_ip='192.168.3.5', mask='255.255.255.0', data='Bonjour toii!')
sender.send_packet(new_packet)

print(get_str())


def tabify(s, tabsize=10):
    ln = ((len(s) / tabsize) + 1) * tabsize
    return s.ljust(int(ln))


class Information:
    def __init__(self, txt=''):
        self.txt = txt


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.logs = tk.Text(self, width=75, height=25)
        self.txt = tk.Label(self, text="Simulation Réseau")
        self.scrolly = tk.Scrollbar(self, orient="vertical")

        self.master = master
        self.create_widgets()
        self.pack(fill=tk.BOTH)

    def create_widgets(self):

        self.logs.insert(tk.END, get_str())
        self.logs.config(state=tk.DISABLED)

        self.txt.pack()
        self.logs.pack(fill=tk.Y, side=tk.LEFT)

        self.scrolly.config(command=self.logs.yview)
        self.scrolly.pack(fill=tk.Y, side=tk.RIGHT)

        self.logs.config(yscrollcommand=self.scrolly.set)


root = tk.Tk("Simulation réseau")
root.geometry("750x600")
app = Application(master=root)

app.mainloop()
