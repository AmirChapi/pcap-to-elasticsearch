Here is a clean, organized, and professional version of your `README.md`.

I have restructured it so that the **Architecture** section explains *what* we built, and the **Deployment** section explains *how* to run it chronologically, removing the duplicate commands that were scattered at the top.

You can copy-paste the code block below directly into your file.

---

```markdown
# 🦈 PCAP to Elasticsearch – Kubernetes & Helm Deployment

## 📌 Project Overview
This project demonstrates a full migration of a Python-based PCAP processing service from **Docker Compose** to a **production-grade Kubernetes architecture**, fully managed using **Helm**.

The system ingests network traffic data from PCAP/PCAPNG files, processes it using Python + Scapy, exposes Prometheus metrics, and stores structured packet data in Elasticsearch, with Kibana used for visualization and exploration.

---

## 🧱 Architecture Components

The solution consists of the following components deployed on Kubernetes:

* **PCAP Service (Python)**
    * Reads PCAP files and extracts packet metadata.
    * Pushes JSON documents into Elasticsearch.
    * Exposes Prometheus metrics on port `9100`.
* **Elasticsearch**
    * Acts as both the search engine and primary data store.
    * Deployed as a `StatefulSet` to preserve identity and storage.
    * Secured with TLS and Service Tokens.
* **Kibana**
    * Visualization layer for Elasticsearch data.
    * Exposed externally via Ingress.
* **Ingress NGINX**
    * Entry point into the cluster.
    * Handles HTTPS and TLS termination.
    * Routes traffic based on hostname (`kibana.local`).
* **Helm**
    * Used to package, template, and manage the entire Kubernetes deployment.

---

## 🚀 Why Helm?
Instead of managing raw Kubernetes YAML files, this project uses **Helm** to:
* Parameterize configuration via `values.yaml`.
* Avoid duplication across manifests.
* Support multiple environments (dev / staging / prod).
* Enable versioned, repeatable deployments.

**Helm turns Kubernetes from static YAML into a manageable system.**

---

## 📁 Helm Chart Structure

```text
helm/
├── Chart.yaml             # Chart metadata
├── values.yaml            # Central configuration
└── templates/             # Dynamic manifests
    ├── pcap-service.yaml
    ├── elasticsearch.yaml
    ├── kibana.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    └── secrets.yaml

```

---

## 🔐 Security Design

### Secrets

Sensitive data (credentials, tokens, certificates) are stored as Kubernetes **Secrets**, not in Git.

* Elasticsearch credentials & Service account tokens.
* TLS private keys.

### TLS & Certificates

The system uses **TLS in two layers**:

1. **External TLS (User → Ingress → Kibana):** Traffic is encrypted using a self-signed certificate managed by Ingress.
2. **Internal TLS (PCAP Service → Elasticsearch):** The Python service connects to Elasticsearch over HTTPS using a mounted CA certificate.

---

## 🚀 Deployment (How to Run)

To deploy the application on a local Kubernetes cluster (Docker Desktop / Minikube), follow these steps strictly in order.

### 1. Create Environment

Create a dedicated namespace for the project to isolate resources:

```bash
kubectl create namespace pcap

```

### 2. Initial Installation

Deploy the Helm chart.

> **Note:** Kibana might enter a `CrashLoopBackOff` or `NotReady` state initially. This is expected because we haven't generated the security token yet.

```bash
helm install pcap-stack . -n pcap -f values.yaml

```

### 3. Generate Security Token

Since local Docker volumes are ephemeral, we must generate a new enrollment token for Kibana every time we restart the environment from scratch:

```bash
kubectl exec -it -n pcap elasticsearch-0 -- bin/elasticsearch-service-tokens create elastic/kibana kibana-live-token

```

> **Action Required:** Copy the generated token output from the terminal.

### 4. Update Configuration

1. Open `pcap-analyzer/values.yaml`.
2. Locate the `serviceAccountToken` field.
3. Paste the token you copied in Step 3.
4. Save the file.

### 5. Apply Configuration

Upgrade the deployment to apply the new token to Kibana:

```bash
helm upgrade pcap-stack . -n pcap -f values.yaml

```

### 6. Verify Status

Ensure all pods are running (Elasticsearch, Kibana, and PCAP Analyzer):

```bash
kubectl get pods -n pcap

```

*Wait until all pods show `1/1 Running`.*

---

## 🌐 Accessing the Application

Once the pods are running, you need to forward ports to access the services from your local machine.

### Access Kibana (Dashboard)

1. Open a new terminal and run:
```bash
kubectl -n ingress-nginx port-forward svc/ingress-nginx-controller 8443:443

```


2. Open your browser to: **[https://kibana.local:8443](https://www.google.com/search?q=https://kibana.local:8443)**
3. Login with user `elastic` and the password defined in your values file.

### Access Prometheus Metrics (Debug)

1. Find your PCAP pod name:
```bash
kubectl get pods -n pcap

```


2. Run the port-forward (replace `pcap-service-XXXX` with your actual pod name):
```bash
kubectl port-forward -n pcap pcap-service-XXXXXX 9100:9100

```


3. Open your browser to: **[http://localhost:9100/metrics](https://www.google.com/search?q=http://localhost:9100/metrics)**

---

## 🧠 Key Takeaways

* **State Management:** Elasticsearch is stateful (StatefulSet), while the PCAP analyzer is stateless (Deployment).
* **Self-Healing:** Kubernetes automatically restarts pods if they crash.
* **Ingress:** Centralizes traffic management and SSL termination.
* **Helm:** Makes complex deployments repeatable and clean.

## 📌 Future Improvements

* Add **Horizontal Pod Autoscaler (HPA)**.
* Integrate full **Prometheus & Grafana** stack.
* Add **CI/CD pipeline** with Argo CD.
* Use external secret managers (Vault / SOPS).

```

```