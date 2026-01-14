# PCAP to Elasticsearch + Prometheus Metrics

A small Python service that reads a PCAP/PCAPNG file, extracts basic packet fields, stores each packet as a single document in Elasticsearch, and exposes Prometheus metrics via `/metrics`.

---



## Project Structure

- `pcap_service.py` - main service
- `data/caputure.pcapng` - example PCAPNG file used by default
## Example PCAP File

Download a sample PCAP/PCAPNG from https://apackets.com/pcaps and place it here:
- `data/caputure.pcapng`

Then run:
```powershell
py .\pcap_service.py --pcap ".\data\caputure.pcapng"


---

## How to Run

### 1) Prerequisites
- Python 3.10+ (tested also with Python 3.13)
- Docker Desktop (to run Elasticsearch)

### 2) Install Python Dependencies
From the project directory:

```bash
py -m pip install scapy prometheus-client "elasticsearch>=8,<9"



Start Elasticsearch (Docker)

docker run -d --name es01 -p 9200:9200 -p 9300:9300 `
  -e "discovery.type=single-node" `
  -e "xpack.security.enabled=true" `
  -e "xpack.security.http.ssl.enabled=false" `
  -e "ELASTIC_PASSWORD=MyStrongPass123!" `
  -e "ES_JAVA_OPTS=-Xms1g -Xmx1g" `
  docker.elastic.co/elasticsearch/elasticsearch:8.13.4

#test
curl.exe -u elastic:MyStrongPass123! http://localhost:9200

Environment Variables (PowerShell example)

$env:ELASTIC_URL="http://127.0.0.1:9200"
$env:ELASTIC_INDEX="pcap-packets"
$env:ELASTIC_USER="elastic"
$env:ELASTIC_PASSWORD="MyStrongPass123!"
$env:METRICS_PORT="9100"


Run the Service

py .\pcap_service.py


Example Document Written to Elasticsearch

curl.exe -u elastic:MyStrongPass123! "http://localhost:9200/pcap-packets/_search?size=2&_source=timestamp,src_ip,dst_ip,src_port,dst_port,l4_protocol,packet_length&pretty"

