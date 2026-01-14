import time
import argparse
import os

from prometheus_client import Counter, start_http_server
from elasticsearch import Elasticsearch
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.inet6 import IPv6
from scapy.utils import PcapNgReader
from pathlib import Path




DEFAULT_PCAP = Path(__file__).parent / "data" / "caputure.pcapng"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--pcap",
    default=str(DEFAULT_PCAP),
    help="Path to pcap/pcapng file (default: ./data/caputure.pcapng)"
)
args = parser.parse_args()

pcap_path = args.pcap
print("Using PCAP:", pcap_path)

if not os.path.exists(pcap_path):
    print("ERROR: PCAP file not found:", pcap_path)
    raise SystemExit(1)

METRICS_PORT = int(os.environ.get("METRICS_PORT", "9100"))
start_http_server(METRICS_PORT)
print("Metrics server running on port", METRICS_PORT, "-> /metrics")


packets_counter = Counter(
    "pcap_packets_total",
    "Total packets read from pcap file",
    ["protocol"]
)

bytes_counter = Counter(
    "pcap_bytes_total",
    "Total bytes read from pcap file",
    ["protocol"]
)

elastic_write_counter = Counter(
    "pcap_elastic_write_total",
    "Total Elasticsearch write attempts",
    ["status"]
)

ELASTIC_URL = os.environ.get("ELASTIC_URL", "http://127.0.0.1:9200")
ELASTIC_INDEX = os.environ.get("ELASTIC_INDEX", "pcap-packets")

ELASTIC_USER = os.environ.get("ELASTIC_USER")        
ELASTIC_PASSWORD = os.environ.get("ELASTIC_PASSWORD")  

ELASTIC_RETRIES = int(os.environ.get("ELASTIC_RETRIES", "3"))
ELASTIC_RETRY_SLEEP = float(os.environ.get("ELASTIC_RETRY_SLEEP", "0.2"))

if ELASTIC_USER and ELASTIC_PASSWORD:
    es = Elasticsearch(
        ELASTIC_URL,
        basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD),
        request_timeout=10
    )
else:
    es = Elasticsearch(
        ELASTIC_URL,
        request_timeout=10
    )

try:
    info = es.info()
    print("Elasticsearch connected:", info["version"]["number"], "index:", ELASTIC_INDEX)
except Exception as e:
    print("ERROR: Could not connect to Elasticsearch:", e)
    raise SystemExit(1)

def extract_fields(pkt):
    data = {
        "timestamp": float(getattr(pkt, "time", 0.0)),
        "packet_length": len(pkt),
        "src_ip": None,
        "dst_ip": None,
        "src_port": None,
        "dst_port": None,
        "l4_protocol": "other",
    }

    # IPv4
    if IP in pkt:
        data["src_ip"] = pkt[IP].src
        data["dst_ip"] = pkt[IP].dst

        if TCP in pkt:
            data["l4_protocol"] = "tcp"
            data["src_port"] = pkt[TCP].sport
            data["dst_port"] = pkt[TCP].dport
        elif UDP in pkt:
            data["l4_protocol"] = "udp"
            data["src_port"] = pkt[UDP].sport
            data["dst_port"] = pkt[UDP].dport
        elif ICMP in pkt:
            data["l4_protocol"] = "icmp"

    # IPv6
    elif IPv6 in pkt:
        data["src_ip"] = pkt[IPv6].src
        data["dst_ip"] = pkt[IPv6].dst

        if TCP in pkt:
            data["l4_protocol"] = "tcp"
            data["src_port"] = pkt[TCP].sport
            data["dst_port"] = pkt[TCP].dport
        elif UDP in pkt:
            data["l4_protocol"] = "udp"
            data["src_port"] = pkt[UDP].sport
            data["dst_port"] = pkt[UDP].dport

    return data

# ---- Read PCAP + metrics + write to Elasticsearch ----
packets_total = {"tcp": 0, "udp": 0, "icmp": 0, "other": 0}
bytes_total = {"tcp": 0, "udp": 0, "icmp": 0, "other": 0}

count = 0
fail_prints = 0

with PcapNgReader(pcap_path) as reader:
    for pkt in reader:
        count += 1

        data = extract_fields(pkt)
        proto = data["l4_protocol"]

        # Local summary counters
        packets_total[proto] += 1
        bytes_total[proto] += data["packet_length"]

        # Prometheus counters
        packets_counter.labels(protocol=proto).inc(1)
        bytes_counter.labels(protocol=proto).inc(data["packet_length"])

        if count <= 5:
            print(f"\nPacket #{count}")
            print(data)

        written = False

        for attempt in range(1, ELASTIC_RETRIES + 1):
            try:
                es.index(index=ELASTIC_INDEX, document=data)
                elastic_write_counter.labels(status="success").inc(1)
                written = True
                break
            except Exception as e:
                if attempt < ELASTIC_RETRIES:
                    print(
                        f"WARN: ES write failed (attempt {attempt}/{ELASTIC_RETRIES}) -> retrying. Error: {e}"
                    )
                    time.sleep(ELASTIC_RETRY_SLEEP)
                else:
                    elastic_write_counter.labels(status="fail").inc(1)
                    if fail_prints < 5:
                        print(
                            f"ERROR: ES write failed after {ELASTIC_RETRIES} attempts. Error: {e}"
                        )
                        fail_prints += 1




