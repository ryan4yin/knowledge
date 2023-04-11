from scapy.all import *

load_layer("tls")

infliestr = "/path/to/mytest.pcap"

pkts = sniff(offline=infliestr)

# 过滤出所有的 SNI 信息

all_servernames = set()

for i, pkt in enumerate(pkts):
    if not pkt.haslayer("TLS"):
        continue
    if 'Client Hello' not in pkt.summary():
        continue
    try:
        pkt_servernames = (it.servername.decode() for it in pkt['TLS']['TLS Handshake - Client Hello']['TLS Extension - Server Name'].servernames)
        all_servernames.update(pkt_servernames)
    except Exception as e:
        continue

print(all_servernames)
