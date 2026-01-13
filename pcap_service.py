from pathlib import Path
import argparse
import os

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