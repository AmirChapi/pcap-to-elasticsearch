# PCAP to Elasticsearch + Prometheus Metrics

A small Python service that reads a PCAP/PCAPNG file, extracts basic packet fields, stores each packet as a single document in Elasticsearch, and exposes Prometheus metrics via `/metrics`.

---

## Project Structure

- `pcap_service.py` - main service (reads PCAP, writes to Elasticsearch, exposes metrics)
- `docker-compose.yml` - runs Elasticsearch + the service
- `Dockerfile` - builds the Python service image
- `requirements.txt` - Python dependencies
- `data/caputure.pcapng` - example PCAPNG file (optional)

---

## Example PCAP File

You can download sample PCAP/PCAPNG files from:
- https://apackets.com/pcaps

Place a file here (default path used by the service):
- `data/caputure.pcapng`

---

## Docker Compose `.env` (recommended)

Docker Compose automatically loads a `.env` file from the same directory as `docker-compose.yml`.

Create a file named `.env`  and set:

```env
ELASTIC_PASSWORD=YourStrongPasswordHere

How to Run (Recommended: Docker Compose)
1) Prerequisites

Docker Desktop

2) Start the stack

From the project directory (where docker-compose.yml is located):

docker compose up -d --build


3) Verify Elasticsearch (requires credentials)

http://localhost:9200

curl.exe http://localhost:9100/metrics

Example Document Written to Elasticsearch

curl.exe -u elastic:MyStrongPass123! "http://localhost:9200/pcap-packets/_search?size=2&_source=timestamp,src_ip,dst_ip,src_port,dst_port,l4_protocol,packet_length&pretty"

