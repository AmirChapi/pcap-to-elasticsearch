from pathlib import Path
import argparse
import os
from prometheus_client import Counter, start_http_server

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

