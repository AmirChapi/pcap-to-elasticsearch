# PCAP to Elasticsearch – Kubernetes & Helm Deployment

## 📌 Project Overview

This project demonstrates a full migration of a Python-based PCAP processing service
from **Docker Compose** to a **production-grade Kubernetes architecture**, fully managed using **Helm**.

The system ingests network traffic data from PCAP/PCAPNG files, processes it using Python + Scapy,
exposes Prometheus metrics, and stores structured packet data in Elasticsearch,
with Kibana used for visualization and exploration.

---

## 🧱 Architecture Components

The solution consists of the following components deployed on Kubernetes:

* **PCAP Service (Python)**

  * Reads PCAP files
  * Extracts packet metadata
  * Pushes documents into Elasticsearch
  * Exposes Prometheus metrics on port `9100`
  kubectl port-forward pcap-service-XXXXXX 9100:9100 -n pcap

* **Elasticsearch**

  * Acts as both search engine and primary data store
  * Deployed as a `StatefulSet` to preserve identity and storage
  * Secured with TLS
  kubectl port-forward elasticsearch-0 9200:9200 -n pcap

* **Kibana**

  * Visualization layer for Elasticsearch data
  * Exposed externally via Ingress
  * Uses service account authentication
  kubectl -n ingress-nginx port-forward svc/ingress-nginx-controller 8443:443
  URL = https://kibana.local:8443/

  TOKEN FOR KIBANA = kubectl exec -it -n pcap elasticsearch-0 -- bin/elasticsearch-service-tokens create elastic/kibana kibana-token-v

* **Ingress NGINX**

  * Entry point into the cluster
  * Handles HTTPS and TLS termination
  * Routes traffic based on hostname

* **Helm**

  * Used to package, template, and manage the entire Kubernetes deployment

---

## 🚀 Why Helm?

Instead of managing raw Kubernetes YAML files, this project uses **Helm** to:

* Parameterize configuration via `values.yaml`
* Avoid duplication across manifests
* Support multiple environments (dev / staging / prod)
* Enable versioned, repeatable deployments
* Make upgrades and rollbacks safe and simple

In short: **Helm turns Kubernetes from static YAML into a manageable system.**

---

## 📁 Helm Chart Structure

```text
helm/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── pcap-service.yaml
    ├── elasticsearch.yaml
    ├── kibana.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    └── secrets.yaml
```

### Chart.yaml

Defines chart metadata such as name, version, and description.

### values.yaml

Central configuration file containing:

* Image names & tags
* Resource limits
* Elasticsearch credentials
* TLS paths
* Ingress hostnames

### templates/

Contains Kubernetes manifests rendered dynamically using Helm templating.

---

## 🔐 Security Design

### Secrets

Sensitive data (credentials, tokens, certificates) are stored as Kubernetes **Secrets**, not in Git.

* Elasticsearch credentials
* Service account tokens
* TLS private keys

Secrets are injected into pods via:

* Environment variables
* Mounted files

> Secrets are Base64-encoded and stored securely in etcd with RBAC protection.

---

### TLS & Certificates

The system uses **TLS in two layers**:

#### 1️⃣ External TLS (User → Ingress → Kibana)

* Browser encrypts traffic using Kibana’s public certificate
* Ingress terminates TLS (TLS termination)
* Traffic is routed to Kibana service

#### 2️⃣ Internal TLS (PCAP Service → Elasticsearch)

* Python service connects to Elasticsearch over HTTPS
* CA certificate is mounted into the container
* Elasticsearch verifies client trust

This ensures:

* Encrypted traffic over public and internal networks
* Protection against sniffing and MITM attacks

---

## 🌐 Networking & Service Discovery

### Kubernetes Service

Each application is exposed internally via a **Service**:

* Provides a stable virtual IP
* Load balances traffic across pods
* Enables internal DNS resolution

Example:

```text
elasticsearch.pcap.svc.cluster.local
kibana.pcap.svc.cluster.local
```

Pods never talk to IPs directly — only to Services.

---

### Ingress

Ingress acts as the **HTTP(S) gateway**:

* Routes traffic by hostname (`kibana.local`)
* Handles TLS certificates
* Connects external users to internal services

---

## 📦 Stateful vs Stateless Workloads

### Elasticsearch – StatefulSet

Elasticsearch is deployed as a **StatefulSet** because:

* Data persistence is critical
* Pod identity must be stable
* Storage must survive restarts

### PCAP Service – Deployment

PCAP service is stateless:

* No persistent storage required
* Easy horizontal scaling
* Supports rolling updates

---

## 📊 Observability

* Prometheus metrics exposed on `/metrics`
* Packet counts and byte volume by protocol
* Elasticsearch write success/failure counters
* Logs streamed directly via Kubernetes logging

---

## 🔁 From Docker Compose to Kubernetes

### What Docker Compose Provided

* Local orchestration
* Single-host deployment
* Limited scaling and resilience

### What Kubernetes + Helm Added

* Self-healing pods
* Declarative desired state
* Horizontal scalability
* Secure secrets management
* TLS and ingress routing
* Environment abstraction via Helm
* Production readiness

---

## 🧠 Key Takeaways

* Kubernetes manages **desired state**, not individual containers
* Services decouple pods from networking concerns
* Ingress centralizes traffic and security
* Helm makes Kubernetes maintainable at scale
* Stateful workloads require different primitives than stateless ones
* Security must be designed at both network and application levels

---

## ✅ Deployment (Example)

```bash
helm upgrade --install pcap-stack ./helm \
  --namespace pcap \
  --create-namespace
```

---

## 📌 Future Improvements

* Add Horizontal Pod Autoscaler (HPA)
* Integrate Prometheus & Grafana
* Add CI/CD pipeline with Argo CD
* Separate environments with Helm values
* Use external secret managers (Vault / SOPS)

---

