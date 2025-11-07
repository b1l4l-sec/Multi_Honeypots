# Pre-Deployment Verification Checklist

Use this checklist before deploying the honeypot platform.

## System Checks

```bash
# Check Docker is installed and running
docker --version
docker-compose --version
sudo systemctl status docker | grep "active (running)"

# Check available memory (minimum 4GB)
free -h | grep "Mem:" | awk '{print $2}'

# Check disk space (minimum 20GB free)
df -h / | tail -1 | awk '{print $4}'

# Check Python version (3.8+)
python3 --version
```

## File Integrity

```bash
# Verify all required files exist
test -f requirements.txt && echo "requirements.txt: OK"
test -f honeypot_modules/logger.py && echo "logger.py: OK"
test -f honeypot_modules/ssh_honeypot.py && echo "ssh_honeypot.py: OK"
test -f honeypot_modules/http_honeypot.py && echo "http_honeypot.py: OK"
test -f honeypot_modules/ftp_honeypot.py && echo "ftp_honeypot.py: OK"
test -f elk_config/docker-compose.yml && echo "docker-compose.yml: OK"
test -f elk_config/logstash.conf && echo "logstash.conf: OK"

# Verify Python files are valid syntax
python3 -m py_compile honeypot_modules/*.py && echo "All Python files: VALID"
```

## Port Availability

```bash
# Check if required ports are free
for port in 2222 8080 2121 9200 5601; do
    if sudo netstat -tulpn | grep -q ":$port "; then
        echo "Port $port: IN USE (need to free it)"
    else
        echo "Port $port: AVAILABLE"
    fi
done
```

## Python Dependencies

```bash
# Create venv and install packages
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verify installation
pip list | grep -E "paramiko|Flask|pyftpdlib" && echo "All packages: INSTALLED"
```

## Log Directory

```bash
# Create and verify log directory
sudo mkdir -p /var/log/multi_honeypot
sudo chmod 755 /var/log/multi_honeypot
test -d /var/log/multi_honeypot && test -w /var/log/multi_honeypot && echo "Log directory: OK"
```

## Docker Images

```bash
# Pull ELK images (may take 5-10 minutes)
cd elk_config
docker-compose pull

# Verify images are downloaded
docker images | grep -E "elasticsearch|logstash|kibana" | grep "8.15.0" && echo "ELK images: READY"
```

## Quick Test

```bash
# Start ELK stack
cd elk_config
docker-compose up -d

# Wait for Elasticsearch
echo "Waiting for Elasticsearch (60 seconds)..."
sleep 60

# Test Elasticsearch
curl -s http://localhost:9200/_cluster/health | grep -q "green\|yellow" && echo "Elasticsearch: HEALTHY"

# Test Kibana
curl -s -I http://localhost:5601 | grep -q "200\|302" && echo "Kibana: ACCESSIBLE"

# Stop ELK
docker-compose down
```

## Pre-Flight Summary

Run this complete check:

```bash
#!/bin/bash

echo "=== Pre-Deployment Verification ==="
echo ""

# Docker
docker --version >/dev/null 2>&1 && echo "[✓] Docker installed" || echo "[✗] Docker NOT installed"

# Python
python3 --version >/dev/null 2>&1 && echo "[✓] Python3 available" || echo "[✗] Python3 NOT available"

# Memory
MEM=$(free -g | awk '/^Mem:/{print $2}')
if [ "$MEM" -ge 4 ]; then
    echo "[✓] Memory: ${MEM}GB (sufficient)"
else
    echo "[⚠] Memory: ${MEM}GB (may be insufficient)"
fi

# Disk
DISK=$(df -BG / | tail -1 | awk '{print $4}' | tr -d 'G')
if [ "$DISK" -ge 20 ]; then
    echo "[✓] Disk: ${DISK}GB free (sufficient)"
else
    echo "[⚠] Disk: ${DISK}GB free (may be insufficient)"
fi

# Log directory
if [ -d /var/log/multi_honeypot ] && [ -w /var/log/multi_honeypot ]; then
    echo "[✓] Log directory exists and writable"
else
    echo "[✗] Log directory missing or not writable"
fi

# Files
if [ -f requirements.txt ] && [ -f honeypot_modules/ssh_honeypot.py ]; then
    echo "[✓] Project files present"
else
    echo "[✗] Project files missing"
fi

# Ports
USED_PORTS=0
for port in 2222 8080 2121 9200 5601; do
    if sudo netstat -tulpn 2>/dev/null | grep -q ":$port "; then
        echo "[⚠] Port $port is in use"
        USED_PORTS=$((USED_PORTS + 1))
    fi
done
if [ $USED_PORTS -eq 0 ]; then
    echo "[✓] All required ports available"
fi

echo ""
echo "=== Verification Complete ==="
```

Save this as `verify.sh`, make executable with `chmod +x verify.sh`, and run `./verify.sh`.

## All Checks Passed?

If all checks pass, you're ready to deploy! Follow **[DEPLOYMENT.md](DEPLOYMENT.md)** for step-by-step instructions.

## Troubleshooting

### Docker not running
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Ports in use
```bash
# Kill process using port (example for port 2222)
sudo fuser -k 2222/tcp
```

### Insufficient memory
- Close other applications
- Reduce ELK memory in docker-compose.yml (not recommended)
- Use a machine with more RAM

### Python packages fail to install
```bash
# Update pip
pip install --upgrade pip

# Install system dependencies
sudo apt install -y python3-dev build-essential
```
