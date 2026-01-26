FROM python:3.13-slim

WORKDIR /app

# Install OS deps (curl for health/debug)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app code
COPY . /app

EXPOSE 9100

ENV PYTHONUNBUFFERED=1
CMD ["python", "-u", "pcap_service.py"]
