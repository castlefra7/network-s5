def mask_length(mask):
    sp_mask = mask.split(".")
    result = 0
    for v in sp_mask:
        result += len(v)
    return result


def create_binary_mask(cidr):
    result = ""
    for b in range(40):
        if b < int(cidr):
            result += "1"
        else:
            result += "0"
        if (b + 1) % 8 == 0 and (b + 1) != 32:
            result += "."
        if b == 32:
            break
    return result


def cidr_to_b_mask(cidr):
    if int(cidr) > 128 or int(cidr) <= 0:
        raise Exception("Veuillez entrer un CIDR valide")
    c_mask = create_binary_mask(cidr)
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


def or_operator(part_ip, part_mask):
    sp_part_ip = list(part_ip)
    sp_part_mask = part_mask.split(".")
    n_sp_part_mask = []
    for part in sp_part_mask:
        n_sp_part_mask.append(str(int(part, base=2) ^ 15))
    result = []
    for i in range(len(sp_part_ip)):
        c = sp_part_ip[i]
        c_i = 0
        if c == 'A':
            c_i = 10
        elif c == 'B':
            c_i = 11
        elif c == 'C':
            c_i = 12
        elif c == 'D':
            c_i = 13
        elif c == 'E':
            c_i = 14
        elif c == 'F':
            c_i = 15
        else:
            c_i = int(sp_part_ip[i])

        r = int(c_i) | int(n_sp_part_mask[i])
        v = ""
        if r == 10:
            v = 'A'
        elif r == 11:
            v = 'B'
        elif r == 12:
            v = 'C'
        elif r == 13:
            v = 'D'
        elif r == 14:
            v = 'E'
        elif r == 15:
            v = 'F'
        else:
            v = str(r)
        result.append(v)
    return ''.join(result)


def and_operator(part_ip, part_mask):
    sp_part_ip = list(part_ip)
    sp_part_mask = part_mask.split(".")
    n_sp_part_mask = []
    for part in sp_part_mask:
        n_sp_part_mask.append(str(int(part, base=2)))
    result = []
    for i in range(len(sp_part_ip)):
        c = sp_part_ip[i]
        c_i = 0
        if c == 'A':
            c_i = 10
        elif c == 'B':
            c_i = 11
        elif c == 'C':
            c_i = 12
        elif c == 'D':
            c_i = 13
        elif c == 'E':
            c_i = 14
        elif c == 'F':
            c_i = 15
        else:
            c_i = int(sp_part_ip[i])

        r = int(c_i) & int(n_sp_part_mask[i])
        v = ""
        if r == 10:
            v = 'A'
        elif r == 11:
            v = 'B'
        elif r == 12:
            v = 'C'
        elif r == 13:
            v = 'D'
        elif r == 14:
            v = 'E'
        elif r == 15:
            v = 'F'
        else:
            v = str(r)
        result.append(v)
    return ''.join(result)


class NetworkAnalysis:
    def __init__(self, ip=None, mask=None):
        self.ip = ip
        if not self.is_ipv6():
            self.mask = calculate_mask(mask)
        else:
            self.mask = mask

    def is_ipv6(self):
        if self.ip.count(":") >= 1:
            return True
        return False

    def get_full_ip_v6(self):
        if self.ip.count(" ") > 0:
            raise Exception("Supprimer les espaces dans l'addresse IP")
        ip = self.ip
        if self.ip.count("::") > 0:
            count = 0
            ip_two_parts = self.ip.split("::")
            first_part_count = len(ip_two_parts[0].split(":"))
            second_part_count = 0
            if len(ip_two_parts) > 1:
                if ip_two_parts[1].count(":") > 0:
                    second_part_count = len(ip_two_parts[1].split(":"))
            count = first_part_count + second_part_count
            remain = 8 - count
            sp_ip = list(ip)
            new_ip = []
            sub_str = ""
            for i in range(len(sp_ip)):
                if sp_ip[i] == ':':
                    if sub_str != "":
                        new_ip.append(sub_str)
                    if sp_ip[(i+1) % len(sp_ip)] == ':':
                        for j in range(remain):
                            new_ip.append("0")
                    sub_str = ""
                else:
                    sub_str += str(sp_ip[i])
            if sub_str != "":
                new_ip.append(sub_str)
            ip = new_ip
        else:
            ip = self.ip.split(":")
        return ip

    def get_polished_ipv6(self):

        ip_sp = self.get_full_ip_v6()
        new_ip_sp = []
        for numb in ip_sp:
            if len(numb) < 4:
                remain_zero = ""
                i_remain = 4 - len(numb)
                for r in range(i_remain):
                    remain_zero += "0"
                new_numb = remain_zero + numb
                new_ip_sp.append(new_numb)
            else:
                new_ip_sp.append(numb)
        return new_ip_sp

    def get_decimal_ipv6(self):
        ip_sp = self.get_polished_ipv6()
        new_ip_sp = []
        for numb in ip_sp:
            list_numb = list(numb)
            new_numb = ""
            for c in list_numb:
                new_numb += c
            new_ip_sp.append(new_numb)
        return new_ip_sp

    def get_ipv6_mask(self):
        cidr = int(self.mask)
        bit_mask = ""
        numb_1 = 0
        for i in range(200):
            if (i + 1) % 5 == 0:
                if (i + 1) % 20 == 0:
                    bit_mask += ":"
                else:
                    bit_mask += "."
            else:

                if numb_1 >= cidr:
                    bit_mask += "0"
                else:
                    bit_mask += "1"
                numb_1 += 1
                if numb_1 >= 128:
                    break
        return bit_mask

    def get_network_address_v6(self):
        ip_sp = self.get_decimal_ipv6()
        mask = self.get_ipv6_mask().split(":")
        final = []
        for i in range(len(ip_sp)):
            final.append(and_operator(ip_sp[i], mask[i]))
        return ':'.join(final)

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

    def get_hosts_number_v6(self):
        i_mask = int(self.mask)
        return 2**(128 - i_mask)

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

    def get_first_ip_v6(self):
        return self.get_network_address_v6()

    def get_last_ip_v6(self):
        ip_sp = self.get_decimal_ipv6()
        mask_sp = self.get_ipv6_mask().split(":")
        final = []
        for i in range(len(ip_sp)):
            final.append(or_operator(ip_sp[i], mask_sp[i]))
        return '.'.join(final)

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
