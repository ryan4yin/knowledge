# 由 ChatGPT 4 生成，我修改了个别错误
from scapy.all import *
from scapy.layers.tls.all import *
import sys

def extract_sni(packet):
    if packet.haslayer(TLSClientHello):
        client_hello = packet[TLSClientHello]
        for extension in client_hello.ext:
            if isinstance(extension, TLS_Ext_ServerName):
                for server_name in extension.servernames:
                    yield server_name.servername.decode('utf-8')


def main():
    if len(sys.argv) != 2:
        print("Usage: python read_sni_from_pcap.py <pcap_file>")
        sys.exit(1)
    pcap_file = sys.argv[1]

    try:
        packets = rdpcap(pcap_file)
    except Scapy_Exception as e:
        print(f"Error reading pcap file: {e}")
        sys.exit(1)

    sni_set = set()
    for packet in packets:
        sni_set.update(extract_sni(packet))

    print(sni_set)

if __name__ == "__main__":
    main()
