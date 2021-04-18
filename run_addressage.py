import tkinter as tk
import tkinter.messagebox as msg
from network_analysis import NetworkAnalysis


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.btn_calculate = tk.Button(self)

        entry_text = tk.StringVar()
        entry_text.set("3124::DEAD:CAFE:FF:FE00:1")
        entry_text_mask = tk.StringVar()
        entry_text_mask.set("80")

        self.input_mask = tk.Entry(self, textvariable=entry_text_mask)
        self.label_mask = tk.Label(self, text="Saisissez votre masque ou bien CIDR (Si IPV6 alors CIDR seulement):")
        self.input_ip = tk.Entry(self, textvariable=entry_text)
        self.label_ip = tk.Label(self, text="Saisissez une addresse IPV4 ou IPV6:")

        self.master = master
        self.create_widgets()

        self.pack()

    def create_widgets(self):
        self.label_ip.pack(side="top")

        self.input_ip.pack(side="top", fill=tk.X)
        self.label_mask.pack(side="top")

        self.input_mask.pack(side="top", fill=tk.X)

        self.btn_calculate["text"] = "Analyser"
        self.btn_calculate["command"] = self.calculate
        self.btn_calculate.pack(side="top", fill=tk.X)

    def calculate(self):

        try:
            network_analysis = NetworkAnalysis(self.input_ip.get(), self.input_mask.get())

            if network_analysis.is_ipv6():
                network_address = network_analysis.get_network_address_v6()
                number_addresses = network_analysis.get_hosts_number_v6()
                first_address = network_analysis.get_first_ip_v6()
                last_address = network_analysis.get_last_ip_v6()
                value = """
                Addresse réseau: \n{}
                Nombre addresses disponible: \n{}
                Première addresse: \n{}
                Dernière addresse: \n{}
                """.format(network_address, number_addresses, first_address, last_address)
            else:
                network_address = network_analysis.get_network_address()
                diff_address = network_analysis.get_broadcast_ip()
                number_addresses = network_analysis.get_hosts_number()
                first_address = network_analysis.get_first_ip()
                last_address = network_analysis.get_last_ip()
                value = """
                Addresse réseau: {}
                Addresse diffusion: {}
                Nombre addresses disponible: {}
                Première addresse: {}
                Dernière addresse: {}
                """.format(network_address, diff_address, number_addresses, first_address,
                           last_address)

            msg.showinfo("Description réseau", value)
        except Exception as e:
            msg.showerror("Erreur", e)


root = tk.Tk("Analyse réseau")
root.geometry("400x120")
app = Application(master=root)
app.mainloop()
