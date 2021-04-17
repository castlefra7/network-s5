def mask_length(mask):
    sp_mask = mask.split(".")
    result = 0
    for v in sp_mask:
        result += len(v)
    return result


def complete_mask(mask_b):
    ending = ""
    for b in range(32 - 1, mask_length(mask_b) - 1, -1):
        ending += "0"
        if b % 8 == 0:
            ending += "."
    return mask_b + ending[::-1]


def create_binary_mask(cidr):
    result = ""
    for b in range(int(cidr)):
        result += "1"
        if (b + 1) % 8 == 0 and (b + 1) != 32:
            result += "."
    return result


def cidr_to_b_mask(cidr):
    if int(cidr) > 32 or int(cidr) <= 0:
        raise Exception("Veuillez entrer un CIDR valide")
    c_mask = complete_mask(create_binary_mask(cidr))
    return c_mask


def cidr_to_mask(cidr):
    mask_b = cidr_to_b_mask(cidr)
    sp_mask_b = mask_b.split(".")
    result = ""
    for iM in range(len(sp_mask_b)):
        result += str(int(sp_mask_b[iM], base=2)) + "."
    return result[0: len(result) - 1]


def calculate_mask(mask):
    if mask == '':
        raise Exception("Veuillez entrer un masque valide")
    if mask.count(".") >= 1:
        sp_mask = mask.split(".")
        if len(sp_mask) != 4:
            raise Exception("Veuillez entrer un masque valide")
        return mask

    return cidr_to_mask(mask)


class NetworkAnalysis:
    def __init__(self, ip=None, mask=None):
        self.ip = ip
        self.mask = calculate_mask(mask)

    def get_network_address(self):
        ip_sp, mask_sp = self.split_values()
        if len(ip_sp) != len(mask_sp):
            return None
        result = []
        for iTer in range(len(ip_sp)):
            result.append(str(ip_sp[iTer] & mask_sp[iTer]))
        return '.'.join(result)

    def get_broadcast_ip(self):
        ip_sp, mask_sp = self.split_values()
        for iTer in range(len(mask_sp)):
            mask_sp[iTer] = mask_sp[iTer] ^ 255
        result = []

        for iTer in range(len(ip_sp)):
            result.append(str(ip_sp[iTer] | mask_sp[iTer]))

        return '.'.join(result)

    def get_hosts_number(self):
        ip_sp, mask_sp = self.split_values()
        result = 0
        mask_binary = ""
        for iTer in range(len(mask_sp)):
            mask_binary += str(f"{mask_sp[iTer]:08b}")
        for s in mask_binary:
            if s == '0':
                result += 1
        return 2 ** result - 2

    def get_first_ip(self):
        if self.get_hosts_number() < 2:
            return self.ip
        network_address = [
            int(numb)
            for numb in self.get_network_address().split('.')
        ]
        network_address[len(network_address) - 1] += 1
        network_address = [str(numb) for numb in network_address]
        return '.'.join(network_address)

    def get_last_ip(self):
        if self.get_hosts_number() < 2:
            return self.ip
        sp_broadcast_address = [
            int(numb)
            for numb in self.get_broadcast_ip().split('.')
        ]
        sp_broadcast_address[len(sp_broadcast_address) - 1] -= 1
        sp_broadcast_address = [str(numb) for numb in sp_broadcast_address]
        return '.'.join(sp_broadcast_address)

    def split_values(self):
        ip_sp = [int(numb) for numb in self.ip.split(".")]
        mask_sp = [int(numb) for numb in self.mask.split(".")]
        return ip_sp, mask_sp
